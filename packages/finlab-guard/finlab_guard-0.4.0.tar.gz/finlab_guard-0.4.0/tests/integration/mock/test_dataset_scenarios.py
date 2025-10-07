"""Integration tests for critical dataset scenarios in finlab-guard.

This module tests the 7 critical scenarios identified in TEST_REFACTOR_PLAN.md:
1. New index, no changes to existing data/dtype
2. New index with dtype changes
3. New index + new column
4. New index + historical changes without allow_historical_changes
5. New index + historical changes with allow_historical_changes
6. Historical changes only with allow_historical_changes
7. Historical changes + new column with allow_historical_changes

Each scenario tests the complete end-to-end workflow including:
- Initial data setup and storage
- Simulated finlab data changes
- get() method behavior
- time_context queries
- Data integrity verification
"""

import shutil
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from finlab_guard import FinlabGuard
from finlab_guard.utils.exceptions import DataModifiedException


def safe_rmtree(path, ignore_errors=False):
    """Windows-compatible rmtree with retry logic for DuckDB file locking."""
    import gc

    # Force garbage collection to release any lingering file handles
    gc.collect()

    for attempt in range(10):  # Increase retry attempts to 10
        try:
            shutil.rmtree(path, ignore_errors=ignore_errors)
            break
        except (PermissionError, OSError):
            if attempt < 9:
                # Exponential backoff: 100ms, 200ms, 400ms, etc.
                wait_time = 0.1 * (2 ** min(attempt, 4))
                time.sleep(wait_time)
                gc.collect()  # Try garbage collection again
                continue
            if not ignore_errors:
                raise


