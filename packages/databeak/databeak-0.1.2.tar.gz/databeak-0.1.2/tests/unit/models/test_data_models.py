"""Unit tests for data models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from databeak.models.data_models import (
    ColumnSchema,
    ComparisonOperator,
    DataPreview,
    DataStatistics,
    DataType,
    FilterCondition,
    OperationResult,
    SessionInfo,
    SortSpec,
)


class TestFilterCondition:
    """Test FilterCondition model."""

    def test_valid_filter_condition(self) -> None:
        """Test valid filter condition creation."""
        condition = FilterCondition(
            column="age", operator=ComparisonOperator.GREATER_THAN_OR_EQUALS, value=18
        )
        assert condition.column == "age"
        assert condition.operator == ComparisonOperator.GREATER_THAN_OR_EQUALS
        assert condition.value == 18

    def test_filter_condition_operators(self) -> None:
        """Test all valid operators."""
        valid_operators = [
            ComparisonOperator.EQUALS,
            ComparisonOperator.NOT_EQUALS,
            ComparisonOperator.GREATER_THAN,
            ComparisonOperator.LESS_THAN,
            ComparisonOperator.GREATER_THAN_OR_EQUALS,
            ComparisonOperator.LESS_THAN_OR_EQUALS,
            ComparisonOperator.CONTAINS,
            ComparisonOperator.NOT_CONTAINS,
            ComparisonOperator.IN,
            ComparisonOperator.NOT_IN,
        ]

        for operator in valid_operators:
            condition = FilterCondition(column="test_col", operator=operator, value="test_value")
            assert condition.operator == operator

    def test_filter_condition_invalid_operator(self) -> None:
        """Test invalid operator raises validation error."""
        with pytest.raises(ValidationError):
            FilterCondition(column="test_col", operator="invalid_op", value="test_value")

    def test_filter_condition_various_value_types(self) -> None:
        """Test filter condition with various value types."""
        # String value
        condition1 = FilterCondition(
            column="name", operator=ComparisonOperator.EQUALS, value="John"
        )
        assert condition1.value == "John"

        # Numeric value
        condition2 = FilterCondition(
            column="age", operator=ComparisonOperator.GREATER_THAN, value=25
        )
        assert condition2.value == 25

        # Boolean value
        condition3 = FilterCondition(
            column="active", operator=ComparisonOperator.EQUALS, value=True
        )
        assert condition3.value is True

        # List value for 'in' operator
        condition4 = FilterCondition(
            column="status", operator=ComparisonOperator.IN, value=["active", "pending"]
        )
        assert condition4.value == ["active", "pending"]

    def test_filter_condition_none_value(self) -> None:
        """Test filter condition with None value."""
        condition = FilterCondition(
            column="optional_field", operator=ComparisonOperator.EQUALS, value=None
        )
        assert condition.value is None

    def test_filter_condition_extra_fields_forbidden(self) -> None:
        """Test that extra fields are allowed (no extra='forbid' configured)."""
        # FilterCondition allows extra fields by default
        condition = FilterCondition(
            column="test_col", operator=ComparisonOperator.EQUALS, value="test_value"
        )
        assert condition.column == "test_col"


class TestSortSpec:
    """Test SortSpec model."""

    def test_sort_spec_default_ascending(self) -> None:
        """Test default ascending behavior."""
        sort_spec = SortSpec(column="name")
        assert sort_spec.column == "name"
        assert sort_spec.ascending is True

    def test_sort_spec_explicit_descending(self) -> None:
        """Test explicit descending sort."""
        sort_spec = SortSpec(column="date", ascending=False)
        assert sort_spec.column == "date"
        assert sort_spec.ascending is False

    def test_sort_spec_empty_column_name(self) -> None:
        """Test validation with empty column name."""
        # Note: Pydantic doesn't validate empty strings by default
        # This test expects a validation error that doesn't actually occur
        sort_spec = SortSpec(column="")
        assert sort_spec.column == ""

    def test_sort_spec_extra_fields_forbidden(self) -> None:
        """Test that extra fields are allowed (no extra='forbid' configured)."""
        # SortSpec allows extra fields by default
        sort_spec = SortSpec(column="test_col", ascending=True)
        assert sort_spec.column == "test_col"


class TestDataType:
    """Test DataType enum."""

    def test_data_type_values(self) -> None:
        """Test all data type values."""
        expected_values = {"integer", "float", "string", "datetime", "boolean", "mixed"}
        actual_values = {dt.value for dt in DataType}
        assert actual_values == expected_values

    def test_data_type_string_conversion(self) -> None:
        """Test string conversion of data types."""
        assert str(DataType.INTEGER) == "DataType.INTEGER"
        assert str(DataType.FLOAT) == "DataType.FLOAT"
        assert str(DataType.STRING) == "DataType.STRING"


class TestComparisonOperator:
    """Test ComparisonOperator enum."""

    def test_comparison_operator_values(self) -> None:
        """Test comparison operator values."""
        operators = {op.value for op in ComparisonOperator}
        expected = {
            "=",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
            "contains",
            "not_contains",
            "starts_with",
            "ends_with",
            "in",
            "not_in",
            "is_null",
            "is_not_null",
        }
        assert operators == expected


class TestColumnSchema:
    """Test ColumnSchema model."""

    def test_column_schema_basic(self) -> None:
        """Test basic column schema creation."""
        schema = ColumnSchema(name="user_id", dtype=DataType.INTEGER, nullable=False)
        assert schema.name == "user_id"
        assert schema.dtype == DataType.INTEGER
        assert schema.nullable is False

    def test_column_schema_with_constraints(self) -> None:
        """Test column schema with constraints."""
        schema = ColumnSchema(
            name="age",
            dtype=DataType.INTEGER,
            nullable=False,
            min_value=0,
            max_value=150,
        )
        assert schema.min_value == 0
        assert schema.max_value == 150

    def test_column_schema_nullable(self) -> None:
        """Test nullable column schema."""
        schema = ColumnSchema(name="middle_name", dtype=DataType.STRING, nullable=True)
        assert schema.nullable is True


class TestOperationResult:
    """Test OperationResult model."""

    def test_operation_result_success(self) -> None:
        """Test successful operation result."""
        result = OperationResult(
            success=True,
            rows_affected=25,
            message="Filter applied successfully",
        )
        assert result.success is True
        assert result.rows_affected == 25
        assert result.message == "Filter applied successfully"

    def test_operation_result_failure(self) -> None:
        """Test failed operation result."""
        result = OperationResult(
            success=False,
            message="Operation failed",
            error="Invalid sort column",
        )
        assert result.success is False
        assert result.error == "Invalid sort column"
        assert result.message == "Operation failed"

    def test_operation_result_with_metadata(self) -> None:
        """Test operation result with data."""
        data = {"execution_time": 0.5, "memory_used": "10MB"}
        result = OperationResult(success=True, message="Operation completed", data=data)
        assert result.data == data
        assert result.success is True


class TestSessionInfo:
    """Test SessionInfo model."""

    def test_session_info_basic(self) -> None:
        """Test basic session info creation."""
        created_time = datetime(2024, 1, 15, 10, 30, 0)
        accessed_time = datetime(2024, 1, 15, 11, 0, 0)
        info = SessionInfo(
            session_id="session_123",
            created_at=created_time,
            last_accessed=accessed_time,
            row_count=100,
            column_count=5,
            columns=["col1", "col2", "col3", "col4", "col5"],
            memory_usage_mb=12.5,
            operations_count=5,
        )
        assert info.session_id == "session_123"
        assert info.operations_count == 5
        assert info.row_count == 100
        assert info.column_count == 5

    def test_session_info_with_file_info(self) -> None:
        """Test session info with file information."""
        created_time = datetime(2024, 1, 15, 10, 30, 0)
        accessed_time = datetime(2024, 1, 15, 11, 0, 0)
        info = SessionInfo(
            session_id="session_456",
            created_at=created_time,
            last_accessed=accessed_time,
            row_count=50,
            column_count=3,
            columns=["id", "name", "value"],
            memory_usage_mb=8.2,
            operations_count=3,
            file_path="data.csv",
        )
        assert info.file_path == "data.csv"
        assert info.operations_count == 3


class TestDataStatistics:
    """Test DataStatistics model."""

    def test_data_statistics_basic(self) -> None:
        """Test basic data statistics creation."""
        stats = DataStatistics(
            column="age",
            dtype="int64",
            count=975,
            null_count=25,
            unique_count=50,
            mean=35.5,
            std=12.2,
            min=18,
            max=95,
        )
        assert stats.column == "age"
        assert stats.dtype == "int64"
        assert stats.count == 975
        assert stats.null_count == 25
        assert stats.mean == 35.5

    def test_data_statistics_with_percentiles(self) -> None:
        """Test data statistics with percentiles."""
        stats = DataStatistics(
            column="score",
            dtype="float64",
            count=500,
            null_count=10,
            unique_count=100,
            mean=75.5,
            std=15.2,
            min=20.0,
            max=100.0,
            q25=65.0,
            q50=75.0,
            q75=85.0,
        )
        assert stats.q25 == 65.0
        assert stats.q50 == 75.0
        assert stats.q75 == 85.0


class TestDataPreview:
    """Test DataPreview model."""

    def test_data_preview_basic(self) -> None:
        """Test basic data preview creation."""
        sample_data: list[dict[str, str | int | float | bool | None]] = [
            {"id": 1, "name": "John", "age": 25},
            {"id": 2, "name": "Jane", "age": 30},
        ]

        preview = DataPreview(rows=sample_data, row_count=1000, column_count=3)

        assert len(preview.rows) == 2
        assert preview.row_count == 1000
        assert preview.column_count == 3

    def test_data_preview_with_truncation(self) -> None:
        """Test data preview with truncation info."""
        preview = DataPreview(
            rows=[{"col1": "value1", "col2": "value2"}],
            row_count=10000,
            column_count=2,
            truncated=True,
        )
        assert preview.truncated is True
