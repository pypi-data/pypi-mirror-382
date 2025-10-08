"""Comprehensive validation tests for all Pydantic models in tool_responses.py.

This module tests field validation, serialization/deserialization, and edge cases for the 29
Pydantic models used in DataBeak's MCP tool responses.
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from databeak.models import DataPreview
from databeak.models.data_models import SessionInfo

# Import statistics models from dedicated module
from databeak.models.statistics_models import (
    ColumnStatisticsResult,
    CorrelationResult,
    StatisticsResult,
    StatisticsSummary,
    ValueCountsResult,
)
from databeak.models.tool_responses import (
    # Core tool responses
    CellLocation,
    CellValueResult,
    ColumnOperationResult,
    DataTypeInfo,
    DeleteRowResult,
    FilterOperationResult,
    HealthResult,
    InsertRowResult,
    MissingDataInfo,
    # RenameColumnsResult,  # Not yet implemented
    ServerInfoResult,
    SortDataResult,
    UpdateRowResult,
)

# Import discovery server models
from databeak.servers.discovery_server import (
    GroupStatistics,
    OutlierInfo,
    OutliersResult,
    ProfileInfo,
)

# Import IO server models that moved to modular architecture
from databeak.servers.io_server import (
    ExportResult,
    LoadResult,
    SessionInfoResult,
)

# =============================================================================
# NESTED MODELS TESTS
# =============================================================================


class TestSessionInfo:
    """Test SessionInfo model."""

    @pytest.mark.parametrize(
        ("session_data", "expected_attrs"),
        [
            (
                {
                    "session_id": "test-123",
                    "created_at": "2023-01-01T10:00:00Z",
                    "last_accessed": "2023-01-01T10:30:00Z",
                    "row_count": 100,
                    "column_count": 5,
                    "columns": ["id", "name", "age", "email", "salary"],
                    "memory_usage_mb": 2.5,
                    "file_path": "/path/to/file.csv",
                },
                {"session_id": "test-123", "row_count": 100, "file_path": "/path/to/file.csv"},
            ),
            (
                {
                    "session_id": "test-456",
                    "created_at": "2023-01-01T10:00:00Z",
                    "last_accessed": "2023-01-01T10:30:00Z",
                    "row_count": 100,
                    "column_count": 5,
                    "columns": ["id", "name"],
                    "memory_usage_mb": 1.0,
                },
                {"session_id": "test-456", "row_count": 100, "file_path": None},
            ),
        ],
    )
    def test_session_info_variations(
        self, session_data: dict[str, Any], expected_attrs: dict[str, Any]
    ) -> None:
        """Test SessionInfo creation with different configurations."""
        session = SessionInfo(**session_data)
        for attr, expected_value in expected_attrs.items():
            assert getattr(session, attr) == expected_value

    def test_missing_required_field(self) -> None:
        """Test missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SessionInfo(  # type: ignore [call-arg]
                session_id="test-123",
                created_at=datetime.fromisoformat("2023-01-01T10:00:00+00:00"),
                # Missing required fields
            )
        assert "Field required" in str(exc_info.value)

    def test_serialization_roundtrip(self) -> None:
        """Test serialization and deserialization."""
        original = SessionInfo(
            session_id="test-123",
            created_at=datetime.fromisoformat("2023-01-01T10:00:00+00:00"),
            last_accessed=datetime.fromisoformat("2023-01-01T10:30:00+00:00"),
            row_count=100,
            column_count=5,
            columns=["id", "name"],
            memory_usage_mb=1.5,
        )
        data = original.model_dump()
        restored = SessionInfo(**data)
        assert restored == original


class TestOutlierInfo:
    """Test OutlierInfo model."""

    def test_valid_creation_with_all_fields(self) -> None:
        """Test valid OutlierInfo creation with all fields."""
        outlier = OutlierInfo(
            row_index=42,
            value=99.9,
            z_score=3.2,
            iqr_score=2.1,
        )
        assert outlier.row_index == 42
        assert outlier.value == 99.9
        assert outlier.z_score == 3.2
        assert outlier.iqr_score == 2.1

    def test_optional_score_fields(self) -> None:
        """Test OutlierInfo with optional score fields as None."""
        outlier = OutlierInfo(row_index=42, value=99.9)
        assert outlier.z_score is None
        assert outlier.iqr_score is None

    def test_invalid_types(self) -> None:
        """Test invalid data types raise ValidationError."""
        with pytest.raises(ValidationError):
            OutlierInfo(row_index="not_an_int", value=99.9)


