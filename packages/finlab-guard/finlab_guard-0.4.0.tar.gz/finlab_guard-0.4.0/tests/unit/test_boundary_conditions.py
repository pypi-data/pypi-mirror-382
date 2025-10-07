"""Boundary conditions tests for finlab-guard."""

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from finlab_guard.cache.manager import CacheManager
from finlab_guard.core.guard import FinlabGuard


class TestDataSizeBoundaries:
    """Test boundary conditions related to data size."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.guard = FinlabGuard(cache_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()

        with patch.object(self.guard, "_fetch_from_finlab", return_value=empty_df):
            result = self.guard.get("empty_key")
            assert result.empty
            assert result.equals(empty_df)

    def test_single_cell_dataframe(self):
        """Test handling of DataFrame with single cell."""
        single_cell_df = pd.DataFrame({"A": [1]}, index=[pd.Timestamp("2023-01-01")])

        with patch.object(
            self.guard, "_fetch_from_finlab", return_value=single_cell_df
        ):
            result = self.guard.get("single_cell_key")
            pd.testing.assert_frame_equal(result, single_cell_df)

    def test_large_dataframe(self):
        """Test handling of large DataFrame."""
        # Create a large DataFrame (1000 rows x 100 columns)
        dates = pd.date_range("2020-01-01", periods=1000, freq="D")
        columns = [f"col_{i}" for i in range(100)]
        large_df = pd.DataFrame(
            np.random.randn(1000, 100), index=dates, columns=columns
        )

        with patch.object(self.guard, "_fetch_from_finlab", return_value=large_df):
            result = self.guard.get("large_key")
            pd.testing.assert_frame_equal(result, large_df)

    def test_dataframe_with_many_nas(self):
        """Test DataFrame with high percentage of NaN values."""
        # Create DataFrame with 90% NaN values
        df = pd.DataFrame(
            np.random.randn(100, 10),
            index=pd.date_range("2023-01-01", periods=100),
            columns=[f"col_{i}" for i in range(10)],
        )
        # Set 90% of values to NaN
        mask = np.random.random((100, 10)) < 0.9
        df = df.mask(mask)

        with patch.object(self.guard, "_fetch_from_finlab", return_value=df):
            result = self.guard.get("sparse_key")
            pd.testing.assert_frame_equal(result, df)

    def test_dataframe_with_single_column(self):
        """Test DataFrame with only one column."""
        single_col_df = pd.DataFrame(
            {"price": [100.5, 101.2, 99.8, 102.1]},
            index=pd.date_range("2023-01-01", periods=4),
        )

        with patch.object(self.guard, "_fetch_from_finlab", return_value=single_col_df):
            result = self.guard.get("single_col_key")
            pd.testing.assert_frame_equal(result, single_col_df)

    def test_dataframe_with_single_row(self):
        """Test DataFrame with only one row."""
        single_row_df = pd.DataFrame(
            [[1, 2, 3, 4, 5]],
            index=[pd.Timestamp("2023-01-01")],
            columns=["A", "B", "C", "D", "E"],
        )

        with patch.object(self.guard, "_fetch_from_finlab", return_value=single_row_df):
            result = self.guard.get("single_row_key")
            pd.testing.assert_frame_equal(result, single_row_df)


class TestDataTypeBoundaries:
    """Test boundary conditions related to data types."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.guard = FinlabGuard(cache_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extreme_float_values(self):
        """Test handling of extreme float values."""
        extreme_df = pd.DataFrame(
            {
                "small": [np.finfo(np.float64).min, 0.0, np.finfo(np.float64).eps],
                "large": [np.finfo(np.float64).max, 1e308, 1e-308],
                "special": [np.inf, -np.inf, np.nan],
            },
            index=pd.date_range("2023-01-01", periods=3),
        )

        with patch.object(self.guard, "_fetch_from_finlab", return_value=extreme_df):
            result = self.guard.get("extreme_float_key")
            pd.testing.assert_frame_equal(result, extreme_df)

    def test_extreme_int_values(self):
        """Test handling of extreme integer values."""
        extreme_int_df = pd.DataFrame(
            {
                "int64_min": [np.iinfo(np.int64).min],
                "int64_max": [np.iinfo(np.int64).max],
                "zero": [0],
            },
            index=pd.date_range("2023-01-01", periods=1),
        )

        with patch.object(
            self.guard, "_fetch_from_finlab", return_value=extreme_int_df
        ):
            result = self.guard.get("extreme_int_key")
            pd.testing.assert_frame_equal(result, extreme_int_df)

    def test_mixed_data_types(self):
        """Test DataFrame with mixed data types."""
        mixed_df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
                "float_col": [1.1, 2.2, 3.3],
                "str_col": ["a", "b", "c"],
                "bool_col": [True, False, True],
                "datetime_col": pd.date_range("2023-01-01", periods=3),
            },
            index=pd.date_range("2023-01-01", periods=3),
        )

        with patch.object(self.guard, "_fetch_from_finlab", return_value=mixed_df):
            result = self.guard.get("mixed_types_key")
            pd.testing.assert_frame_equal(result, mixed_df)

    def test_string_with_special_characters(self):
        """Test strings with special characters."""
        special_str_df = pd.DataFrame(
            {
                "special_chars": [
                    "normal_string",
                    "string with spaces",
                    "string\nwith\nnewlines",
                    "string\twith\ttabs",
                    'string"with"quotes',
                    "string'with'quotes",
                    "string\\with\\backslashes",
                    "string/with/slashes",
                    "unicode_測試_string",
                    "",  # empty string
                ]
            },
            index=pd.date_range("2023-01-01", periods=10),
        )

        with patch.object(
            self.guard, "_fetch_from_finlab", return_value=special_str_df
        ):
            result = self.guard.get("special_str_key")
            pd.testing.assert_frame_equal(result, special_str_df)

    def test_categorical_dtype_handling(self):
        """Test handling of categorical dtype columns."""
        # Create DataFrame with categorical column
        categorical_df = pd.DataFrame(
            {
                "stock_id": pd.Categorical(["1101", "1102", "1103", "1104"]),
                "name": ["Stock A", "Stock B", "Stock C", "Stock D"],
                "value": [100.0, 200.0, 300.0, 400.0],
            },
            index=pd.date_range("2023-01-01", periods=4),
        )

        # Store initial categorical data
        with patch.object(
            self.guard, "_fetch_from_finlab", return_value=categorical_df
        ):
            result1 = self.guard.get("categorical_key")
            assert result1.shape == categorical_df.shape
            # Verify data is preserved (dtype may be converted to object)
            assert result1["name"].tolist() == categorical_df["name"].tolist()
            assert result1["value"].tolist() == categorical_df["value"].tolist()

        # Test modification with new categorical value
        modified_df = pd.concat(
            [
                categorical_df,
                pd.DataFrame(
                    {
                        "stock_id": ["1105"],
                        "name": ["Stock E"],
                        "value": [500.0],
                    },
                    index=[pd.Timestamp("2023-01-05")],
                ),
            ]
        )

        with patch.object(self.guard, "_fetch_from_finlab", return_value=modified_df):
            result2 = self.guard.get("categorical_key", allow_historical_changes=True)
            assert result2.shape == (5, 3)
            assert "1105" in result2["stock_id"].values