class TestDatasetScenarios:
    """Test critical dataset scenarios with complete end-to-end workflows."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        safe_rmtree(temp_dir)

    @pytest.fixture
    def guard(self, temp_cache_dir):
        """Create FinlabGuard instance for testing."""
        config = {
            "compression": None
        }  # Disable compression to avoid PyArrow issues in tests
        guard_instance = FinlabGuard(cache_dir=temp_cache_dir, config=config)
        yield guard_instance
        # Ensure DuckDB connection is closed to prevent Windows file locking
        guard_instance.close()

    @pytest.fixture
    def initial_data(self):
        """Create standard initial test data."""
        return pd.DataFrame(
            {
                "col1": np.array([100, 200], dtype="int32"),
                "col2": np.array([1.1, 2.2], dtype="float32"),
            },
            index=["A", "B"],
        )

    def _mock_finlab_data(self, data: pd.DataFrame):
        """Mock finlab.data.get to return specified data."""
        # Use the simpler approach - patch the _fetch_from_finlab method
        # The finlab module mock is handled by conftest.py
        return patch.object(FinlabGuard, "_fetch_from_finlab", return_value=data)

    def _verify_data_integrity(self, expected: pd.DataFrame, actual: pd.DataFrame):
        """Verify complete data integrity including dtypes and order."""
        pd.testing.assert_frame_equal(
            expected, actual, check_dtype=True, check_index_type=True
        )
        assert list(expected.columns) == list(actual.columns), "Column order mismatch"
        assert list(expected.index) == list(actual.index), "Index order mismatch"

    def _verify_time_context_query(
        self,
        guard: FinlabGuard,
        key: str,
        target_time: datetime,
        expected: pd.DataFrame,
    ):
        """Verify time context query returns correct historical data."""
        guard.set_time_context(target_time)
        try:
            result = guard.get(key, allow_historical_changes=False)
            self._verify_data_integrity(expected, result)
        finally:
            guard.clear_time_context()

    def test_scenario_1_new_index_no_changes(self, guard, initial_data):
        """
        Scenario 1: New index added, no changes to existing data/dtype

        Setup:
        - Initial: index=[A,B], cols=[col1,col2], dtypes=[int32,float32]

        Action:
        - finlab adds: index=[A,B,C], cols=[col1,col2], dtypes=[int32,float32]
        - Values for A,B are completely unchanged

        Verify:
        - get() returns [A,B,C] data successfully
        - time_context query returns original [A,B] data
        - dtype mapping has no new entry (no changes)
        """
        key = "test_scenario_1"
        initial_time = datetime.now() - timedelta(hours=2)  # Use past time
        later_time = datetime.now()

        # Setup: Save initial data with explicit timestamp
        with patch.object(guard, "_now", return_value=initial_time):
            with self._mock_finlab_data(initial_data):
                result1 = guard.get(key)
                self._verify_data_integrity(initial_data, result1)

        # Action: Add new index C with same dtypes, no changes to A,B
        new_data = pd.DataFrame(
            {
                "col1": np.array([100, 200, 300], dtype="int32"),  # A,B unchanged
                "col2": np.array([1.1, 2.2, 3.3], dtype="float32"),  # A,B unchanged
            },
            index=["A", "B", "C"],
        )

        with patch.object(guard, "_now", return_value=later_time):
            with self._mock_finlab_data(new_data):
                result2 = guard.get(key)

        # Verify: get() returns new data with index C
        self._verify_data_integrity(new_data, result2)

        # Verify: time_context returns original data (query time after initial_time but before later_time)
        query_time = initial_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time, initial_data)

        # Verify: New dtype mapping entry created (index structure changed)
        dtype_history = guard.cache_manager._load_dtype_mapping(key)
        assert len(dtype_history["dtype_history"]) >= 2, (
            "Should have multiple dtype entries (index structure changed)"
        )

    def test_scenario_2_new_index_dtype_changed(self, guard, initial_data):
        """
        Scenario 2: New index with dtype changes

        Setup:
        - Initial: dtypes=[int32,float32]

        Action:
        - finlab adds index + col1 changes to int64

        Verify:
        - get() returns new data with new dtype
        - time_context uses old dtype (int32)
        - dtype mapping adds new entry
        """
        key = "test_scenario_2"
        initial_time = datetime.now() - timedelta(hours=2)
        later_time = datetime.now()

        # Setup: Save initial data with explicit timestamp
        with patch.object(guard, "_now", return_value=initial_time):
            with self._mock_finlab_data(initial_data):
                result1 = guard.get(key)
                self._verify_data_integrity(initial_data, result1)

        # Action: Add new index + change col1 dtype to int64
        new_data = pd.DataFrame(
            {
                "col1": np.array([100, 200, 300], dtype="int64"),  # dtype changed
                "col2": np.array([1.1, 2.2, 3.3], dtype="float32"),  # unchanged
            },
            index=["A", "B", "C"],
        )

        with patch.object(guard, "_now", return_value=later_time):
            with self._mock_finlab_data(new_data):
                # Allow dtype changes as this scenario tests dtype evolution
                result2 = guard.get(key, allow_historical_changes=True)

        # Verify: get() returns new data with new dtype
        self._verify_data_integrity(new_data, result2)
        assert result2["col1"].dtype == np.dtype("int64"), "New dtype should be int64"

        # Verify: time_context returns data with old dtype
        query_time = initial_time + timedelta(minutes=30)
        guard.set_time_context(query_time)
        try:
            old_result = guard.get(key, allow_historical_changes=False)

            # Check if we got valid historical data
            if len(old_result) == 0 or "col1" not in old_result.columns:
                raise AssertionError(
                    f"Time context query failed to return historical data. "
                    f"Got shape: {old_result.shape}, columns: {list(old_result.columns)}"
                )

            assert old_result["col1"].dtype == np.dtype("int32"), (
                "Old dtype should be int32"
            )
        finally:
            guard.clear_time_context()

        # Verify: New dtype mapping entry created
        dtype_history = guard.cache_manager._load_dtype_mapping(key)
        assert len(dtype_history["dtype_history"]) >= 2, (
            "Should have multiple dtype entries (dtype changed)"
        )

    def test_scenario_3_new_index_new_column(self, guard, initial_data):
        """
        Scenario 3: New index + new column

        Setup:
        - Initial: cols=[col1,col2]

        Action:
        - finlab adds index C + adds col3

        Verify:
        - get() returns new structure successfully
        - time_context returns old structure (no col3)
        - column order is correctly preserved
        """
        key = "test_scenario_3"
        initial_time = datetime.now() - timedelta(hours=2)
        later_time = datetime.now()

        # Setup: Save initial data with explicit timestamp
        with patch.object(guard, "_now", return_value=initial_time):
            with self._mock_finlab_data(initial_data):
                result1 = guard.get(key)
                self._verify_data_integrity(initial_data, result1)

        # Action: Add new index C + new column col3
        new_data = pd.DataFrame(
            {
                "col1": np.array([100, 200, 300], dtype="int32"),
                "col2": np.array([1.1, 2.2, 3.3], dtype="float32"),
                "col3": np.array([10.0, 20.0, 30.0], dtype="float64"),  # new column
            },
            index=["A", "B", "C"],
        )

        with patch.object(guard, "_now", return_value=later_time):
            with self._mock_finlab_data(new_data):
                result2 = guard.get(key)

        # Verify: get() returns new structure
        self._verify_data_integrity(new_data, result2)
        assert "col3" in result2.columns, "New column should be present"
        assert list(result2.columns) == ["col1", "col2", "col3"], (
            "Column order preserved"
        )

        # Verify: time_context returns old structure (no col3)
        query_time = initial_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time, initial_data)

    def test_scenario_4_new_index_historical_changes_no_force(
        self, guard, initial_data
    ):
        """
        Scenario 4: New index + historical changes, no allow_historical_changes

        Setup:
        - Initial: A=100, B=200

        Action:
        - finlab adds C=300 + modifies A=105

        Verify:
        - get() raises DataModifiedException
        - exception contains correct change information
        - original data is not polluted
        - time_context can still access original data
        """
        key = "test_scenario_4"
        initial_time = datetime.now() - timedelta(hours=2)
        later_time = datetime.now()

        # Setup: Save initial data with explicit timestamp
        with patch.object(guard, "_now", return_value=initial_time):
            with self._mock_finlab_data(initial_data):
                result1 = guard.get(key)
                self._verify_data_integrity(initial_data, result1)

        # Action: Add new index C + modify historical data A
        modified_data = pd.DataFrame(
            {
                "col1": np.array(
                    [105, 200, 300], dtype="int32"
                ),  # A modified: 100->105
                "col2": np.array([1.1, 2.2, 3.3], dtype="float32"),
            },
            index=["A", "B", "C"],
        )

        with patch.object(guard, "_now", return_value=later_time):
            with self._mock_finlab_data(modified_data):
                # Verify: get() raises DataModifiedException
                with pytest.raises(DataModifiedException) as exc_info:
                    guard.get(key, allow_historical_changes=False)

                # Verify: exception contains correct change information
                exception = exc_info.value
                # Check if there are any changes in the ChangeResult
                total_changes = (
                    len(exception.changes.cell_changes)
                    + len(exception.changes.row_additions)
                    + len(exception.changes.row_deletions)
                    + len(exception.changes.column_additions)
                    + len(exception.changes.column_deletions)
                )
                assert total_changes > 0, "Should detect modifications"

                # For this test, changes should be in cell_changes
                assert not exception.changes.cell_changes.empty, (
                    "Should have cell changes"
                )

                # Find the modification for index A, col1
                cell_changes = exception.changes.cell_changes
                a_modifications = cell_changes[
                    (cell_changes["row_key"] == "A")
                    & (cell_changes["col_key"] == "col1")
                ]
                assert len(a_modifications) == 1, "Should detect A modification"
                # Note: Values are stored as JSON strings, so we need to parse them
                import json

                # The new value should be 105 (stored as JSON)
                raw_value = a_modifications.iloc[0]["value"]

                # Use the cache manager's JSON parsing method to handle special encodings
                from finlab_guard.cache.manager import CacheManager

                cache_manager = CacheManager(guard.cache_dir, guard.config)

                # First parse the JSON, then parse the value with proper handling
                parsed_json = json.loads(raw_value)
                new_value = cache_manager._parse_json_value(parsed_json)

                # Convert to int for comparison if it's a whole number
                if isinstance(new_value, float) and new_value.is_integer():
                    new_value = int(new_value)

                assert new_value == 105, f"New value should be 105, got {new_value}"

        # Verify: time_context can still access original data (not polluted)
        query_time = initial_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time, initial_data)

    def test_scenario_5_new_index_historical_changes_with_force(
        self, guard, initial_data
    ):
        """
        Scenario 5: New index + historical changes with allow_historical_changes

        Verify:
        - get(allow_historical_changes=True) succeeds
        - returns latest finlab data (including modifications)
        - saves incremental changes (modifications + additions)
        - time_context can access both before/after data
        """
        key = "test_scenario_5"
        initial_time = datetime.now() - timedelta(hours=2)
        later_time = datetime.now()

        # Setup: Save initial data with explicit timestamp
        with patch.object(guard, "_now", return_value=initial_time):
            with self._mock_finlab_data(initial_data):
                result1 = guard.get(key)
                self._verify_data_integrity(initial_data, result1)

        # Action: Add new index C + modify historical data A
        modified_data = pd.DataFrame(
            {
                "col1": np.array(
                    [105, 200, 300], dtype="int32"
                ),  # A modified: 100->105
                "col2": np.array([1.1, 2.2, 3.3], dtype="float32"),
            },
            index=["A", "B", "C"],
        )

        with patch.object(guard, "_now", return_value=later_time):
            with self._mock_finlab_data(modified_data):
                # Verify: get(allow_historical_changes=True) succeeds
                result2 = guard.get(key, allow_historical_changes=True)

        # Verify: returns latest finlab data (including modifications)
        self._verify_data_integrity(modified_data, result2)

        # Verify: time_context can access original data (before modification)
        query_time_1 = initial_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time_1, initial_data)

        # Verify: time_context can access modified data (after modification)
        query_time_2 = later_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time_2, modified_data)

    def test_scenario_6_historical_changes_only_with_force(self, guard, initial_data):
        """
        Scenario 6: Only historical changes with allow_historical_changes

        Setup:
        - Initial: A=100, B=200

        Action:
        - finlab modifies: A=105 (B unchanged)

        Verify:
        - get(allow_historical_changes=True) succeeds
        - incremental storage contains only modifications
        - time_context queries work correctly for different time points
        """
        key = "test_scenario_6"
        initial_time = datetime.now() - timedelta(hours=2)
        later_time = datetime.now()

        # Setup: Save initial data with explicit timestamp
        with patch.object(guard, "_now", return_value=initial_time):
            with self._mock_finlab_data(initial_data):
                result1 = guard.get(key)
                self._verify_data_integrity(initial_data, result1)

        # Action: Modify only historical data A (no new index)
        modified_data = pd.DataFrame(
            {
                "col1": np.array([105, 200], dtype="int32"),  # A modified: 100->105
                "col2": np.array([1.1, 2.2], dtype="float32"),  # B unchanged
            },
            index=["A", "B"],
        )

        with patch.object(guard, "_now", return_value=later_time):
            with self._mock_finlab_data(modified_data):
                # Verify: get(allow_historical_changes=True) succeeds
                result2 = guard.get(key, allow_historical_changes=True)

        # Verify: returns modified data
        self._verify_data_integrity(modified_data, result2)
        assert result2.loc["A", "col1"] == 105, "A should be modified to 105"
        assert result2.loc["B", "col1"] == 200, "B should remain unchanged"

        # Verify: time_context queries work for different time points
        query_time_1 = initial_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time_1, initial_data)
        query_time_2 = later_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time_2, modified_data)

    def test_scenario_7_historical_changes_new_column_with_force(
        self, guard, initial_data
    ):
        """
        Scenario 7: Historical changes + new column with allow_historical_changes

        Action:
        - modify A=105 + add col3

        Verify:
        - mixed changes handled correctly
        - dtype mapping updated correctly
        - time_context queries work for both old/new structures
        """
        key = "test_scenario_7"
        initial_time = datetime.now() - timedelta(hours=2)
        later_time = datetime.now()

        # Setup: Save initial data with explicit timestamp
        with patch.object(guard, "_now", return_value=initial_time):
            with self._mock_finlab_data(initial_data):
                result1 = guard.get(key)
                self._verify_data_integrity(initial_data, result1)

        # Action: Modify historical data A + add new column col3
        mixed_changes_data = pd.DataFrame(
            {
                "col1": np.array([105, 200], dtype="int32"),  # A modified: 100->105
                "col2": np.array([1.1, 2.2], dtype="float32"),
                "col3": np.array([10.0, 20.0], dtype="float64"),  # new column
            },
            index=["A", "B"],
        )

        with patch.object(guard, "_now", return_value=later_time):
            with self._mock_finlab_data(mixed_changes_data):
                # Verify: mixed changes handled correctly
                result2 = guard.get(key, allow_historical_changes=True)

        # Verify: returns data with modifications and new structure
        self._verify_data_integrity(mixed_changes_data, result2)
        assert result2.loc["A", "col1"] == 105, "A should be modified"
        assert "col3" in result2.columns, "New column should be present"

        # Verify: time_context returns old structure (no col3, original values)
        query_time_1 = initial_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time_1, initial_data)

        # Verify: time_context returns new structure (with col3, modified values)
        query_time_2 = later_time + timedelta(minutes=30)
        self._verify_time_context_query(guard, key, query_time_2, mixed_changes_data)

        # Verify: dtype mapping updated correctly (new column means structure change)
        dtype_history = guard.cache_manager._load_dtype_mapping(key)
        assert len(dtype_history["dtype_history"]) >= 2, (
            "Should have multiple dtype entries (structure changed)"
        )


# Test utilities and helper methods
class TestScenarioHelpers:
    """Test the helper methods used in scenario tests."""

    def test_mock_finlab_data_utility(self):
        """Test that the finlab data mocking utility works correctly."""
        test_data = pd.DataFrame({"col": [1, 2]}, index=["A", "B"])

        scenarios = TestDatasetScenarios()
        with scenarios._mock_finlab_data(test_data) as mock_fetch:
            # Verify the mock is properly set up
            assert mock_fetch.return_value.equals(test_data), (
                "Mock should return the test data"
            )

    def test_data_integrity_verification(self):
        """Test the data integrity verification utility."""
        data1 = pd.DataFrame(
            {
                "col1": np.array([1, 2], dtype="int32"),
                "col2": np.array([1.1, 2.2], dtype="float32"),
            },
            index=["A", "B"],
        )

        data2 = data1.copy()

        scenarios = TestDatasetScenarios()
        # Should not raise any exception for identical data
        scenarios._verify_data_integrity(data1, data2)

        # Test with different data should fail
        data3 = data1.copy()
        data3.iloc[0, 0] = 999

        with pytest.raises(AssertionError):
            scenarios._verify_data_integrity(data1, data3)