class TestStatisticsSummary:
    """Test StatisticsSummary model with field aliases."""

    def test_valid_creation(self) -> None:
        """Test valid StatisticsSummary creation."""
        stats = StatisticsSummary(
            count=100,
            mean=50.5,
            std=15.2,
            min=10.0,
            percentile_25=35.0,
            percentile_50=50.0,
            percentile_75=65.0,
            max=90.0,
        )
        assert stats.count == 100
        assert stats.percentile_25 == 35.0

    def test_field_aliases(self) -> None:
        """Test field aliases work correctly."""
        # Using aliases in dict
        data = {
            "count": 100,
            "mean": 50.0,
            "std": 15.0,
            "min": 10.0,
            "25%": 35.0,  # alias
            "50%": 50.0,  # alias
            "75%": 65.0,  # alias
            "max": 90.0,
        }
        stats = StatisticsSummary(**data)
        assert stats.percentile_25 == 35.0
        assert stats.percentile_50 == 50.0
        assert stats.percentile_75 == 65.0

    def test_serialization_with_aliases(self) -> None:
        """Test serialization includes both field names and aliases."""
        stats = StatisticsSummary(
            count=100,
            mean=50.0,
            std=15.0,
            min=10.0,
            percentile_25=35.0,
            percentile_50=50.0,
            percentile_75=65.0,
            max=90.0,
        )
        # Test by_alias=True serialization
        data = stats.model_dump(by_alias=True)
        assert "25%" in data
        assert "50%" in data
        assert "75%" in data


class TestDataTypeInfo:
    """Test DataTypeInfo model with Literal types."""

    def test_valid_types(self) -> None:
        """Test valid data types."""
        for dtype in ["int64", "float64", "object", "bool", "datetime64", "category"]:
            info = DataTypeInfo(
                type=dtype,
                nullable=True,
                unique_count=10,
                null_count=2,
            )
            assert info.type == dtype

    def test_invalid_type(self) -> None:
        """Test invalid data type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DataTypeInfo(
                type="invalid_type",
                nullable=True,
                unique_count=10,
                null_count=2,
            )
        assert "Input should be" in str(exc_info.value)


class TestMissingDataInfo:
    """Test MissingDataInfo model."""

    def test_valid_creation(self) -> None:
        """Test valid MissingDataInfo creation."""
        missing_info = MissingDataInfo(
            total_missing=25,
            missing_by_column={"age": 10, "salary": 15},
            missing_percentage=12.5,
        )
        assert missing_info.total_missing == 25
        assert missing_info.missing_by_column["age"] == 10


class TestDataPreview:
    """Test DataPreview model."""

    def test_valid_creation(self) -> None:
        """Test valid DataPreview creation."""
        preview = DataPreview(
            rows=[
                {"id": 1, "name": "John", "age": 30},
                {"id": 2, "name": "Jane", "age": 25},
            ],
            row_count=2,
            column_count=3,
            truncated=False,
        )
        assert len(preview.rows) == 2
        assert preview.truncated is False

    def test_mixed_data_types(self) -> None:
        """Test DataPreview with mixed data types in rows."""
        preview = DataPreview(
            rows=[
                {"id": 1, "name": "John", "active": True, "score": 95.5},
                {"id": 2, "name": None, "active": False, "score": None},
            ],
            row_count=2,
            column_count=4,
        )
        assert preview.rows[0]["active"] is True
        assert preview.rows[1]["name"] is None


class TestGroupStatistics:
    """Test GroupStatistics model with optional fields."""

    def test_all_fields_present(self) -> None:
        """Test GroupStatistics with all fields."""
        stats = GroupStatistics(
            count=10,
            mean=50.0,
            sum=500.0,
            min=10.0,
            max=90.0,
            std=15.5,
        )
        assert stats.count == 10
        assert stats.mean == 50.0

    def test_only_required_fields(self) -> None:
        """Test GroupStatistics with only count (required)."""
        stats = GroupStatistics(count=10)
        assert stats.count == 10
        assert stats.mean is None
        assert stats.sum is None


class TestCellLocation:
    """Test CellLocation model."""

    def test_valid_creation(self) -> None:
        """Test valid CellLocation creation."""
        cell = CellLocation(row=5, column="name", value="John Doe")
        assert cell.row == 5
        assert cell.column == "name"
        assert cell.value == "John Doe"

    def test_csv_cell_value_types(self) -> None:
        """Test CellLocation accepts standard CSV value types."""
        for value in [42, 3.14, "text", True, None]:
            cell = CellLocation(row=0, column="test", value=value)
            assert cell.value == value

    def test_invalid_complex_types(self) -> None:
        """Test CellLocation rejects complex types that aren't valid CSV cell values."""
        with pytest.raises(ValidationError):
            CellLocation(row=0, column="test", value=[1, 2, 3])
        with pytest.raises(ValidationError):
            CellLocation(row=0, column="test", value={"key": "value"})