class TestTimeBoundaries:
    """Test boundary conditions related to time handling."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.guard = FinlabGuard(cache_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_timestamp_uniqueness_rapid_succession(self):
        """Test timestamp uniqueness when saving data in rapid succession."""
        df1 = pd.DataFrame({"A": [1]}, index=[pd.Timestamp("2023-01-01")])
        df2 = pd.DataFrame({"A": [1, 2]}, index=pd.date_range("2023-01-01", periods=2))

        with patch.object(self.guard, "_fetch_from_finlab", return_value=df1):
            self.guard.get("rapid_key")

        # Immediately try to save another version
        # Allow historical changes as this test is about timestamp uniqueness, not dtype protection
        with patch.object(self.guard, "_fetch_from_finlab", return_value=df2):
            result = self.guard.get("rapid_key", allow_historical_changes=True)
            pd.testing.assert_frame_equal(result, df2)

        # Verify timestamps are unique
        raw_data = self.guard.cache_manager.load_raw_data("rapid_key")
        timestamps = raw_data["save_time"].unique()
        assert len(timestamps) >= 2  # Should have unique timestamps

    def test_time_context_edge_cases(self):
        """Test time context with edge cases."""
        # Test with time before any data
        very_early_time = datetime(1900, 1, 1)
        self.guard.set_time_context(very_early_time)

        result = self.guard.get("nonexistent_historical_key")
        assert result.empty

        # Test with time far in the future
        very_late_time = datetime(2100, 1, 1)
        self.guard.set_time_context(very_late_time)

        result = self.guard.get("nonexistent_future_key")
        assert result.empty

    def test_datetime_index_boundaries(self):
        """Test with extreme datetime values in index."""
        # Test with very early dates
        early_dates = pd.date_range("1900-01-01", periods=3, freq="D")
        early_df = pd.DataFrame({"A": [1, 2, 3]}, index=early_dates)

        with patch.object(self.guard, "_fetch_from_finlab", return_value=early_df):
            result = self.guard.get("early_dates_key")
            pd.testing.assert_frame_equal(result, early_df)

        # Test with future dates
        future_dates = pd.date_range("2100-01-01", periods=3, freq="D")
        future_df = pd.DataFrame({"A": [4, 5, 6]}, index=future_dates)

        with patch.object(self.guard, "_fetch_from_finlab", return_value=future_df):
            result = self.guard.get("future_dates_key")
            pd.testing.assert_frame_equal(result, future_df)


class TestCacheBoundaries:
    """Test boundary conditions related to cache management."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(
            Path(self.temp_dir), {"compression": "snappy"}
        )

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_key_with_maximum_length(self):
        """Test cache key with long name."""
        # Create a long key name (filesystem safe)
        long_key = "a" * 50  # 50 character key - more conservative

        df = pd.DataFrame(
            {"A": [1, 2, 3]}, index=pd.date_range("2023-01-01", periods=3)
        )
        self.cache_manager.save_data(long_key, df, datetime.now())

        # Verify the cache file exists
        cache_path = self.cache_manager._get_cache_path(long_key)
        assert cache_path.exists(), f"Cache file should exist at {cache_path}"

        result = self.cache_manager.load_data(long_key)
        assert not result.empty, "Result should not be empty"
        assert result.shape == df.shape, (
            f"Expected shape {df.shape}, got {result.shape}"
        )

    def test_many_cache_files(self):
        """Test performance with many cache files."""
        # Create many small cache files
        num_files = 100
        for i in range(num_files):
            key = f"test_key_{i:03d}"
            df = pd.DataFrame({"A": [i]}, index=[pd.Timestamp("2023-01-01")])
            self.cache_manager.save_data(key, df, datetime.now())

        # Verify all can be loaded
        for i in range(num_files):
            key = f"test_key_{i:03d}"
            result = self.cache_manager.load_data(key)
            assert not result.empty
            assert result.iloc[0, 0] == i

    def test_dtype_mapping_with_many_entries(self):
        """Test dtype mapping with many historical entries."""
        key = "dtype_test_key"
        df = pd.DataFrame({"A": [1]}, index=[pd.Timestamp("2023-01-01")])

        # Create many dtype mapping entries by changing dtypes repeatedly
        for i in range(50):
            # Alternate between int64 and float64
            if i % 2 == 0:
                df["A"] = df["A"].astype("int64")
            else:
                df["A"] = df["A"].astype("float64")

            timestamp = datetime.now() + timedelta(seconds=i)
            self.cache_manager._save_dtype_mapping(key, df, timestamp)

        # Verify dtype history has correct number of entries
        dtype_mapping = self.cache_manager._load_dtype_mapping(key)
        assert dtype_mapping is not None
        assert len(dtype_mapping["dtype_history"]) <= 50  # Some may be deduplicated


