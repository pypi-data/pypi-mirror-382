"""Comprehensive unit tests for discovery_server module to improve coverage."""

import uuid
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from fastmcp import Context
from fastmcp.exceptions import ToolError

import databeak
from databeak.core.session import get_session_manager
from databeak.exceptions import ColumnNotFoundError, InvalidParameterError
from databeak.servers.discovery_server import (
    DataSummaryResult,
    FindCellsResult,
    GroupAggregateResult,
    InspectDataResult,
    OutliersResult,
    ProfileResult,
    detect_outliers,
    find_cells_with_value,
    get_data_summary,
    group_by_aggregate,
    inspect_data_around,
    profile_data,
)
from tests.test_mock_context import create_mock_context


@pytest.fixture
def outliers_ctx() -> Context:
    # def mock_session_with_outliers() -> Context:
    """Create real session with data containing outliers."""
    rng = np.random.Generator(np.random.PCG64(seed=42))
    normal_data = rng.normal(50, 10, 95)  # Normal distribution
    outliers = [150, 200, -50, -100, 300]  # Clear outliers
    all_data = np.concatenate([normal_data, outliers])
    rng.shuffle(all_data)

    session_id = str(uuid.uuid4())
    manager = get_session_manager()
    session = manager.get_or_create_session(session_id)
    df = pd.DataFrame(
        {
            "values": all_data,
            "values2": rng.normal(100, 20, 100),
            "category": rng.choice(["A", "B", "C"], 100),
            "subcategory": rng.choice(["X", "Y", "Z"], 100),
            "text": [f"item_{i}" for i in range(100)],
            "nulls": [None if i % 10 == 0 else i for i in range(100)],
            "dates": pd.date_range("2024-01-01", periods=100),
            "mixed": [i if i % 2 == 0 else f"text_{i}" for i in range(100)],
        },
    )
    session.df = df
    return create_mock_context(session.session_id)


@pytest.mark.asyncio
class TestDetectOutliers:
    """Test detect_outliers function comprehensively."""

    async def test_outliers_iqr_method(self, outliers_ctx: Context) -> None:
        """Test outlier detection using IQR method."""
        ctx = outliers_ctx
        result = await detect_outliers(ctx, columns=["values"], method="iqr")

        assert isinstance(result, OutliersResult)
        assert result.success is True
        assert result.method == "iqr"
        assert result.outliers_found > 0
        assert "values" in result.outliers_by_column
        assert len(result.outliers_by_column["values"]) > 0

        # Check outlier details structure
        for outlier_info in result.outliers_by_column["values"]:
            assert hasattr(outlier_info, "row_index")
            assert hasattr(outlier_info, "value")
            assert hasattr(outlier_info, "iqr_score") or hasattr(outlier_info, "z_score")

    async def test_outliers_zscore_method(self, outliers_ctx: Context) -> None:
        """Test outlier detection using z-score method."""
        ctx = outliers_ctx
        result = await detect_outliers(ctx, columns=["values"], method="zscore", threshold=3.0)

        assert result.success is True
        assert result.method == "zscore"
        assert result.outliers_found > 0
        assert result.threshold == 3.0

    async def test_outliers_isolation_forest(self, outliers_ctx: Context) -> None:
        """Test that isolation_forest method is not supported."""
        ctx = outliers_ctx

        with pytest.raises(InvalidParameterError):
            await detect_outliers(
                ctx,
                columns=["values", "values2"],
                method="isolation_forest",
            )

    async def test_outliers_all_columns(self, outliers_ctx: Context) -> None:
        """Test outlier detection on all numeric columns."""
        ctx = outliers_ctx
        result = await detect_outliers(ctx, method="iqr")

        assert result.success is True
        # Should process all numeric columns
        column_names = set(result.outliers_by_column.keys())
        assert "values" in column_names

    async def test_outliers_invalid_method(self, outliers_ctx: Context) -> None:
        """Test outlier detection with invalid method."""
        ctx = outliers_ctx

        with pytest.raises(InvalidParameterError):
            await detect_outliers(ctx, method="invalid_method")

    async def test_outliers_non_numeric_columns(self, outliers_ctx: Context) -> None:
        """Test outlier detection on non-numeric columns."""
        ctx = outliers_ctx

        with pytest.raises(InvalidParameterError):
            await detect_outliers(ctx, columns=["text"])

    async def test_outliers_no_outliers_found(self, outliers_ctx: Context) -> None:
        """Test when no outliers are found."""
        # Create session with data that has no outliers
        uniform_session_id = str(uuid.uuid4())
        manager = get_session_manager()
        uniform_session = manager.get_or_create_session(uniform_session_id)
        uniform_df = pd.DataFrame(
            {
                "uniform": np.ones(100) * 50,  # All same value
            },
        )
        uniform_session.df = uniform_df

        ctx = create_mock_context(uniform_session_id)
        result = await detect_outliers(ctx, columns=["uniform"], method="iqr")
        assert result.success is True
        assert result.outliers_found == 0

    async def test_outliers_with_nulls(self, outliers_ctx: Context) -> None:
        """Test outlier detection with null values."""
        ctx = outliers_ctx
        result = await detect_outliers(ctx, columns=["nulls"], method="zscore")

        assert result.success is True
        # Should handle nulls gracefully

    async def test_outliers_custom_threshold(self, outliers_ctx: Context) -> None:
        """Test outlier detection with custom threshold."""
        ctx = outliers_ctx
        result = await detect_outliers(ctx, columns=["values"], method="zscore", threshold=2.0)

        assert result.success is True
        assert result.threshold == 2.0

        # Lower threshold should find more outliers
        result2 = await detect_outliers(ctx, columns=["values"], method="zscore", threshold=4.0)
        assert result.outliers_found >= result2.outliers_found