class TestProfileInfo:
    """Test ProfileInfo model."""

    def test_valid_creation(self) -> None:
        """Test valid ProfileInfo creation."""
        profile = ProfileInfo(
            column_name="age",
            data_type="int64",
            null_count=5,
            null_percentage=2.5,
            unique_count=45,
            unique_percentage=90.0,
            most_frequent=25,
            frequency=3,
        )
        assert profile.column_name == "age"
        assert profile.most_frequent == 25

    def test_optional_fields(self) -> None:
        """Test ProfileInfo with optional fields as None."""
        profile = ProfileInfo(
            column_name="age",
            data_type="int64",
            null_count=5,
            null_percentage=2.5,
            unique_count=45,
            unique_percentage=90.0,
        )
        assert profile.most_frequent is None
        assert profile.frequency is None


# =============================================================================
# SYSTEM TOOL RESPONSES TESTS
# =============================================================================


class TestHealthResult:
    """Test HealthResult model."""

    def test_valid_creation(self) -> None:
        """Test valid HealthResult creation."""
        health = HealthResult(
            status="healthy",
            version="1.0.0",
            active_sessions=3,
            max_sessions=10,
            session_ttl_minutes=30,
            memory_usage_mb=512.0,
            memory_threshold_mb=2048.0,
            memory_status="normal",
            history_operations_total=25,
            history_limit_per_session=1000,
        )
        assert health.success is True  # Inherited default
        assert health.status == "healthy"
        assert health.active_sessions == 3

    def test_missing_required_field(self) -> None:
        """Test missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            HealthResult(status="healthy")  # type: ignore [call-arg]


class TestServerInfoResult:
    """Test ServerInfoResult model."""

    def test_valid_creation(self) -> None:
        """Test valid ServerInfoResult creation."""
        server_info = ServerInfoResult(
            name="DataBeak",
            version="1.0.0",
            description="CSV manipulation server",
            capabilities={"analytics": ["statistics", "correlation"]},
            supported_formats=["csv", "json", "excel"],
            max_file_size_mb=100,
            session_timeout_minutes=30,
        )
        assert server_info.name == "DataBeak"
        assert "analytics" in server_info.capabilities


# =============================================================================
# IO TOOL RESPONSES TESTS
# =============================================================================


class TestLoadResult:
    """Test LoadResult model - one of the critical models."""

    def test_valid_creation_minimal(self) -> None:
        """Test valid LoadResult creation with minimal required fields."""
        result = LoadResult(
            rows_affected=100,
            columns_affected=["id", "name", "age"],
        )
        assert result.success is True
        assert result.rows_affected == 100
        assert len(result.columns_affected) == 3
        assert result.data is None  # Optional field
        assert result.memory_usage_mb is None  # Optional field

    def test_valid_creation_with_optional_fields(self) -> None:
        """Test valid LoadResult creation with all fields."""
        preview = DataPreview(
            rows=[{"id": 1, "name": "John"}],
            row_count=1,
            column_count=2,
        )
        result = LoadResult(
            rows_affected=50,
            columns_affected=["id", "name"],
            data=preview,
            memory_usage_mb=1.5,
        )
        assert result.data is not None
        assert result.memory_usage_mb == 1.5

    def test_missing_required_fields(self) -> None:
        """Test missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LoadResult()  # type: ignore [call-arg]  # Missing rows_affected, columns_affected
        assert "Field required" in str(exc_info.value)

    def test_invalid_field_types(self) -> None:
        """Test invalid field types raise ValidationError."""
        with pytest.raises(ValidationError):
            LoadResult(
                rows_affected="not_an_int",  # Should be int
                columns_affected=["col1"],
            )

    def test_serialization_roundtrip(self) -> None:
        """Test serialization and deserialization preserves data."""
        original = LoadResult(
            rows_affected=75,
            columns_affected=["a", "b", "c"],
            memory_usage_mb=2.0,
        )
        # Test dict serialization
        data = original.model_dump()
        restored = LoadResult(**data)
        assert restored == original

        # Test JSON serialization
        json_str = original.model_dump_json()
        json_data = json.loads(json_str)
        restored_from_json = LoadResult(**json_data)
        assert restored_from_json == original

    def test_extra_fields_ignored(self) -> None:
        """Test extra fields are ignored during creation."""
        data = {
            "rows_affected": 100,
            "columns_affected": ["id"],
            "extra_field": "should_be_ignored",
        }
        result = LoadResult(**data)
        assert result.rows_affected == 100
        # Extra field should not cause an error (Pydantic ignores by default)


