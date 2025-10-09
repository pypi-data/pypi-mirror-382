# pyright: reportPrivateUsage=false
import logging
import math
import sqlite3
import sys
import warnings
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Generic, TypeVar

import anyio
import anyio.from_thread
import anyio.lowlevel
import anyio.to_thread
from aioresult import TaskFailedException
from typing_extensions import ParamSpec

if sys.version_info < (3, 11):
    from exceptiongroup import BaseExceptionGroup

from ._exceptions import AnyIOSQLiteInternalError
from ._worker import Worker
from .cursor import Cursor

if sys.version_info >= (3, 11):
    from .blob import Blob

if TYPE_CHECKING:
    from collections.abc import (
        AsyncGenerator,
        AsyncIterator,
        Callable,
        Iterable,
        Mapping,
        Sequence,
    )
    from os import PathLike
    from types import TracebackType
    from typing import (
        Any,
        Literal,
        Optional,
        SupportsIndex,
        Union,
        cast,
    )

    from _typeshed import ReadableBuffer
    from anyio.abc import TaskGroup
    from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
    from typing_extensions import Self

    from ._types import (
        AggregateProtocol,
        IsolationLevel,
        SqliteData,
        WindowAggregateClass,
    )
    from .cursor import SyncCursorT

    _SyncConnectionT2 = TypeVar("_SyncConnectionT2", bound=sqlite3.Connection)
    _ArgsT = ParamSpec("_ArgsT")
    _ReturnT = TypeVar("_ReturnT")
    _T = TypeVar("_T")

_SyncConnectionT = TypeVar("_SyncConnectionT", bound=sqlite3.Connection)

MISSING: "Any" = object()
logger = logging.getLogger("anyio_sqlite")


