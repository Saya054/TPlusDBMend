"""Tests for SQL scanning state transitions; no live SQL Server required."""
import unittest
from unittest.mock import Mock
from core.sql_scan import scan_table, ScanStatus, quote_identifier


def factory(batches=None, execute_error=None, fetch_error=None):
    conn = Mock()
    cursor = Mock()
    conn.cursor.return_value = cursor
    cursor.description = [("id",)]
    if execute_error:
        cursor.execute.side_effect = execute_error
    if fetch_error:
        cursor.fetchmany.side_effect = fetch_error
    else:
        cursor.fetchmany.side_effect = list(batches or [[]])
    return lambda: conn, conn, cursor


class ScannerTests(unittest.TestCase):
    def test_streaming_until_eof(self):
        make, conn, cursor = factory([[1, 2], [3], []])
        result = scan_table(make, "db", "dbo", "t")
        self.assertEqual(result.status, ScanStatus.COMPLETED)
        self.assertEqual(result.rows_read, 3)
        self.assertEqual(cursor.fetchmany.call_count, 3)
        conn.close.assert_called_once()

    def test_timeout_is_not_corruption(self):
        make, _, _ = factory(fetch_error=Exception("HYT00", "Query timeout expired"))
        result = scan_table(make, "db", "dbo", "t")
        self.assertEqual(result.status, ScanStatus.QUERY_FAILED)
        self.assertFalse(result.confirmed_corruption)

    def test_explicit_corruption_code(self):
        err = Exception("HY000", "[SQL Server] I/O error (824) (SQLFetch)")
        make, _, _ = factory(fetch_error=err)
        result = scan_table(make, "db", "dbo", "t")
        self.assertEqual(result.status, ScanStatus.CORRUPTION_REPORTED)
        self.assertEqual(result.native_error, 824)

    def test_early_cancel(self):
        make, _, cursor = factory([[1], []])
        result = scan_table(make, "db", "dbo", "t", cancelled=lambda: True)
        self.assertEqual(result.status, ScanStatus.INTERRUPTED)
        cursor.fetchmany.assert_not_called()

    def test_identifier_escaping(self):
        self.assertEqual(quote_identifier("a]b"), "[a]]b]")


if __name__ == "__main__":
    unittest.main()