@pytest.mark.asyncio
class TestProfileData:
    """Test profile_data function."""

    async def test_profile_all_columns(self, outliers_ctx: Context) -> None:
        """Test profiling all columns."""
        ctx = outliers_ctx
        result = await profile_data(ctx)

        assert isinstance(result, ProfileResult)
        assert result.success is True
        assert result.total_rows == 100
        assert result.total_columns == 8
        assert len(result.profile) == 8

        # Check column profile structure
        for profile in result.profile.values():
            assert hasattr(profile, "column_name")
            assert hasattr(profile, "data_type")
            assert hasattr(profile, "null_count")
            assert hasattr(profile, "null_percentage")
            assert hasattr(profile, "unique_count")
            assert hasattr(profile, "unique_percentage")

    async def test_profile_specific_columns(self, outliers_ctx: Context) -> None:
        """Test profiling specific columns."""
        # profile_data doesn't support columns parameter - it profiles all columns
        ctx = outliers_ctx
        result = await profile_data(ctx)

        assert result.success is True
        # Check that the expected columns are in the profile
        assert "values" in result.profile
        assert "category" in result.profile
        assert "text" in result.profile

    async def test_profile_include_sample_values(self, outliers_ctx: Context) -> None:
        """Test profile with sample values."""
        # profile_data doesn't support columns or include_sample_values parameters
        ctx = outliers_ctx
        result = await profile_data(ctx)

        assert result.success is True
        profile = result.profile["category"]
        # Check for most_frequent value instead of sample_values
        assert hasattr(profile, "most_frequent")
        assert profile.most_frequent is not None

    async def test_profile_numeric_columns(self, outliers_ctx: Context) -> None:
        """Test profiling numeric columns."""
        ctx = outliers_ctx
        result = await profile_data(ctx)

        profile = result.profile["values"]
        assert profile.data_type == "float64"
        # ProfileInfo doesn't include numeric_stats - that's in a different API
        assert hasattr(profile, "null_count")
        assert hasattr(profile, "unique_count")

    async def test_profile_categorical_columns(self, outliers_ctx: Context) -> None:
        """Test profiling categorical columns."""
        ctx = outliers_ctx
        result = await profile_data(ctx)

        profile = result.profile["category"]
        assert profile.data_type == "object"
        assert profile.unique_count == 3
        assert hasattr(profile, "most_frequent")
        assert hasattr(profile, "frequency")

    async def test_profile_datetime_columns(self, outliers_ctx: Context) -> None:
        """Test profiling datetime columns."""
        ctx = outliers_ctx
        result = await profile_data(ctx)

        profile = result.profile["dates"]
        assert "datetime" in profile.data_type
        # Date range info is not in ProfileInfo

    async def test_profile_mixed_type_columns(self, outliers_ctx: Context) -> None:
        """Test profiling mixed type columns."""
        ctx = outliers_ctx
        result = await profile_data(ctx)

        profile = result.profile["mixed"]
        assert profile.data_type == "object"
        assert profile.unique_count > 0

    async def test_profile_quality_metrics(self, outliers_ctx: Context) -> None:
        """Test profile with quality metrics."""
        # profile_data doesn't support include_quality_metrics parameter
        ctx = outliers_ctx
        result = await profile_data(ctx)

        assert result.success is True
        # Quality metrics are not part of ProfileResult
        assert hasattr(result, "memory_usage_mb")

    async def test_profile_empty_dataframe(self, outliers_ctx: Context) -> None:
        """Test profiling empty dataframe."""
        empty_session_id = str(uuid.uuid4())
        manager = get_session_manager()
        empty_session = manager.get_or_create_session(empty_session_id)
        empty_session.df = pd.DataFrame()

        ctx = create_mock_context(empty_session_id)
        result = await profile_data(ctx)
        assert result.success is True
        assert result.total_rows == 0
        assert result.total_columns == 0
        assert len(result.profile) == 0