class TestSessionInfoResult:
    """Test SessionInfoResult model - one of the critical models."""

    def test_valid_creation(self) -> None:
        """Test valid SessionInfoResult creation."""
        result = SessionInfoResult(
            created_at="2023-01-01T10:00:00Z",
            last_modified="2023-01-01T10:30:00Z",
            data_loaded=True,
            row_count=100,
            column_count=5,
        )
        assert result.data_loaded is True
        assert result.row_count == 100

    def test_optional_count_fields(self) -> None:
        """Test optional count fields can be None."""
        result = SessionInfoResult(
            created_at="2023-01-01T10:00:00Z",
            last_modified="2023-01-01T10:30:00Z",
            data_loaded=False,
        )
        assert result.row_count is None
        assert result.column_count is None


class TestExportResult:
    """Test ExportResult model."""

    def test_valid_creation(self) -> None:
        """Test valid ExportResult creation."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            result = ExportResult(
                file_path=tmp.name,
                format="csv",
                rows_exported=100,
                file_size_mb=0.5,
            )
            assert result.format == "csv"
            assert result.rows_exported == 100
            # Clean up
            Path(tmp.name).unlink()

    def test_literal_format_validation(self) -> None:
        """Test format field validates against literal values."""
        valid_formats = ["csv", "tsv", "json", "excel", "parquet", "html", "markdown"]
        with tempfile.NamedTemporaryFile() as tmp:
            for fmt in valid_formats:
                result = ExportResult(
                    file_path=tmp.name,
                    format=fmt,
                    rows_exported=10,
                )
                assert result.format == fmt

            # Test invalid format
            with pytest.raises(ValidationError):
                ExportResult(
                    file_path=tmp.name,
                    format="invalid_format",
                    rows_exported=10,
                )


# =============================================================================
# ANALYTICS TOOL RESPONSES TESTS
# =============================================================================


class TestStatisticsResult:
    """Test StatisticsResult model - one of the critical models."""

    def test_valid_creation(self) -> None:
        """Test valid StatisticsResult creation."""
        stats = {
            "age": StatisticsSummary(
                count=100,
                mean=35.5,
                std=12.2,
                min=18.0,
                percentile_25=28.0,
                percentile_50=35.0,
                percentile_75=43.0,
                max=65.0,
            ),
        }
        result = StatisticsResult(
            statistics=stats,
            column_count=1,
            numeric_columns=["age"],
            total_rows=100,
        )
        assert "age" in result.statistics
        assert result.statistics["age"].mean == 35.5

    def test_multiple_columns(self) -> None:
        """Test StatisticsResult with multiple columns."""
        stats = {
            "age": StatisticsSummary(
                count=100,
                mean=35.0,
                std=10.0,
                min=18.0,
                percentile_25=28.0,
                percentile_50=35.0,
                percentile_75=42.0,
                max=65.0,
            ),
            "salary": StatisticsSummary(
                count=100,
                mean=55000.0,
                std=15000.0,
                min=30000.0,
                percentile_25=45000.0,
                percentile_50=55000.0,
                percentile_75=65000.0,
                max=90000.0,
            ),
        }
        result = StatisticsResult(
            statistics=stats,
            column_count=2,
            numeric_columns=["age", "salary"],
            total_rows=100,
        )
        assert len(result.statistics) == 2
        assert set(result.numeric_columns) == {"age", "salary"}


class TestCorrelationResult:
    """Test CorrelationResult model."""

    def test_valid_creation(self) -> None:
        """Test valid CorrelationResult creation."""
        matrix = {
            "age": {"age": 1.0, "salary": 0.75},
            "salary": {"age": 0.75, "salary": 1.0},
        }
        result = CorrelationResult(
            correlation_matrix=matrix,
            method="pearson",
            columns_analyzed=["age", "salary"],
        )
        assert result.method == "pearson"
        assert result.correlation_matrix["age"]["salary"] == 0.75

    def test_correlation_methods(self) -> None:
        """Test all valid correlation methods."""
        matrix = {"a": {"a": 1.0}}
        for method in ["pearson", "spearman", "kendall"]:
            result = CorrelationResult(
                correlation_matrix=matrix,
                method=method,
                columns_analyzed=["a"],
            )
            assert result.method == method

    def test_invalid_correlation_method(self) -> None:
        """Test invalid correlation method raises ValidationError."""
        with pytest.raises(ValidationError):
            CorrelationResult(
                correlation_matrix={"a": {"a": 1.0}},
                method="invalid_method",
                columns_analyzed=["a"],
            )


class TestValueCountsResult:
    """Test ValueCountsResult model."""

    def test_valid_creation(self) -> None:
        """Test valid ValueCountsResult creation."""
        result = ValueCountsResult(
            column="status",
            value_counts={"active": 75, "inactive": 25},
            total_values=100,
            unique_values=2,
        )
        assert result.column == "status"
        assert result.value_counts["active"] == 75

    def test_mixed_value_types(self) -> None:
        """Test ValueCountsResult with mixed value types."""
        result = ValueCountsResult(
            column="mixed",
            value_counts={"text": 10, "123": 5, "true": 3},
            total_values=18,
            unique_values=3,
        )
        assert len(result.value_counts) == 3


class TestOutliersResult:
    """Test OutliersResult model."""

    def test_valid_creation(self) -> None:
        """Test valid OutliersResult creation."""
        outliers = {
            "age": [
                OutlierInfo(row_index=42, value=95.0, z_score=3.2),
                OutlierInfo(row_index=15, value=-5.0, z_score=-2.8),
            ],
        }
        result = OutliersResult(
            outliers_found=2,
            outliers_by_column=outliers,
            method="zscore",
            threshold=3.0,
        )
        assert result.outliers_found == 2
        assert len(result.outliers_by_column["age"]) == 2

    def test_outlier_methods(self) -> None:
        """Test all valid outlier detection methods."""
        outliers = {"col": [OutlierInfo(row_index=0, value=100.0)]}
        for method in ["zscore", "iqr", "isolation_forest"]:
            result = OutliersResult(
                outliers_found=1,
                outliers_by_column=outliers,
                method=method,
                threshold=2.0,
            )
            assert result.method == method


class TestColumnStatisticsResult:
    """Test ColumnStatisticsResult model - one of the critical models."""

    def test_valid_creation(self) -> None:
        """Test valid ColumnStatisticsResult creation."""
        stats = StatisticsSummary(
            count=100,
            mean=45.5,
            std=12.2,
            min=20.0,
            percentile_25=38.0,
            percentile_50=45.0,
            percentile_75=53.0,
            max=70.0,
        )
        result = ColumnStatisticsResult(
            column="age",
            statistics=stats,
            data_type="int64",
            non_null_count=98,
        )
        assert result.column == "age"
        assert result.data_type == "int64"
        assert result.statistics.mean == 45.5

    def test_all_data_types(self) -> None:
        """Test all valid data types."""
        stats = StatisticsSummary(
            count=10,
            mean=5.0,
            std=1.0,
            min=1.0,
            percentile_25=3.0,
            percentile_50=5.0,
            percentile_75=7.0,
            max=10.0,
        )
        for dtype in ["int64", "float64", "object", "bool", "datetime64", "category"]:
            result = ColumnStatisticsResult(
                column="test_col",
                statistics=stats,
                data_type=dtype,
                non_null_count=10,
            )
            assert result.data_type == dtype


# =============================================================================
# ROW TOOL RESPONSES TESTS
# =============================================================================


class TestCellValueResult:
    """Test CellValueResult model."""

    def test_valid_creation(self) -> None:
        """Test valid CellValueResult creation."""
        result = CellValueResult(
            value="John Doe",
            coordinates={"row": 5, "column": "name"},
            data_type="string",
        )
        assert result.value == "John Doe"
        assert result.coordinates["row"] == 5

    def test_various_value_types(self) -> None:
        """Test CellValueResult with various value types."""
        test_values: list[str | int | float | bool | None] = [42, 3.14, "text", True, None]
        for value in test_values:
            result = CellValueResult(
                value=value,
                coordinates={"row": 0, "column": "test"},
                data_type=type(value).__name__ if value is not None else "None",
            )
            assert result.value == value


class TestInsertRowResult:
    """Test InsertRowResult model."""

    def test_valid_creation(self) -> None:
        """Test valid InsertRowResult creation."""
        result = InsertRowResult(
            row_index=10,
            rows_before=100,
            rows_after=101,
            data_inserted={"id": 101, "name": "New User", "age": 30},
            columns=["id", "name", "age"],
        )
        assert result.operation == "insert_row"  # Default value
        assert result.row_index == 10
        assert result.rows_before == 100
        assert result.rows_after == 101

    def test_default_operation_field(self) -> None:
        """Test default operation field value."""
        result = InsertRowResult(
            row_index=5,
            rows_before=50,
            rows_after=51,
            data_inserted={"col": "value"},
            columns=["col"],
        )
        assert result.operation == "insert_row"


class TestDeleteRowResult:
    """Test DeleteRowResult model."""

    def test_valid_creation(self) -> None:
        """Test valid DeleteRowResult creation."""
        result = DeleteRowResult(
            row_index=5,
            rows_before=100,
            rows_after=99,
            deleted_data={"id": 6, "name": "Deleted User"},
        )
        assert result.operation == "delete_row"  # Default value
        assert result.rows_before == 100
        assert result.rows_after == 99


class TestUpdateRowResult:
    """Test UpdateRowResult model."""

    def test_valid_creation(self) -> None:
        """Test valid UpdateRowResult creation."""
        result = UpdateRowResult(
            row_index=10,
            columns_updated=["name", "age"],
            old_values={"name": "John", "age": 30},
            new_values={"name": "John Doe", "age": 31},
            changes_made=2,
        )
        assert result.operation == "update_row"  # Default value
        assert len(result.columns_updated) == 2
        assert result.changes_made == 2


# =============================================================================
# DATA TOOL RESPONSES TESTS
# =============================================================================


class TestFilterOperationResult:
    """Test FilterOperationResult model - one of the critical models."""

    def test_valid_creation(self) -> None:
        """Test valid FilterOperationResult creation."""
        result = FilterOperationResult(
            rows_before=1000,
            rows_after=750,
            rows_filtered=250,
            conditions_applied=2,
        )
        assert result.rows_before == 1000
        assert result.rows_after == 750
        assert result.rows_filtered == 250
        assert result.conditions_applied == 2

    def test_calculated_fields_consistency(self) -> None:
        """Test that filter counts are logically consistent."""
        result = FilterOperationResult(
            rows_before=100,
            rows_after=60,
            rows_filtered=40,
            conditions_applied=1,
        )
        # Verify mathematical relationship
        assert result.rows_before - result.rows_after == result.rows_filtered

    def test_missing_required_field(self) -> None:
        """Test missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            FilterOperationResult(  # type: ignore [call-arg]
                rows_before=100,
                # Missing rows_after, rows_filtered, conditions_applied
            )

    def test_negative_values_validation(self) -> None:
        """Test validation handles negative values appropriately."""
        # This should work (though logically odd)
        result = FilterOperationResult(
            rows_before=0,
            rows_after=0,
            rows_filtered=0,
            conditions_applied=0,
        )
        assert result.rows_filtered == 0


