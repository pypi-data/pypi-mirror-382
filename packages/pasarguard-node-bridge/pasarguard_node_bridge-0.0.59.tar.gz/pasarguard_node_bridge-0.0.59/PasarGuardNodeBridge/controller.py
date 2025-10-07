import ssl
import asyncio
import weakref
import logging
from enum import IntEnum
from uuid import UUID
from typing import Optional

from aiorwlock import RWLock

from PasarGuardNodeBridge.common.service_pb2 import User


class RollingQueue(asyncio.Queue):
    def __init__(self, maxsize=0):
        super().__init__(maxsize)
        self._closed = False

    async def put(self, item):
        if self._closed:
            return
        while self.maxsize > 0 and self.full():
            try:
                await asyncio.wait_for(self.get(), timeout=0.1)
            except asyncio.TimeoutError:
                break
        try:
            await super().put(item)
        except asyncio.QueueFull:
            pass

    async def close(self):
        """Close the queue and prevent further operations"""
        self._closed = True
        while not self.empty():
            try:
                self.get_nowait()
            except asyncio.QueueEmpty:
                break


class UserQueue(asyncio.Queue):
    """Queue that tracks pending user emails to avoid duplicate entries"""

    def __init__(self, maxsize=0):
        super().__init__(maxsize)
        self._email_count: dict[str, int] = {}  # Track count of each email in queue
        self._closed = False

    async def close(self):
        """Close the queue and prevent further operations"""
        self._closed = True
        while not self.empty():
            try:
                self.get_nowait()
            except asyncio.QueueEmpty:
                break

    async def put(self, item):
        """Add user to queue and track their email"""
        if self._closed:
            return
        if item and hasattr(item, "email"):
            self._email_count[item.email] = self._email_count.get(item.email, 0) + 1
        await super().put(item)

    def put_nowait(self, item):
        """Add user to queue without waiting and track their email"""
        if self._closed:
            return
        if item and hasattr(item, "email"):
            self._email_count[item.email] = self._email_count.get(item.email, 0) + 1
        super().put_nowait(item)

    def _update_email_count(self, item):
        """Update email count when removing a user from queue"""
        if item and hasattr(item, "email"):
            if item.email in self._email_count:
                self._email_count[item.email] -= 1
                if self._email_count[item.email] <= 0:
                    del self._email_count[item.email]

    async def get(self):
        """Remove and return user from queue, updating email count"""
        if self._closed:
            return
        item = await super().get()
        self._update_email_count(item)
        return item

    def get_nowait(self):
        """Remove and return user from queue without waiting, updating email count"""
        if self._closed:
            return
        item = super().get_nowait()
        self._update_email_count(item)
        return item

    def has_email(self, email: str) -> bool:
        """Check if a user with this email is already queued"""
        return email in self._email_count and self._email_count[email] > 0