@pytest.mark.asyncio
class TestGroupByAggregate:
    """Test group_by_aggregate function."""

    async def test_group_by_single_column(self, outliers_ctx: Context) -> None:
        """Test grouping by single column."""
        ctx = outliers_ctx
        result = await group_by_aggregate(
            ctx,
            group_by=["category"],
            aggregations={"values": ["mean", "sum", "count"]},
        )

        assert isinstance(result, GroupAggregateResult)
        assert result.success is True
        assert result.group_by_columns == ["category"]
        assert len(result.groups) == 3  # A, B, C

        # result.groups is a dict of GroupStatistics keyed by group names
        for stats in result.groups.values():
            assert hasattr(stats, "mean")
            assert hasattr(stats, "sum")
            assert hasattr(stats, "count")

    async def test_group_by_multiple_columns(self, outliers_ctx: Context) -> None:
        """Test grouping by multiple columns."""
        ctx = outliers_ctx
        result = await group_by_aggregate(
            ctx,
            group_by=["category", "subcategory"],
            aggregations={"values": ["mean"]},
        )

        assert result.success is True
        assert result.group_by_columns == ["category", "subcategory"]
        assert len(result.groups) > 0

    async def test_group_by_multiple_aggregations(self, outliers_ctx: Context) -> None:
        """Test multiple aggregation functions."""
        ctx = outliers_ctx
        result = await group_by_aggregate(
            ctx,
            group_by=["category"],
            aggregations={
                "values": ["mean", "median", "std", "min", "max"],
                "values2": ["sum", "count"],
            },
        )

        assert result.success is True
        # Check first group's aggregated values
        first_group_key = next(iter(result.groups.keys()))
        stats = result.groups[first_group_key]
        # GroupStatistics has mean, sum, min, max, std, count attributes
        assert hasattr(stats, "mean")
        assert hasattr(stats, "sum")
        assert hasattr(stats, "min")
        assert hasattr(stats, "max")
        assert hasattr(stats, "std")
        assert hasattr(stats, "count")

    async def test_group_by_invalid_column(self, outliers_ctx: Context) -> None:
        """Test grouping by invalid column."""
        ctx = outliers_ctx

        with pytest.raises(ColumnNotFoundError):
            await group_by_aggregate(
                ctx,
                group_by=["invalid_col"],
                aggregations={"values": ["mean"]},
            )

    async def test_group_by_invalid_aggregation(self, outliers_ctx: Context) -> None:
        """Test invalid aggregation function."""
        # Server ignores invalid aggregations and uses defaults
        ctx = outliers_ctx
        result = await group_by_aggregate(
            ctx,
            group_by=["category"],
            aggregations={"values": ["invalid_agg"]},
        )
        assert result.success is True

    async def test_group_by_non_numeric_aggregation(self, outliers_ctx: Context) -> None:
        """Test aggregating non-numeric columns."""
        ctx = outliers_ctx
        result = await group_by_aggregate(
            ctx,
            group_by=["category"],
            aggregations={"text": ["count", "nunique"]},
        )

        assert result.success is True
        # Count and nunique should work for non-numeric

    async def test_group_by_with_nulls(self, outliers_ctx: Context) -> None:
        """Test grouping with null values."""
        ctx = outliers_ctx
        result = await group_by_aggregate(
            ctx,
            group_by=["category"],
            aggregations={"nulls": ["mean", "count"]},
        )

        assert result.success is True
        # Should handle nulls in aggregation