class TestColumnOperationResult:
    """Test ColumnOperationResult model - one of the critical models."""

    def test_valid_creation_minimal(self) -> None:
        """Test valid ColumnOperationResult creation with minimal fields."""
        result = ColumnOperationResult(
            operation="add_column",
            rows_affected=100,
            columns_affected=["new_column"],
        )
        assert result.operation == "add_column"
        assert result.rows_affected == 100
        assert result.columns_affected == ["new_column"]
        # Optional fields should be None
        assert result.original_sample is None
        assert result.updated_sample is None
        assert result.part_index is None
        assert result.transform is None
        assert result.nulls_filled is None

    def test_valid_creation_with_all_fields(self) -> None:
        """Test valid ColumnOperationResult creation with all optional fields."""
        result = ColumnOperationResult(
            operation="transform_column",
            rows_affected=50,
            columns_affected=["transformed_col"],
            original_sample=["old_val1", "old_val2"],
            updated_sample=["new_val1", "new_val2"],
            part_index=1,
            transform="uppercase",
            nulls_filled=5,
        )
        assert result.original_sample == ["old_val1", "old_val2"]
        assert result.updated_sample == ["new_val1", "new_val2"]
        assert result.part_index == 1
        assert result.transform == "uppercase"
        assert result.nulls_filled == 5

    def test_mixed_sample_types(self) -> None:
        """Test ColumnOperationResult with mixed types in samples."""
        result = ColumnOperationResult(
            operation="clean_column",
            rows_affected=25,
            columns_affected=["mixed_col"],
            original_sample=[1, "text", 3.14, None, True],
            updated_sample=[1, "TEXT", 3.14, "N/A", True],
        )
        assert result.original_sample is not None
        assert result.original_sample[1] == "text"
        assert result.updated_sample is not None
        assert result.updated_sample[1] == "TEXT"
        assert result.original_sample is not None
        assert result.original_sample[3] is None
        assert result.updated_sample is not None
        assert result.updated_sample[3] == "N/A"

    def test_serialization_with_optional_fields(self) -> None:
        """Test serialization handles optional fields correctly."""
        result = ColumnOperationResult(
            operation="remove_column",
            rows_affected=100,
            columns_affected=["removed_col"],
            nulls_filled=0,
        )

        # Test dict serialization
        data = result.model_dump()
        assert data["nulls_filled"] == 0
        assert "original_sample" not in data or data["original_sample"] is None

        # Test round-trip
        restored = ColumnOperationResult(**data)
        assert restored == result


