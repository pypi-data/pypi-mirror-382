from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import postgres_mcp.top_queries.top_queries_calc as top_queries_module
from postgres_mcp.sql import SqlDriver
from postgres_mcp.sql.extension_utils import ExtensionStatus
from postgres_mcp.top_queries import TopQueriesCalc


class MockSqlRowResult:
    def __init__(self, cells: Dict[str, Any]):
        self.cells = cells


# Fixtures for different PostgreSQL versions
@pytest.fixture
def mock_pg12_driver() -> Generator[MagicMock, None, None]:
    """Create a mock for SqlDriver that simulates PostgreSQL 12."""
    driver = MagicMock(spec=SqlDriver)

    # Set up the version mock directly on the mock driver
    with patch.object(top_queries_module, "get_postgres_version", autospec=True) as mock_version:
        mock_version.return_value = 12

        # Create async mock for execute_query
        mock_execute = AsyncMock()

        # Configure the mock to return different results based on the query
        async def side_effect(query: Any, *args: Any, **kwargs: Any) -> Optional[List[MockSqlRowResult]]:
            if "pg_stat_statements" in query:
                # Return data in PG 12 format with total_time and mean_time columns
                return [
                    MockSqlRowResult(cells={"query": "SELECT * FROM users", "calls": 100, "total_time": 1000.0, "mean_time": 10.0, "rows": 1000}),
                    MockSqlRowResult(cells={"query": "SELECT * FROM orders", "calls": 50, "total_time": 750.0, "mean_time": 15.0, "rows": 500}),
                    MockSqlRowResult(cells={"query": "SELECT * FROM products", "calls": 200, "total_time": 500.0, "mean_time": 2.5, "rows": 2000}),
                ]
            return None

        mock_execute.side_effect = side_effect
        driver.execute_query = mock_execute

        yield driver


@pytest.fixture
def mock_pg13_driver() -> Generator[MagicMock, None, None]:
    """Create a mock for SqlDriver that simulates PostgreSQL 13."""
    driver = MagicMock(spec=SqlDriver)

    # Set up the version mock directly on the mock driver
    with patch.object(top_queries_module, "get_postgres_version", autospec=True) as mock_version:
        mock_version.return_value = 13

        # Create async mock for execute_query
        mock_execute = AsyncMock()

        # Configure the mock to return different results based on the query
        async def side_effect(query: Any, *args: Any, **kwargs: Any) -> Optional[List[MockSqlRowResult]]:
            if "pg_stat_statements" in query:
                # Return data in PG 13+ format with total_exec_time and mean_exec_time columns
                return [
                    MockSqlRowResult(
                        cells={"query": "SELECT * FROM users", "calls": 100, "total_exec_time": 1000.0, "mean_exec_time": 10.0, "rows": 1000}
                    ),
                    MockSqlRowResult(
                        cells={"query": "SELECT * FROM orders", "calls": 50, "total_exec_time": 750.0, "mean_exec_time": 15.0, "rows": 500}
                    ),
                    MockSqlRowResult(
                        cells={"query": "SELECT * FROM products", "calls": 200, "total_exec_time": 500.0, "mean_exec_time": 2.5, "rows": 2000}
                    ),
                ]
            return None

        mock_execute.side_effect = side_effect
        driver.execute_query = mock_execute

        yield driver


# Patch check_extension to return different extension statuses
@pytest.fixture
def mock_extension_installed() -> Generator[MagicMock, None, None]:
    """Mock check_extension to report extension is installed."""
    with patch.object(top_queries_module, "check_extension", autospec=True) as mock_check:
        mock_check.return_value = ExtensionStatus(
            is_installed=True,
            is_available=True,
            name="pg_stat_statements",
            message="Extension is installed",
            default_version="1.0",
        )
        yield mock_check


@pytest.fixture
def mock_extension_not_installed() -> Generator[MagicMock, None, None]:
    """Mock check_extension to report extension is not installed."""
    with patch.object(top_queries_module, "check_extension", autospec=True) as mock_check:
        mock_check.return_value = ExtensionStatus(
            is_installed=False,
            is_available=True,
            name="pg_stat_statements",
            message="Extension not installed",
            default_version=None,
        )
        yield mock_check


