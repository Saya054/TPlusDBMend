"""Read-only SQL Server table scanner.

A completed scan means the result stream reached EOF. It does not prove
DBCC integrity or ERP-level consistency. Transport and query errors are never
silently classified as corruption.
"""
from dataclasses import dataclass
from enum import Enum
from time import monotonic
from typing import Callable, Optional
import re


class ScanStatus(str, Enum):
    COMPLETED = "completed"
    CORRUPTION_REPORTED = "corruption_reported"
    QUERY_FAILED = "query_failed"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True)
class ScanResult:
    status: ScanStatus
    rows_read: int
    elapsed_seconds: float
    sqlstate: Optional[str] = None
    native_error: Optional[int] = None
    message: str = ""

    @property
    def confirmed_corruption(self) -> bool:
        return self.status == ScanStatus.CORRUPTION_REPORTED


# These codes indicate a reported page/checksum or allocation consistency
# problem. Other errors are not assumed to be corruption.
CORRUPTION_CODES = {823, 824, 825, 8905, 8906, 8908, 8928, 8939, 8944}
NATIVE_CODE_RE = re.compile(r"\\((\\d{3,5})\\)\\s*\\(SQLExecDirectW|SQLFetch|SQLGetData|SQLMoreResults|SQLPrepare|SQLExecute\\)", re.I)


def quote_identifier(identifier: str) -> str:
    if not identifier or "\\x00" in identifier:
        raise ValueError("Invalid SQL identifier")
    return "[" + identifier.replace("]", "]]") + "]"


def extract_error(exc: Exception):
    args = getattr(exc, "args", ())
    sqlstate = args[0] if args and isinstance(args[0], str) and re.fullmatch(r"[A-Z0-9]{5}", args[0]) else None
    message = " ".join(str(a) for a in args) if args else str(exc)
    # ODBC messages often contain a native code before the function name.
    match = NATIVE_CODE_RE.search(message)
    native = int(match.group(1)) if match else None
    return sqlstate, native, message


def scan_table(connection_factory: Callable, database: str, schema: str,
               table: str, batch_size: int = 512,
               timeout_seconds: int = 300,
               cancelled: Optional[Callable[[], bool]] = None,
               on_progress: Optional[Callable[[int], None]] = None) -> ScanResult:
    """Scan every returned row using a dedicated, read-only connection.

    connection_factory must create a fresh DB-API connection with the requested
    database selected; this routine never changes transaction settings.
    The query timeout is per driver operation, not a guaranteed total deadline.
    A caller should enforce a process-level deadline if necessary.
    """
    if batch_size <= 0 or timeout_seconds < 0:
        raise ValueError("Invalid scan options")
    start = monotonic()
    rows_read = 0
    conn = cursor = None
    try:
        conn = connection_factory()
        cursor = conn.cursor()
        if hasattr(cursor, "timeout"):
            cursor.timeout = timeout_seconds
        # The selected database must be checked by the caller; no USE or writes.
        sql = "SELECT * FROM " + quote_identifier(schema) + "." + quote_identifier(table)
        cursor.execute(sql)
        if cursor.description is None:
            return ScanResult(ScanStatus.QUERY_FAILED, 0, monotonic()-start,
                              message="SELECT did not return a result set")
        while True:
            if cancelled is not None and cancelled():
                return ScanResult(ScanStatus.INTERRUPTED, rows_read,
                                  monotonic()-start, message="Cancelled by caller")
            batch = cursor.fetchmany(batch_size)
            if not batch:
                return ScanResult(ScanStatus.COMPLETED, rows_read,
                                  monotonic()-start)
            rows_read += len(batch)
            if on_progress is not None:
                on_progress(rows_read)
    except Exception as exc:
        state, native, message = extract_error(exc)
        status = (ScanStatus.CORRUPTION_REPORTED if native in CORRUPTION_CODES
                  else ScanStatus.QUERY_FAILED)
        return ScanResult(status, rows_read, monotonic()-start,
                          sqlstate=state, native_error=native, message=message)
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