class Connection(Generic[_SyncConnectionT]):
    """
    An asynchronous :class:`sqlite3.Connection` proxy.

    The object supports the asynchronous context management protocol. When leaving
    the body of the context manager, any open transactions is committed or rolled
    back before the connection is closed. If this commit fails, the transaction is
    rolled back.

    A :exc:`ResourceWarning` is emitted if the connection is not closed before it
    is deleted.
    """

    iter_chunk_size: int
    """
    The initial :attr:`Cursor.iter_chunk_size` for
    :class:`Cursor` objects created from this connection. Changing this
    attribute does not affect the :attr:`Cursor.iter_chunk_size` of existing
    cursors belonging to this connection, only new ones.
    """

    __slots__ = (
        "_closed",
        "_connection",
        "_connector",
        "_iterdump_recv",
        "_iterdump_send",
        "_tg",
        "_worker",
        "iter_chunk_size",
    )

    def __init__(
        self,
        task_group: "TaskGroup",
        connector: "Callable[[], _SyncConnectionT]",
        iter_chunk_size: int,
    ):
        self.iter_chunk_size = iter_chunk_size

        self._closed: bool = False

        self._connection: "Optional[_SyncConnectionT]" = None
        self._connector = connector

        self._tg = task_group
        self._worker = Worker()
        self._iterdump_send: "MemoryObjectSendStream[Optional[str]]" = MISSING
        self._iterdump_recv: "MemoryObjectReceiveStream[Optional[str]]" = MISSING

    if sys.version_info >= (3, 12):

        @classmethod
        async def connect(
            cls,
            task_group: "TaskGroup",
            database: "str | bytes | PathLike[str] | PathLike[bytes]",
            # this is the wait timeout for when the database is locked
            timeout: float = 5.0,  # noqa: ASYNC109
            detect_types: int = 0,
            isolation_level: "IsolationLevel | None" = "DEFERRED",
            factory: type["_SyncConnectionT2"] = sqlite3.Connection,
            cached_statements: int = 128,
            uri: bool = False,
            autocommit: bool = sqlite3.LEGACY_TRANSACTION_CONTROL,  # pyright: ignore[reportArgumentType]
            iter_chunk_size: int = 128,
        ) -> "Connection[_SyncConnectionT2]":
            """
            Opens an asynchronous SQLite connection.

            This method is used to specify a custom task group to run the worker thread
            in. The caller is responsible for closing the connection.

            If you don't need a custom task group, you should probably
            use :func:`connect` instead.

            Aside from `task_group`, other parameters have the same meaning as their
            `sqlite3` counterparts and are passed through to :func:`sqlite3.connect`.

            :param task_group: An AnyIO task group to run the worker thread in.
            :param int iter_chunk_size: The initial :attr:`Cursor.iter_chunk_size` for
                :class:`Cursor` objects created from this connection. Changing this
                attribute does not affect the :attr:`Cursor.iter_chunk_size` of existing
                cursors belonging to this connection, only new ones.
            """

            def connector():
                return sqlite3.connect(
                    database,
                    timeout=timeout,
                    detect_types=detect_types,
                    isolation_level=isolation_level,
                    factory=factory,
                    cached_statements=cached_statements,
                    uri=uri,
                    autocommit=autocommit,
                )

            conn = cls(task_group, connector, iter_chunk_size)  # pyright: ignore[reportArgumentType]

            await conn._actually_connect()
            return conn  # pyright: ignore[reportReturnType]

    else:

        @classmethod
        async def connect(
            cls,
            task_group: "TaskGroup",
            database: "Union[str, bytes, PathLike[str], PathLike[bytes]]",
            # this is the wait timeout for when the database is locked
            timeout: float = 5.0,  # noqa: ASYNC109
            detect_types: int = 0,
            isolation_level: "Optional[IsolationLevel]" = "DEFERRED",
            factory: type["_SyncConnectionT2"] = sqlite3.Connection,
            cached_statements: int = 128,
            uri: bool = False,
            iter_chunk_size: int = 128,
        ) -> "Connection[_SyncConnectionT2]":
            """
            Opens an asynchronous SQLite connection.

            This method is used to specify a custom task group to run the worker thread
            in. The caller is responsible for closing the connection.

            If you don't need a custom task group, you should probably use
            :func:`connect` instead.

            Aside from `task_group` and `iter_chunk_size`, other parameters have the
            same meaning as their `sqlite3` counterparts and are passed through to
            :func:`sqlite3.connect`.

            :param task_group: An AnyIO task group to run the worker thread in.
            :param int iter_chunk_size: The initial :attr:`Cursor.iter_chunk_size` for
                :class:`Cursor` objects created from this connection. Changing this
                attribute does not affect the :attr:`Cursor.iter_chunk_size` of existing
                cursors belonging to this connection, only new ones.
            """

            def connector():
                return sqlite3.connect(
                    database,
                    timeout=timeout,
                    detect_types=detect_types,
                    isolation_level=isolation_level,
                    factory=factory,
                    cached_statements=cached_statements,
                    uri=uri,
                )

            conn = cls(task_group, connector, iter_chunk_size)  # pyright: ignore[reportArgumentType]

            await conn._actually_connect()
            return conn  # pyright: ignore[reportReturnType]

    @property
    def connection(self) -> _SyncConnectionT:
        """
        Returns the underlying SQLite connection. Raises sqlite3.ProgrammingError
        if there are none.
        """

        if self._connection is None:
            msg = "no active connections"
            raise sqlite3.ProgrammingError(msg)

        return self._connection

    # Lifecycle management

    async def __aenter__(self) -> "Self":
        if self._closed:
            msg = "Cannot operate on a closed database."
            raise sqlite3.ProgrammingError(msg)

        if self._connection is None:
            await self._actually_connect()

        return self

    async def __aexit__(
        self,
        exc_type: "Optional[type[BaseException]]",
        exc_value: "Optional[BaseException]",
        traceback: "Optional[TracebackType]",
    ):
        if exc_type is None and exc_value is None and traceback is None:
            try:
                await self.commit()
            except Exception as e:
                # commit failed, try to rollback in order to unlock the database
                try:
                    await self.rollback()
                except Exception as e2:
                    # rollback also failed, chain the exceptions
                    raise e2 from e

                # rollback succeeded, raise commit error
                raise
        else:
            try:
                await self.rollback()
            except Exception as e:  # noqa: BLE001
                logger.warning("error ignored in rollback on %r", self, exc_info=e)

        await self.aclose()

    async def _actually_connect(self):
        if self._connection is not None:
            return self

        self._tg.start_soon(anyio.to_thread.run_sync, self._worker.run)

        try:
            self._connection = await self._to_thread(self._connector)
        except BaseException:
            await self._stop_running()
            raise

        return self

    async def _stop_running(self):
        self._worker.stop()
        self._connection = None

        if self._iterdump_send is not MISSING:
            await self._iterdump_send.aclose()

        if self._iterdump_recv is not MISSING:
            await self._iterdump_recv.aclose()

        self._closed = True

    async def aclose(self):
        """Closes the connection."""

        if self._connection is None or self._closed:
            return

        await self._to_thread(self._connection.close)
        await self._stop_running()

    async def _to_thread(
        self,
        func: "Callable[_ArgsT, _ReturnT]",
        *args: "_ArgsT.args",
        **kwargs: "_ArgsT.kwargs",
    ) -> "_ReturnT":
        await anyio.lowlevel.checkpoint_if_cancelled()

        if self._closed:
            msg = "Cannot operate on a closed database."
            raise sqlite3.ProgrammingError(msg)

        future = self._worker.post(func, *args, **kwargs)

        await future.wait_done()

        try:
            return future.result()
        except TaskFailedException:
            inner = future.exception()
            # if TaskFailedException is raised, then the exception is not None,
            # but pyright can't know that.
            raise inner from None  # pyright: ignore[reportGeneralTypeIssues]

    async def cursor(
        self,
        factory: "Callable[[_SyncConnectionT], SyncCursorT]" = sqlite3.Cursor,
    ) -> Cursor[_SyncConnectionT, "SyncCursorT"]:
        """
        Create and return a :class:`Cursor` asynchronous proxy.

        :param factory: The underlying :mod:`sqlite3` cursor class.
        """
        # this really should be (_SyncConnectionT) -> SyncCursorT because you
        # can override the connection factory, but pyright seems really unhappy
        # if I don't cast this.
        if TYPE_CHECKING:
            factory = cast("Callable[[sqlite3.Connection], SyncCursorT]", factory)

        sync_cursor = await self._to_thread(self.connection.cursor, factory)

        return Cursor(self, sync_cursor)

    if sys.version_info >= (3, 11):

        async def blobopen(
            self,
            table: str,
            column: str,
            row: int,
            /,
            *,
            readonly: bool = False,
            name: str = "main",
        ):
            """
            Open a :class:`Blob` asynchronous proxy to an SQLite BLOB.

            Parameters are inherited from :meth:`sqlite3.Connection.blobopen`.
            """
            sync_blob = await self._to_thread(
                self.connection.blobopen,
                table,
                column,
                row,
                readonly=readonly,
                name=name,
            )

            return Blob(self, sync_blob)

    async def commit(self):
        await self._to_thread(self.connection.commit)

    async def rollback(self):
        await self._to_thread(self.connection.rollback)

    async def execute(
        self, sql: str, parameters: "Union[Sequence[Any], Mapping[str, Any]]" = (), /
    ) -> Cursor[_SyncConnectionT, sqlite3.Cursor]:
        sync_cursor = await self._to_thread(self.connection.execute, sql, parameters)

        return Cursor(self, sync_cursor)

    async def executemany(
        self,
        sql: str,
        parameters: "Iterable[Union[Sequence[Any], Mapping[str, Any]]]",
        /,
    ) -> Cursor[_SyncConnectionT, sqlite3.Cursor]:
        sync_cursor = await self._to_thread(
            self.connection.executemany, sql, parameters
        )

        return Cursor(self, sync_cursor)

    async def executescript(
        self, sql_script: str, /
    ) -> Cursor[_SyncConnectionT, sqlite3.Cursor]:
        sync_cursor = await self._to_thread(self.connection.executescript, sql_script)

        return Cursor(self, sync_cursor)

    async def create_function(
        self,
        name: str,
        narg: int,
        func: "Optional[Callable[..., SqliteData]]",
        *,
        deterministic: bool = False,
    ) -> None:
        return await self._to_thread(
            self.connection.create_function,
            name,
            narg,
            func,
            deterministic=deterministic,
        )

    async def create_aggregate(
        self, name: str, n_arg: int, aggregate_class: "Callable[[], AggregateProtocol]"
    ) -> None:
        return await self._to_thread(
            self.connection.create_aggregate,
            name,
            n_arg,
            aggregate_class,
        )

    if sys.version_info >= (3, 11):

        async def create_window_function(
            self,
            name: str,
            num_params: int,
            aggregate_class: "Callable[[], WindowAggregateClass] | None",
            /,
        ) -> None:
            return await self._to_thread(
                self.connection.create_window_function,
                name,
                num_params,
                aggregate_class,
            )

    async def create_collation(
        self,
        name: str,
        callable: "Optional[Callable[[str, str], Union[int, SupportsIndex]]]",
        /,
    ) -> None:
        return await self._to_thread(
            self.connection.create_collation,
            name,
            callable,
        )

    def interrupt(self):
        self.connection.interrupt()

    async def set_authorizer(
        self,
        authorizer_callback: "Optional[Callable[[int, Optional[str], Optional[str], Optional[str], Optional[str]], int]]",  # noqa: E501
    ) -> None:
        return await self._to_thread(
            self.connection.set_authorizer,
            authorizer_callback,
        )

    async def set_progress_handler(
        self, progress_handler: "Optional[Callable[[], Optional[int]]]", n: int
    ) -> None:
        return await self._to_thread(
            self.connection.set_progress_handler,
            progress_handler,
            n,
        )

    async def set_trace_callback(
        self, trace_callback: "Optional[Callable[[str], object]]"
    ) -> None:
        return await self._to_thread(
            self.connection.set_trace_callback,
            trace_callback,
        )

    async def enable_load_extension(self, enabled: bool, /) -> None:
        return await self._to_thread(
            self.connection.enable_load_extension,
            enabled,
        )

    if sys.version_info >= (3, 12):

        async def load_extension(
            self, path: str, /, *, entrypoint: str | None = None
        ) -> None:
            return await self._to_thread(
                self.connection.load_extension,
                path,
                entrypoint=entrypoint,
            )

    else:

        async def load_extension(self, path: str, /) -> None:
            return await self._to_thread(
                self.connection.load_extension,
                path,
            )

    if sys.version_info >= (3, 13):

        def _iterdumper(self, token: anyio.lowlevel.EventLoopToken, filter: str | None):
            try:
                for line in self.connection.iterdump(filter=filter):
                    anyio.from_thread.run_sync(
                        self._iterdump_send.send_nowait, line, token=token
                    )
            finally:
                anyio.from_thread.run_sync(
                    self._iterdump_send.send_nowait, None, token=token
                )

        async def iterdump(self, *, filter: str | None = None) -> "AsyncIterator[str]":
            if self._iterdump_send is MISSING or self._iterdump_recv is MISSING:
                self._iterdump_send, self._iterdump_recv = (
                    anyio.create_memory_object_stream["Optional[str]"](math.inf)
                )

            self._tg.start_soon(
                lambda: self._to_thread(
                    self._iterdumper, anyio.lowlevel.current_token(), filter
                )
            )

            async for line in self._iterdump_recv:
                if line is None:
                    break

                yield line
    else:

        def _iterdumper(self, token: anyio.lowlevel.EventLoopToken):
            try:
                for line in self.connection.iterdump():
                    anyio.from_thread.run_sync(
                        self._iterdump_send.send_nowait, line, token=token
                    )
            finally:
                anyio.from_thread.run_sync(
                    self._iterdump_send.send_nowait, None, token=token
                )

        async def iterdump(self) -> "AsyncIterator[str]":
            if self._iterdump_send is MISSING or self._iterdump_recv is MISSING:
                self._iterdump_send, self._iterdump_recv = (
                    anyio.create_memory_object_stream["Optional[str]"](math.inf)
                )

            self._tg.start_soon(
                lambda: self._to_thread(
                    self._iterdumper, anyio.lowlevel.current_token()
                )
            )

            async for line in self._iterdump_recv:
                if line is None:
                    break

                yield line

    async def backup(
        self,
        target: "Union[Connection[_SyncConnectionT], sqlite3.Connection]",
        *,
        pages: int = -1,
        progress: "Optional[Callable[[int, int, int], Any]]" = None,
        name: str = "main",
        sleep: float = 0.250,
    ) -> None:
        if isinstance(target, Connection):
            target = target.connection

        return await self._to_thread(
            self.connection.backup,
            target,
            pages=pages,
            progress=progress,
            name=name,
            sleep=sleep,
        )

    if sys.version_info >= (3, 11):

        async def getlimit(self, category: int, /) -> int:
            return await self._to_thread(self.connection.getlimit, category)

        async def setlimit(self, category: int, limit: int, /) -> int:
            return await self._to_thread(self.connection.setlimit, category, limit)

        async def serialize(self, *, name: str = "main") -> bytes:
            return await self._to_thread(self.connection.serialize, name=name)

        async def deserialize(
            self, data: "ReadableBuffer", /, *, name: str = "main"
        ) -> None:
            return await self._to_thread(self.connection.deserialize, data, name=name)

    if sys.version_info >= (3, 12):

        async def getconfig(self, op: int, /) -> bool:
            return await self._to_thread(self.connection.getconfig, op)

        async def setconfig(self, op: int, enable: bool = True, /) -> bool:
            return await self._to_thread(self.connection.setconfig, op, enable)

        async def autocommit(self) -> int:
            return await self._to_thread(getattr, self.connection, "autocommit")

        async def set_autocommit(self, val: int, /) -> None:
            def inner(connection: sqlite3.Connection, val: int):
                connection.autocommit = val

            return await self._to_thread(inner, self.connection, val)

    @property
    def in_transaction(self) -> bool:
        return self.connection.in_transaction

    @property
    def isolation_level(self) -> "Optional[Union[IsolationLevel, Literal['']]]":
        return self.connection.isolation_level

    @isolation_level.setter
    def isolation_level(self, val: "Optional[IsolationLevel]") -> None:
        self.connection.isolation_level = val

    @property
    def row_factory(
        self,
    ) -> "Optional[Callable[[sqlite3.Cursor, sqlite3.Row], object]]":
        return self.connection.row_factory

    @row_factory.setter
    def row_factory(
        self, value: "Optional[Callable[[sqlite3.Cursor, sqlite3.Row], object]]"
    ):
        self.connection.row_factory = value

    @property
    def text_factory(self) -> "Union[Callable[[bytes], str], str, bytes, bytearray]":
        return self.connection.text_factory

    @text_factory.setter
    def text_factory(
        self, value: "Union[Callable[[bytes], str], str, bytes, bytearray]"
    ):
        self.connection.text_factory = value

    @property
    def total_changes(self):
        return self.connection.total_changes

    def __del__(self):
        if self._connection is None or self._closed:
            return

        warnings.warn(
            (
                f"{self!r} was deleted before being closed. "
                "Please use 'async with' or '.aclose()' to close the connection "
                "properly."
            ),
            ResourceWarning,
            stacklevel=1,
        )

        # attempt to stop the worker thread, unfortunately the memory object streams
        # will be left dangling
        self._worker.stop()