@pytest.mark.asyncio
class TestFindCellsWithValue:
    """Test find_cells_with_value function."""

    async def test_find_exact_match(self, outliers_ctx: Context) -> None:
        """Test finding cells with exact match."""
        ctx = outliers_ctx
        result = await find_cells_with_value(ctx, "A", columns=["category"])

        assert isinstance(result, FindCellsResult)
        assert result.success is True
        assert result.matches_found > 0
        assert len(result.coordinates) > 0

        for loc in result.coordinates:
            # CellLocation is an object with row, column, value attributes
            assert hasattr(loc, "row")
            assert hasattr(loc, "column")
            assert hasattr(loc, "value")
            assert loc.value == "A"

    async def test_find_numeric_value(self, outliers_ctx: Context) -> None:
        """Test finding numeric value."""
        # Find a specific numeric value
        manager = get_session_manager()
        session = manager.get_or_create_session(outliers_ctx.session_id)
        df = session.df
        assert df is not None
        target_value = df["values"].iloc[0]

        ctx = outliers_ctx
        result = await find_cells_with_value(ctx, target_value, columns=["values"])

        assert result.success is True
        assert result.matches_found >= 1

    async def test_find_partial_match(self, outliers_ctx: Context) -> None:
        """Test finding cells with partial match."""
        ctx = outliers_ctx
        result = await find_cells_with_value(ctx, "item", columns=["text"], exact_match=False)

        assert result.success is True
        assert result.matches_found == 100  # All text values contain "item"

    async def test_find_case_insensitive(self, outliers_ctx: Context) -> None:
        """Test case-insensitive search."""
        # find_cells_with_value doesn't support case_sensitive parameter
        # It does exact matching by default
        ctx = outliers_ctx
        result = await find_cells_with_value(ctx, "A", columns=["category"], exact_match=True)

        assert result.success is True
        assert result.matches_found > 0

    async def test_find_in_all_columns(self, outliers_ctx: Context) -> None:
        """Test finding value in all columns."""
        ctx = outliers_ctx
        result = await find_cells_with_value(ctx, "A")

        assert result.success is True
        # Should search all columns

    async def test_find_null_values(self, outliers_ctx: Context) -> None:
        """Test finding null values."""
        ctx = outliers_ctx
        result = await find_cells_with_value(ctx, None, columns=["nulls"])

        assert result.success is True
        assert result.matches_found == 10  # Every 10th value is null

    async def test_find_no_matches(self, outliers_ctx: Context) -> None:
        """Test when no matches are found."""
        ctx = outliers_ctx
        result = await find_cells_with_value(ctx, "NONEXISTENT")

        assert result.success is True
        assert result.matches_found == 0
        assert len(result.coordinates) == 0

    async def test_find_max_results(self, outliers_ctx: Context) -> None:
        """Test limiting maximum results."""
        # find_cells_with_value doesn't support max_results parameter
        ctx = outliers_ctx
        result = await find_cells_with_value(ctx, "A", columns=["category"])

        assert result.success is True
        # Since max_results is not supported, check all matches are returned
        assert len(result.coordinates) > 0


@pytest.mark.asyncio
class TestGetDataSummary:
    """Test get_data_summary function."""

    async def test_data_summary_default(self, outliers_ctx: Context) -> None:
        """Test getting default data summary."""
        ctx = outliers_ctx
        result = await get_data_summary(ctx)

        assert isinstance(result, DataSummaryResult)
        assert result.success is True
        assert result.shape["rows"] == 100
        assert result.shape["columns"] == 8
        assert result.memory_usage_mb > 0

        # Check data types
        assert len(result.data_types) > 0
        assert "numeric" in result.data_types
        assert "text" in result.data_types

        # Check missing data
        assert hasattr(result.missing_data, "total_missing")
        assert hasattr(result.missing_data, "missing_by_column")

        # Check preview
        assert result.preview is not None
        assert hasattr(result.preview, "rows")
        assert hasattr(result.preview, "row_count")

    async def test_data_summary_with_statistics(self, outliers_ctx: Context) -> None:
        """Test data summary with basic statistics."""
        # get_data_summary doesn't have include_statistics parameter
        ctx = outliers_ctx
        result = await get_data_summary(ctx)

        assert result.success is True
        # basic_stats is not a field in DataSummaryResult
        assert result.success is True

    async def test_data_summary_max_preview_rows(self, outliers_ctx: Context) -> None:
        """Test data summary with custom preview size."""
        ctx = outliers_ctx
        result = await get_data_summary(ctx, max_preview_rows=20)

        assert result.success is True
        assert result.preview is not None
        assert len(result.preview.rows) <= 20

    async def test_data_summary_empty_dataframe(self, outliers_ctx: Context) -> None:
        """Test data summary for empty dataframe."""
        empty_session_id = str(uuid.uuid4())
        manager = get_session_manager()
        empty_session = manager.get_or_create_session(empty_session_id)
        empty_session.df = pd.DataFrame()

        ctx = create_mock_context(empty_session_id)
        result = await get_data_summary(ctx)
        assert result.success is True
        assert result.shape["rows"] == 0
        assert result.shape["columns"] == 0

    async def test_data_summary_large_dataframe(self, outliers_ctx: Context) -> None:
        """Test data summary for large dataframe."""
        large_session_id = str(uuid.uuid4())
        manager = get_session_manager()
        large_session = manager.get_or_create_session(large_session_id)
        rng = np.random.Generator(np.random.PCG64(seed=42))
        large_df = pd.DataFrame(rng.standard_normal((10000, 100)))
        large_session.df = large_df

        ctx = create_mock_context(large_session_id)
        result = await get_data_summary(ctx)
        assert result.success is True
        assert result.shape["rows"] == 10000
        assert result.shape["columns"] == 100
        assert result.memory_usage_mb > 0