class TestConfigurationBoundaries:
    """Test boundary conditions related to configuration."""

    def test_initialization_with_extreme_config(self):
        """Test initialization with extreme configuration values."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Test with valid extreme configurations
            extreme_config = {
                "compression": "snappy",  # Valid compression
                "progress_bar": True,  # Valid type
                "log_level": "DEBUG",  # Valid log level
                "custom_param": None,  # None values
                "large_number": 10**20,  # Very large number
                "negative_number": -(10**10),  # Very negative number
            }

            # Should handle gracefully
            guard = FinlabGuard(cache_dir=temp_dir, config=extreme_config)
            assert guard.config["compression"] == "snappy"
            assert guard.config["progress_bar"]
            assert guard.config["log_level"] == "DEBUG"

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cache_dir_special_paths(self):
        """Test cache directory with special path formats."""
        special_paths = [
            "~/test_cache",  # Home directory expansion
            "./relative_cache",  # Relative path
            "../parent_cache",  # Parent directory
            "/tmp/absolute_cache",  # Absolute path
        ]

        for path in special_paths:
            temp_config_dir = None
            try:
                guard = FinlabGuard(cache_dir=path)
                # Should expand and create directory
                assert guard.cache_dir.exists()
                temp_config_dir = guard.cache_dir
            finally:
                if temp_config_dir and temp_config_dir.exists():
                    shutil.rmtree(temp_config_dir, ignore_errors=True)


class TestConcurrencyBoundaries:
    """Test boundary conditions related to concurrent access."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.guard = FinlabGuard(cache_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rapid_consecutive_operations(self):
        """Test rapid consecutive cache operations."""
        df1 = pd.DataFrame({"A": [1]}, index=[pd.Timestamp("2023-01-01")])
        df2 = pd.DataFrame({"A": [1, 2]}, index=pd.date_range("2023-01-01", periods=2))
        df3 = pd.DataFrame(
            {"A": [1, 2, 3]}, index=pd.date_range("2023-01-01", periods=3)
        )

        # Rapid consecutive operations
        # Allow historical changes as this test is about concurrency, not dtype protection
        with patch.object(self.guard, "_fetch_from_finlab", return_value=df1):
            self.guard.get("rapid_key", allow_historical_changes=True)

        with patch.object(self.guard, "_fetch_from_finlab", return_value=df2):
            self.guard.get("rapid_key", allow_historical_changes=True)

        with patch.object(self.guard, "_fetch_from_finlab", return_value=df3):
            result3 = self.guard.get("rapid_key", allow_historical_changes=True)

        # Should handle all operations correctly
        pd.testing.assert_frame_equal(result3, df3)

    def test_multiple_guard_instances_same_cache(self):
        """Test multiple FinlabGuard instances using same cache directory."""
        guard2 = FinlabGuard(cache_dir=self.temp_dir)

        df = pd.DataFrame(
            {"A": [1, 2, 3]}, index=pd.date_range("2023-01-01", periods=3)
        )

        # First guard saves data
        with patch.object(self.guard, "_fetch_from_finlab", return_value=df):
            self.guard.get("shared_key")

        # Second guard should be able to read it
        result = guard2.cache_manager.load_data("shared_key")
        # Verify the data exists and has correct structure
        assert not result.empty
        assert result.shape == df.shape
