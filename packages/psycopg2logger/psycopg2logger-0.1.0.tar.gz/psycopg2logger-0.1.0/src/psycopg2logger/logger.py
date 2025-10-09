from datetime import datetime, timezone
import time
import psycopg2
from psycopg2.extensions import connection as _connection, cursor as _cursor
import functools
import logging
from fastapimw.context import current_request_path, current_request_method
from tcp import socketsender
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class SQLLogRecord(BaseModel):
    timestamp: str
    statement: str
    duration: int
    endpoint: str
    http_method: Optional[str]
    caller_class: Optional[str]
    caller_method: Optional[str]
    caller_namespace: Optional[str]


log = logging.getLogger("sql_interceptor")
sender = socketsender.TCPLogSender("127.0.0.1", 6000)


class InterceptingCursor(_cursor):
    def execute(self, query, vars=None):
        start = time.perf_counter()
        try:
            return super().execute(query, vars)
        finally:
            duration = int((time.perf_counter() - start) * 1000)
            self.pass_log_message(query, vars, duration)

    def executemany(self, query, vars_list):
        start = time.perf_counter()
        try:
            return super().executemany(query, vars_list)
        finally:
            duration = int((time.perf_counter() - start) * 1000)
            self.pass_log_message(query, vars_list, duration)

    def pass_log_message(self, query: Any, vars: Any, duration: int):
        method = current_request_method.get()
        path = f"{current_request_path.get()} [{method}]"
        full_sql = str(query)
        try:
            full_sql = self.mogrify(query, vars).decode() if vars is not None else query
        except Exception as e:
            log.info(f"Failed to mogrify query {e}")
        log_entry = SQLLogRecord(
            timestamp=datetime.now(timezone.utc).strftime("%d%M%Y %H:%M:%S.%f"),
            statement=full_sql,
            duration=duration,
            endpoint=path,
            http_method=method,
            caller_class=None,
            caller_method=None,
            caller_namespace=None,
        )
        sender.send(log_entry.model_dump())


class InterceptingConnection(_connection):
    def cursor(self, *args, **kwargs):
        kwargs.setdefault("cursor_factory", InterceptingCursor)
        return super().cursor(*args, **kwargs)


# Patch psycopg2.connect globally
_psycopg2_connect = psycopg2.connect


@functools.wraps(_psycopg2_connect)
def connect_intercepting(*args, **kwargs):
    kwargs.setdefault("connection_factory", InterceptingConnection)
    return _psycopg2_connect(*args, **kwargs)


psycopg2.connect = connect_intercepting
