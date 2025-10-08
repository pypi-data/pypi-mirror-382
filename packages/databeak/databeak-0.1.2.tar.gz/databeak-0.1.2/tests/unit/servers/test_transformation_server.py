"""Unit tests for transformation server module.

Tests the server wrapper layer, Pydantic model conversion, and FastMCP integration for core data
transformation operations.
"""

import pytest
from fastmcp import Context
from fastmcp.exceptions import ToolError

# Ensure full module coverage
from databeak.exceptions import ColumnNotFoundError, NoDataLoadedError
from databeak.models import FilterCondition
from databeak.servers.io_server import load_csv_from_content
from databeak.servers.transformation_server import (
    SortColumn,
    fill_missing_values,
    filter_rows,
    remove_duplicates,
    sort_data,
)
from tests.test_mock_context import create_mock_context


@pytest.fixture
async def transformation_ctx() -> Context:
    """Create a test session with transformation data."""
    csv_content = """name,age,score,status,notes
John Doe,30,85.5,active,Good performance
Jane Smith,25,92.0,active,
Bob Johnson,35,78.5,inactive,Needs improvement
Alice Brown,28,95.0,active,Excellent
Charlie Wilson,30,85.5,pending,"""

    ctx = create_mock_context()
    await load_csv_from_content(ctx, csv_content)
    return ctx


@pytest.mark.asyncio
class TestTransformationServerFilterRows:
    """Test filter_rows server function."""

    async def test_filter_with_pydantic_models(self, transformation_ctx: Context) -> None:
        """Test filtering using Pydantic FilterCondition models."""
        conditions = [
            FilterCondition(column="age", operator=">", value=27),
            FilterCondition(column="status", operator="=", value="active"),
        ]

        ctx = transformation_ctx
        result = filter_rows(ctx, conditions, mode="and")
        assert result.success is True
        assert result.rows_before == 5
        assert result.rows_after == 2  # John (30, active) and Alice (28 > 27, active)

    async def test_filter_with_mixed_formats(self, transformation_ctx: Context) -> None:
        """Test filtering with mixed Pydantic models and dict formats."""
        conditions = [
            FilterCondition(column="age", operator=">=", value=30),
            {"column": "status", "operator": "!=", "value": "inactive"},
        ]

        ctx = transformation_ctx
        # Test validates dict-to-FilterCondition conversion (Pydantic handles this)
        result = filter_rows(ctx, conditions, mode="and")  # type: ignore[arg-type]
        assert result.success is True
        assert result.rows_after == 2  # John and Charlie

    async def test_filter_null_operators(self, transformation_ctx: Context) -> None:
        """Test null operators with Pydantic models."""
        conditions = [FilterCondition(column="notes", operator="is_null")]

        ctx = transformation_ctx
        result = filter_rows(ctx, conditions)
        assert result.success is True
        assert result.rows_after == 2  # Jane and Charlie have empty notes

    async def test_filter_text_operators(self, transformation_ctx: Context) -> None:
        """Test text operators with Pydantic models."""
        conditions = [FilterCondition(column="name", operator="contains", value="o")]

        ctx = transformation_ctx
        result = filter_rows(ctx, conditions)
        assert result.success is True
        assert result.rows_after == 4  # John Doe, Bob Johnson, Alice Brown, Charlie Wilson

    async def test_filter_or_mode(self, transformation_ctx: Context) -> None:
        """Test OR mode with multiple conditions."""
        conditions = [
            FilterCondition(column="age", operator="<", value=28),
            FilterCondition(column="score", operator=">", value=94),
        ]

        ctx = transformation_ctx
        result = filter_rows(ctx, conditions, mode="or")
        assert result.success is True
        assert result.rows_after == 2  # Jane (age < 28) and Alice (score > 94)


@pytest.mark.asyncio
class TestTransformationServerSort:
    """Test sort_data server function."""

    async def test_sort_with_pydantic_models(self, transformation_ctx: Context) -> None:
        """Test sorting using Pydantic SortColumn models."""
        columns: list[str | SortColumn] = [
            SortColumn(column="age", ascending=False),
            SortColumn(column="score", ascending=True),
        ]

        ctx = transformation_ctx
        result = sort_data(ctx, columns)
        assert result.sorted_by == ["age", "score"]
        assert len(result.ascending) == 2

    async def test_sort_with_mixed_formats(self, transformation_ctx: Context) -> None:
        """Test sorting with mixed formats."""
        columns = [
            SortColumn(column="status", ascending=True),
            {"column": "score", "ascending": False},
            "name",  # Simple string format
        ]

        ctx = transformation_ctx
        # Test validates dict/string-to-SortSpec conversion (Pydantic handles this)
        result = sort_data(ctx, columns)  # type: ignore[arg-type]
        assert result.success is True

    async def test_sort_string_columns(self, transformation_ctx: Context) -> None:
        """Test sorting simple string columns."""
        ctx = transformation_ctx
        result = sort_data(ctx, ["name", "status"])
        assert result.success is True