if sys.version_info >= (3, 12):

    @asynccontextmanager
    async def connect(
        database: "str | bytes | PathLike[str] | PathLike[bytes]",
        # this is the wait timeout for when the database is locked
        timeout: float = 5.0,  # noqa: ASYNC109
        detect_types: int = 0,
        isolation_level: "IsolationLevel | None" = "DEFERRED",
        factory: type[_SyncConnectionT] = sqlite3.Connection,
        cached_statements: int = 128,
        uri: bool = False,
        autocommit: bool = sqlite3.LEGACY_TRANSACTION_CONTROL,  # pyright: ignore[reportArgumentType]
        iter_chunk_size: int = 128,
    ) -> "AsyncGenerator[Connection[_SyncConnectionT], Any]":
        """
        Opens an asynchronous SQLite connection.

        This async context manager connects to the database when entering the context
        manager and closes the connection when exiting. It yields a :class:`Connection`
        instance.

        Aside from `iter_chunk_size`, parameters have the same meaning as their
        :mod:`sqlite3` counterparts and are passed through to :func:`sqlite3.connect`.

        :param int iter_chunk_size: The initial :attr:`Cursor.iter_chunk_size` for
            :class:`Cursor` objects created from this connection. Changing this
            attribute does not affect the :attr:`Cursor.iter_chunk_size` of existing
            cursors belonging to this connection, only new ones.
        """

        try:
            async with (
                anyio.create_task_group() as tg,
                await Connection.connect(
                    tg,
                    database,
                    timeout,
                    detect_types,
                    isolation_level,
                    factory,
                    cached_statements,
                    uri,
                    autocommit,
                    iter_chunk_size,
                ) as conn,
            ):
                yield conn
        except BaseExceptionGroup as excgroup:
            if len(excgroup.exceptions) == 1:
                raise excgroup.exceptions[0] from None

            msg = (
                "anyio-sqlite is not expected to raise multiple exceptions. "
                "Please report this as a bug to https://github.com/beer-psi/anyio-sqlite"
            )
            raise AnyIOSQLiteInternalError(msg) from excgroup