# =============================================================================
# COMPREHENSIVE EDGE CASES AND ERROR HANDLING
# =============================================================================


class TestComprehensiveEdgeCases:
    """Test comprehensive edge cases across all models."""

    def test_empty_collections(self) -> None:
        """Test models handle empty collections appropriately."""
        # Empty columns list
        result = LoadResult(
            rows_affected=0,
            columns_affected=[],
        )
        assert len(result.columns_affected) == 0

        # Empty statistics dict
        stats_result = StatisticsResult(
            statistics={},
            column_count=0,
            numeric_columns=[],
            total_rows=0,
        )
        assert len(stats_result.statistics) == 0

    def test_unicode_and_special_characters(self) -> None:
        """Test models handle Unicode and special characters."""
        result = LoadResult(
            rows_affected=1,
            columns_affected=["名前", "年齢", "email@domain"],
        )
        assert "名前" in result.columns_affected

    def test_very_large_numbers(self) -> None:
        """Test models handle very large numbers."""
        result = FilterOperationResult(
            rows_before=999999999,
            rows_after=999999998,
            rows_filtered=1,
            conditions_applied=1,
        )
        assert result.rows_before == 999999999

    def test_json_serialization_edge_cases(self) -> None:
        """Test JSON serialization handles edge cases."""
        # Model with None values
        result = SessionInfoResult(
            created_at="2023-01-01T10:00:00Z",
            last_modified="2023-01-01T10:30:00Z",
            data_loaded=False,
        )

        json_str = result.model_dump_json()
        assert '"row_count":null' in json_str or '"row_count": null' in json_str

        # Verify it can be parsed back
        parsed = json.loads(json_str)
        restored = SessionInfoResult(**parsed)
        assert restored == result

    def test_model_validation_with_extra_fields(self) -> None:
        """Test all models handle extra fields appropriately."""
        # Test with LoadResult (critical model)
        data_with_extra = {
            "rows_affected": 50,
            "columns_affected": ["col1"],
            "unknown_field": "should_be_ignored",
            "another_extra": 42,
        }

        result = LoadResult(**data_with_extra)
        assert result.rows_affected == 50
        # Should not have extra fields as attributes
        assert not hasattr(result, "unknown_field")

    def test_pydantic_config_behavior(self) -> None:
        """Test Pydantic configuration behavior."""
        # Test StatisticsSummary Config settings
        stats = StatisticsSummary(
            count=100,
            mean=50.0,
            std=10.0,
            min=10.0,
            percentile_25=40.0,
            percentile_50=50.0,
            percentile_75=60.0,
            max=90.0,
        )

        # Should be able to use both field names and aliases
        data_with_alias = {
            "count": 100,
            "mean": 50.0,
            "std": 10.0,
            "min": 10.0,
            "25%": 40.0,
            "50%": 50.0,
            "75%": 60.0,
            "max": 90.0,
        }
        stats_from_alias = StatisticsSummary(**data_with_alias)
        assert stats_from_alias == stats

    def test_inheritance_behavior(self) -> None:
        """Test BaseToolResponse inheritance behavior."""
        # All response models should inherit from BaseToolResponse
        result = LoadResult(
            rows_affected=10,
            columns_affected=["col1"],
        )

        # Should have success field from base class
        assert hasattr(result, "success")
        assert result.success is True

        # Should be able to override success
        result_with_failure = LoadResult(
            success=False,
            rows_affected=0,
            columns_affected=[],
        )
        assert result_with_failure.success is False