@pytest.mark.asyncio
async def test_top_queries_pg12_total_sort(mock_pg12_driver: MagicMock, mock_extension_installed: MagicMock) -> None:
    """Test top queries calculation on PostgreSQL 12 sorted by total execution time."""
    # Create the TopQueriesCalc instance with the mock driver
    calc = TopQueriesCalc(sql_driver=mock_pg12_driver)  # type: ignore[arg-type]

    # Get top queries sorted by total time
    result = await calc.get_top_queries_by_time(limit=3, sort_by="total")

    # Check that the result contains the expected information
    assert "Top 3 slowest queries by total execution time" in result
    # First query should be the one with highest total_time
    assert "SELECT * FROM users" in result
    # Verify the query used the correct column name for PG 12
    assert "total_time" in str(mock_pg12_driver.execute_query.call_args)  # type: ignore[attr-defined]
    assert "ORDER BY total_time DESC" in str(mock_pg12_driver.execute_query.call_args)  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_top_queries_pg12_mean_sort(mock_pg12_driver: MagicMock, mock_extension_installed: MagicMock) -> None:
    """Test top queries calculation on PostgreSQL 12 sorted by mean execution time."""
    # Create the TopQueriesCalc instance with the mock driver
    calc = TopQueriesCalc(sql_driver=mock_pg12_driver)  # type: ignore[arg-type]

    # Get top queries sorted by mean time
    result = await calc.get_top_queries_by_time(limit=3, sort_by="mean")

    # Check that the result contains the expected information
    assert "Top 3 slowest queries by mean execution time per call" in result
    # First query should be the one with highest mean_time
    assert "SELECT * FROM orders" in result
    # Verify the query used the correct column name for PG 12
    assert "mean_time" in str(mock_pg12_driver.execute_query.call_args)  # type: ignore[attr-defined]
    assert "ORDER BY mean_time DESC" in str(mock_pg12_driver.execute_query.call_args)  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_top_queries_pg13_total_sort(mock_pg13_driver: MagicMock, mock_extension_installed: MagicMock) -> None:
    """Test top queries calculation on PostgreSQL 13 sorted by total execution time."""
    # Create the TopQueriesCalc instance with the mock driver
    calc = TopQueriesCalc(sql_driver=mock_pg13_driver)  # type: ignore[arg-type]

    # Get top queries sorted by total time
    result = await calc.get_top_queries_by_time(limit=3, sort_by="total")

    # Check that the result contains the expected information
    assert "Top 3 slowest queries by total execution time" in result
    # First query should be the one with highest total_exec_time
    assert "SELECT * FROM users" in result
    # Verify the query used the correct column name for PG 13+
    assert "total_exec_time" in str(mock_pg13_driver.execute_query.call_args)  # type: ignore[attr-defined]
    assert "ORDER BY total_exec_time DESC" in str(mock_pg13_driver.execute_query.call_args)  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_top_queries_pg13_mean_sort(mock_pg13_driver: MagicMock, mock_extension_installed: MagicMock) -> None:
    """Test top queries calculation on PostgreSQL 13 sorted by mean execution time."""
    # Create the TopQueriesCalc instance with the mock driver
    calc = TopQueriesCalc(sql_driver=mock_pg13_driver)  # type: ignore[arg-type]

    # Get top queries sorted by mean time
    result = await calc.get_top_queries_by_time(limit=3, sort_by="mean")

    # Check that the result contains the expected information
    assert "Top 3 slowest queries by mean execution time per call" in result
    # First query should be the one with highest mean_exec_time
    assert "SELECT * FROM orders" in result
    # Verify the query used the correct column name for PG 13+
    assert "mean_exec_time" in str(mock_pg13_driver.execute_query.call_args)  # type: ignore[attr-defined]
    assert "ORDER BY mean_exec_time DESC" in str(mock_pg13_driver.execute_query.call_args)  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_extension_not_installed(mock_pg13_driver: MagicMock, mock_extension_not_installed: MagicMock) -> None:
    """Test behavior when pg_stat_statements extension is not installed."""
    # Create the TopQueriesCalc instance with the mock driver
    calc = TopQueriesCalc(sql_driver=mock_pg13_driver)  # type: ignore[arg-type]

    # Try to get top queries when extension is not installed
    result = await calc.get_top_queries_by_time(limit=3)

    # Check that the result contains the installation instructions
    assert "extension is required to report" in result
    assert "CREATE EXTENSION" in result

    # Verify that execute_query was not called (since extension is not installed)
    mock_pg13_driver.execute_query.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_error_handling(mock_pg13_driver: MagicMock, mock_extension_installed: MagicMock) -> None:
    """Test error handling in the TopQueriesCalc class."""
    # Configure execute_query to raise an exception
    mock_pg13_driver.execute_query.side_effect = Exception("Database error")  # type: ignore[attr-defined]

    # Create the TopQueriesCalc instance with the mock driver
    calc = TopQueriesCalc(sql_driver=mock_pg13_driver)  # type: ignore[arg-type]

    # Try to get top queries
    result = await calc.get_top_queries_by_time(limit=3)

    # Check that the error is properly reported
    assert "Error getting slow queries: Database error" in result