else:

    @asynccontextmanager
    async def connect(
        database: "Union[str, bytes, PathLike[str], PathLike[bytes]]",
        # this is the wait timeout for when the database is locked
        timeout: float = 5.0,  # noqa: ASYNC109
        detect_types: int = 0,
        isolation_level: "Optional[IsolationLevel]" = "DEFERRED",
        factory: type[_SyncConnectionT] = sqlite3.Connection,
        cached_statements: int = 128,
        uri: bool = False,
        iter_chunk_size: int = 128,
    ) -> "AsyncGenerator[Connection[_SyncConnectionT], Any]":
        """
        Opens an asynchronous SQLite connection.

        This async context manager connects to the database when entering the context
        manager and closes the connection when exiting. It yields a :class:`Connection`
        instance.

        Aside from `iter_chunk_size`, parameters have the same meaning as their
        :mod:`sqlite3` counterparts and are passed through to :func:`sqlite3.connect`.

        :param int iter_chunk_size: The initial :attr:`Cursor.iter_chunk_size` for
            :class:`Cursor` objects created from this connection. Changing this
            attribute does not affect the :attr:`Cursor.iter_chunk_size` of existing
            cursors belonging to this connection, only new ones.
        """

        try:
            async with (
                anyio.create_task_group() as tg,
                await Connection.connect(
                    tg,
                    database,
                    timeout,
                    detect_types,
                    isolation_level,
                    factory,
                    cached_statements,
                    uri,
                    iter_chunk_size,
                ) as conn,
            ):
                yield conn
        except BaseExceptionGroup as excgroup:
            if len(excgroup.exceptions) == 1:
                raise excgroup.exceptions[0] from None

            msg = (
                "anyio-sqlite is not expected to raise multiple exceptions. "
                "Please report this as a bug to https://github.com/beer-psi/anyio-sqlite"
            )
            raise AnyIOSQLiteInternalError(msg) from excgroup