class TestSortDataResult:
    """Test SortDataResult model."""

    @pytest.mark.parametrize(
        ("session_id", "sorted_by", "ascending", "rows_processed", "description"),
        [
            ("sort-123", ["department", "salary"], [True, False], 100, "multi-column sort"),
            ("single-sort", ["name"], [True], 50, "single column sort"),
            ("multi-sort", ["dept", "salary", "age"], [True, False, True], 75, "three column sort"),
        ],
    )
    def test_sort_data_result_creation(
        self,
        session_id: str,
        sorted_by: list[str],
        ascending: list[bool],
        rows_processed: int,
        description: str,
    ) -> None:
        """Test SortDataResult creation with various configurations."""
        result = SortDataResult(
            sorted_by=sorted_by,
            ascending=ascending,
            rows_processed=rows_processed,
        )
        assert result.sorted_by == sorted_by
        assert result.ascending == ascending
        assert result.rows_processed == rows_processed
        assert len(result.sorted_by) == len(ascending)

    def test_serialization_roundtrip(self) -> None:
        """Test serialization and deserialization."""
        original = SortDataResult(
            sorted_by=["col1", "col2"],
            ascending=[False, True],
            rows_processed=25,
        )
        data = original.model_dump()
        restored = SortDataResult(**data)
        assert restored == original