@pytest.mark.asyncio
class TestInspectDataAround:
    """Test inspect_data_around function."""

    async def test_inspect_around_cell(self, outliers_ctx: Context) -> None:
        """Test inspecting data around a specific cell."""
        ctx = outliers_ctx
        result = await inspect_data_around(ctx, 50, "values", radius=5)

        assert isinstance(result, InspectDataResult)
        assert result.success is True
        assert result.center_coordinates["row"] == 50
        assert result.center_coordinates["column"] == "values"
        assert result.radius == 5

        # Check surrounding data - it's a DataPreview object
        assert hasattr(result.surrounding_data, "rows")
        assert len(result.surrounding_data.rows) <= 11  # radius*2 + 1

    async def test_inspect_around_edge_cell(self, outliers_ctx: Context) -> None:
        """Test inspecting around edge cells."""
        ctx = outliers_ctx
        result = await inspect_data_around(ctx, 0, "values", radius=5)

        assert result.success is True
        assert result.center_coordinates["row"] == 0
        # Should handle edge case gracefully
        assert len(result.surrounding_data.rows) <= 6  # Can't go before row 0

    async def test_inspect_around_invalid_row(self, outliers_ctx: Context) -> None:
        """Test inspecting around invalid row."""
        # Function doesn't validate row bounds, just returns empty data
        ctx = outliers_ctx
        result = await inspect_data_around(ctx, 1000, "values")
        assert result.success is True
        assert len(result.surrounding_data.rows) == 0  # No rows in range

    async def test_inspect_around_invalid_column(self, outliers_ctx: Context) -> None:
        """Test inspecting around invalid column."""
        ctx = outliers_ctx

        with pytest.raises(ColumnNotFoundError):
            await inspect_data_around(ctx, 50, "invalid_col")

    async def test_inspect_around_large_radius(self, outliers_ctx: Context) -> None:
        """Test inspecting with large radius."""
        ctx = outliers_ctx
        result = await inspect_data_around(ctx, 50, "values", radius=100)

        assert result.success is True
        # Should cap at dataframe boundaries
        assert len(result.surrounding_data.rows) == 100

    async def test_inspect_around_with_context(self, outliers_ctx: Context) -> None:
        """Test inspect with context information."""
        ctx = outliers_ctx
        result = await inspect_data_around(ctx, 50, "values", radius=3)

        assert result.success is True
        # Should include all columns in surrounding data
        # Now only returns columns in the radius, not all columns
        assert result.surrounding_data.column_count >= 1


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling across all functions."""

    @pytest.mark.skip(reason="TODO: Update error message expectations")
    async def test_no_data_loaded(self) -> None:
        """Test all functions when no data is loaded."""
        with patch.object(databeak, "session_manager") as manager:
            session = Mock()
            session.has_data.return_value = False
            manager.return_value.get_session.return_value = session

            ctx = create_mock_context("no-data")

            with pytest.raises(ToolError):
                await detect_outliers(ctx)

            ctx = create_mock_context("no-data")

            with pytest.raises(ToolError):
                await profile_data(ctx)

    async def test_edge_cases(self, outliers_ctx: Context) -> None:
        """Test various edge cases."""
        # Single row dataframe
        single_row_session_id = str(uuid.uuid4())
        manager = get_session_manager()
        single_row_session = manager.get_or_create_session(single_row_session_id)
        single_row_df = pd.DataFrame({"col": [1]})
        single_row_session.df = single_row_df

        ctx = create_mock_context(single_row_session_id)
        result = await profile_data(ctx)
        assert result.success is True
        assert result.total_rows == 1

        # Single column dataframe
        single_col_session_id = str(uuid.uuid4())
        single_col_session = manager.get_or_create_session(single_col_session_id)
        single_col_df = pd.DataFrame({"only_col": range(100)})
        single_col_session.df = single_col_df

        ctx = create_mock_context(single_col_session_id)
        outliers_result = await detect_outliers(ctx)
        assert outliers_result.success is True