@pytest.mark.asyncio
class TestTransformationServerDuplicates:
    """Test remove_duplicates server function."""

    async def test_remove_duplicates_all_columns(self, transformation_ctx: Context) -> None:
        """Test removing exact duplicates."""
        # First add a duplicate row
        from databeak.servers.row_operations_server import insert_row

        ctx_insert = transformation_ctx
        insert_row(
            ctx_insert,
            row_index=-1,
            data={
                "name": "John Doe",
                "age": 30,
                "score": 85.5,
                "status": "active",
                "notes": "Good performance",
            },
        )

        ctx = transformation_ctx
        result = remove_duplicates(ctx)
        assert result.operation == "remove_duplicates"
        assert result.rows_affected > 0

    async def test_remove_duplicates_subset(self, transformation_ctx: Context) -> None:
        """Test removing duplicates based on subset of columns."""
        ctx = transformation_ctx
        result = remove_duplicates(ctx, subset=["age", "score"])
        assert result.success is True

    async def test_remove_duplicates_keep_options(self, transformation_ctx: Context) -> None:
        """Test different keep options."""
        for keep_option in ["first", "last", "none"]:
            ctx = transformation_ctx
            result = remove_duplicates(ctx, keep=keep_option)  # type: ignore[arg-type]  # Testing different keep options
            assert result.operation == "remove_duplicates"


@pytest.mark.asyncio
class TestTransformationServerFillMissing:
    """Test fill_missing_values server function."""

    async def test_fill_missing_drop(self, transformation_ctx: Context) -> None:
        """Test dropping rows with missing values."""
        ctx = transformation_ctx
        result = fill_missing_values(ctx, strategy="drop")
        assert result.operation == "fill_missing_values"
        assert result.success is True

    async def test_fill_missing_with_value(self, transformation_ctx: Context) -> None:
        """Test filling with specific value."""
        ctx = transformation_ctx
        result = fill_missing_values(ctx, strategy="fill", value="Unknown")
        assert result.success is True

    async def test_fill_missing_forward_fill(self, transformation_ctx: Context) -> None:
        """Test forward fill strategy."""
        ctx = transformation_ctx
        result = fill_missing_values(ctx, strategy="forward")
        assert result.success is True

    async def test_fill_missing_column_specific(self, transformation_ctx: Context) -> None:
        """Test filling specific columns only."""
        ctx = transformation_ctx
        result = fill_missing_values(ctx, strategy="fill", value="N/A", columns=["notes"])
        assert result.success is True

    async def test_fill_missing_statistical(self, transformation_ctx: Context) -> None:
        """Test statistical fill strategies."""
        for strategy in ["mean", "median", "mode"]:
            ctx = transformation_ctx
            result = fill_missing_values(ctx, strategy=strategy)  # type: ignore[arg-type]  # Testing different strategies
            assert result.success is True


@pytest.mark.asyncio
class TestTransformationServerErrorHandling:
    """Test error handling in transformation server."""

    async def test_filter_invalid_session(self) -> None:
        """Test filtering with invalid session."""

        conditions = [FilterCondition(column="test", operator="=", value="test")]

        ctx = create_mock_context("invalid-session-id")

        with pytest.raises(NoDataLoadedError):
            filter_rows(ctx, conditions)

    async def test_sort_invalid_session(self) -> None:
        """Test sorting with invalid session."""

        columns: list[str | SortColumn] = [SortColumn(column="test", ascending=True)]

        ctx = create_mock_context("invalid-session-id")

        with pytest.raises(NoDataLoadedError):
            sort_data(ctx, columns)

    async def test_filter_invalid_column(self, transformation_ctx: Context) -> None:
        """Test filtering with invalid column name."""
        conditions = [FilterCondition(column="nonexistent", operator="=", value="test")]

        ctx = transformation_ctx

        with pytest.raises(ColumnNotFoundError):
            filter_rows(ctx, conditions)

    async def test_sort_invalid_column(self, transformation_ctx: Context) -> None:
        """Test sorting with invalid column name."""
        columns: list[str | SortColumn] = [SortColumn(column="nonexistent", ascending=True)]

        ctx = transformation_ctx

        with pytest.raises(ToolError):
            sort_data(ctx, columns)