# NOTE: SelectColumnsResult model not yet implemented in tool_responses
# Uncomment this test class when the model is available
# class TestSelectColumnsResult:
#     """Test SelectColumnsResult model."""
#
#     def test_valid_creation(self) -> None:
#         """Test valid SelectColumnsResult creation."""
#         result = SelectColumnsResult(
#             session_id="select-123",
#             selected_columns=["name", "age", "salary"],
#             columns_before=10,
#             columns_after=3,
#         )
#         assert result.session_id == "select-123"
#         assert result.selected_columns == ["name", "age", "salary"]
#         assert result.columns_before == 10
#         assert result.columns_after == 3


# # class TestRenameColumnsResult:  # Not yet implemented
#     """Test RenameColumnsResult model."""
#
#     def test_valid_creation(self) -> None:
#         """Test valid RenameColumnsResult creation."""
#         result = RenameColumnsResult(
#             session_id="rename-123",
#             renamed={"old_name": "new_name", "old_age": "new_age"},
#             columns=["new_name", "new_age", "unchanged"],
#         )
#         assert result.session_id == "rename-123"
#         assert result.renamed["old_name"] == "new_name"
#         assert "new_name" in result.columns
#
#     def test_single_rename(self) -> None:
#         """Test renaming single column."""
#         result = RenameColumnsResult(
#             session_id="single-rename",
#             renamed={"old_col": "new_col"},
#             columns=["new_col", "other_col"],
#         )
#         assert len(result.renamed) == 1
#         assert result.renamed["old_col"] == "new_col"
#
#     def test_multiple_renames(self) -> None:
#         """Test renaming multiple columns."""
#         renames = {
#             "first_name": "fname",
#             "last_name": "lname",
#             "email_address": "email",
#         }
#         result = RenameColumnsResult(
#             session_id="multi-rename",
#             renamed=renames,
#             columns=["fname", "lname", "email", "id"],
#         )
#         assert len(result.renamed) == 3
#         assert all(new_name in result.columns for new_name in renames.values())
#
#     def test_empty_rename_map(self) -> None:
#         """Test with no columns renamed."""
#         result = RenameColumnsResult(
#             session_id="no-renames",
#             renamed={},
#             columns=["col1", "col2", "col3"],
#         )
#         assert len(result.renamed) == 0
#         assert len(result.columns) == 3
#
#     def test_serialization_roundtrip(self) -> None:
#         """Test serialization and deserialization."""
#         original = RenameColumnsResult(
#             session_id="serialize-test",
#             renamed={"old": "new"},
#             columns=["new", "other"],
#         )
#         data = original.model_dump()
#         restored = RenameColumnsResult(**data)
#         assert restored == original