class NodeAPIError(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail

    def __str__(self):
        return f"NodeAPIError(code={self.code}, detail={self.detail})"


class Health(IntEnum):
    NOT_CONNECTED = 0
    BROKEN = 1
    HEALTHY = 2
    INVALID = 3


class Controller:
    def __init__(
        self,
        server_ca: str,
        api_key: str,
        name: str = "default",
        extra: dict | None = None,
        max_logs: int = 1000,
        logger: logging.Logger | None = None,
    ):
        self.max_logs = max_logs
        self.name = name
        if extra is None:
            extra = {}
        if logger is None:
            logger = logging.getLogger(self.name)
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            logger.addHandler(handler)
        self.logger = logger
        try:
            self.api_key = UUID(api_key)

            self.ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            self.ctx.set_alpn_protocols(["h2"])
            self.ctx.load_verify_locations(cadata=server_ca)
            self.ctx.check_hostname = True

        except ssl.SSLError as e:
            raise NodeAPIError(-1, f"SSL initialization failed: {str(e)}")

        except (ValueError, TypeError) as e:
            raise NodeAPIError(-2, f"Invalid API key format: {str(e)}")

        self._health = Health.NOT_CONNECTED
        self._user_queue: Optional[UserQueue] = UserQueue(maxsize=10000)
        self._notify_queue: Optional[asyncio.Queue] = asyncio.Queue(maxsize=10)
        self._logs_queue: Optional[RollingQueue] = RollingQueue(self.max_logs)
        self._tasks: list[asyncio.Task] = []
        self._node_version = ""
        self._core_version = ""
        self._extra = extra
        self._lock = RWLock()
        self._shutdown_event = asyncio.Event()

    async def set_health(self, health: Health):
        async with self._lock.writer_lock:
            if self._health is Health.INVALID:
                return
            if health == Health.BROKEN and self._health != Health.BROKEN:
                if self._notify_queue:
                    await self._notify_queue.put(None)
            self._health = health

    async def get_health(self) -> Health:
        async with self._lock.reader_lock:
            return self._health

    async def update_user(self, user: User):
        async with self._lock.reader_lock:
            if self._user_queue:
                await self._user_queue.put(user)

    async def update_users(self, users: list[User]):
        async with self._lock.reader_lock:
            if not self._user_queue or not users:
                return
            for user in users:
                await self._user_queue.put(user)

    async def requeue_user_with_deduplication(self, user: User):
        """
        Requeue a user only if there's no existing version in the queue.
        Uses the UserQueue's email tracking to prevent duplicate entries.
        """
        async with self._lock.reader_lock:
            if not self._user_queue:
                return

            # Only requeue if user is not already in queue
            if not self._user_queue.has_email(user.email):
                try:
                    await self._user_queue.put(user)
                except asyncio.QueueFull:
                    pass

    async def flush_user_queue(self):
        async with self._lock.writer_lock:
            if self._user_queue:
                await self._user_queue.close()
                self._user_queue = UserQueue(10000)

    async def get_logs(self) -> asyncio.Queue | None:
        async with self._lock.reader_lock:
            return self._logs_queue

    async def flush_logs_queue(self):
        async with self._lock.writer_lock:
            if self._logs_queue:
                await self._logs_queue.close()
                self._logs_queue = RollingQueue(self.max_logs)

    async def node_version(self) -> str:
        async with self._lock.reader_lock:
            return self._node_version

    async def core_version(self) -> str:
        async with self._lock.reader_lock:
            return self._core_version

    async def get_extra(self) -> dict:
        async with self._lock.reader_lock:
            return self._extra

    async def connect(self, node_version: str, core_version: str, tasks: list | None = None):
        if tasks is None:
            tasks = []
        async with self._lock.writer_lock:
            self._shutdown_event.clear()
            await self._cleanup_tasks()
            self._health = Health.HEALTHY
            self._node_version = node_version
            self._core_version = core_version

            for t in tasks:
                task = asyncio.create_task(t())
                self._tasks.append(task)

    async def disconnect(self):
        await self.set_health(Health.NOT_CONNECTED)

        async with self._lock.writer_lock:
            self._shutdown_event.set()
            await self._cleanup_tasks()
            await self._cleanup_queues()

            self._node_version = ""
            self._core_version = ""

    async def _cleanup_tasks(self):
        """Clean up all background tasks properly - must be called with writer_lock held"""
        if self._tasks:
            for task in self._tasks:
                if not task.done():
                    task.cancel()

            try:
                await asyncio.wait_for(asyncio.gather(*self._tasks, return_exceptions=True), timeout=5.0)
            except asyncio.TimeoutError:
                pass

            self._tasks.clear()

    async def _cleanup_queues(self):
        """Properly clean up all queues - must be called with writer_lock held"""
        if self._user_queue:
            try:
                await asyncio.wait_for(self._user_queue.put(None), timeout=0.1)
            except (asyncio.TimeoutError, asyncio.QueueFull):
                pass

            while not self._user_queue.empty():
                try:
                    self._user_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

            self._user_queue = UserQueue(maxsize=10000)

        if self._notify_queue:
            try:
                await asyncio.wait_for(self._notify_queue.put(None), timeout=0.1)
            except (asyncio.TimeoutError, asyncio.QueueFull):
                pass

            while not self._notify_queue.empty():
                try:
                    self._notify_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

            self._notify_queue = asyncio.Queue(maxsize=10)

        if self._logs_queue:
            await self._logs_queue.close()
            self._logs_queue = RollingQueue(self.max_logs)

    def is_shutting_down(self) -> bool:
        """Check if the node is shutting down"""
        return self._shutdown_event.is_set()
