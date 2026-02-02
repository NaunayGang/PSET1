"""
Tests for algorithm.py module.

Tests the route optimization algorithm functions.
"""

import pytest
import pandas as pd
import numpy as np
from app.algorithm import (
    compute_top_routes,
    optimize_route_selection,
    validate_route_pair,
)


class TestComputeTopRoutes:
    """Test suite for compute_top_routes function."""

    def test_compute_top_routes_basic(self):
        """Test basic functionality of compute_top_routes."""
        # Create test dataframe
        data = {
            'PULocationID': [1, 1, 2, 2, 3, 1, 2],
            'DOLocationID': [2, 3, 3, 1, 1, 2, 3]
        }
        df = pd.DataFrame(data)

        result = compute_top_routes(df, limit_rows=100, top_n_routes=5)

        # Should return list of tuples (pickup, dropoff, frequency)
        assert isinstance(result, list)
        assert len(result) <= 5

        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 3
            assert isinstance(item[0], (int, np.integer))  # pickup_zone_id
            assert isinstance(item[1], (int, np.integer))  # dropoff_zone_id
            assert isinstance(item[2], (int, np.integer))  # frequency

    def test_compute_top_routes_sorted_by_frequency(self):
        """Test that results are sorted by frequency descending."""
        # Create test dataframe with known frequencies
        data = {
            'PULocationID': [1, 1, 1, 2, 2, 3],  # 1->2 appears 3 times, 2->3 appears 2 times, 3->1 appears 1 time
            'DOLocationID': [2, 2, 2, 3, 3, 1]
        }
        df = pd.DataFrame(data)

        result = compute_top_routes(df, limit_rows=100, top_n_routes=5)

        # First result should be the most frequent
        assert result[0][2] >= result[1][2]  # frequency decreases

    def test_compute_top_routes_missing_columns(self):
        """Test that missing required columns raise ValueError."""
        # DataFrame missing PULocationID
        df = pd.DataFrame({'DOLocationID': [1, 2, 3]})

        with pytest.raises(ValueError, match="DataFrame must contain 'PULocationID' and 'DOLocationID' columns"):
            compute_top_routes(df)

        # DataFrame missing DOLocationID
        df = pd.DataFrame({'PULocationID': [1, 2, 3]})

        with pytest.raises(ValueError, match="DataFrame must contain 'PULocationID' and 'DOLocationID' columns"):
            compute_top_routes(df)

    def test_compute_top_routes_limit_rows(self):
        """Test that limit_rows parameter works."""
        # Create large dataframe
        data = {
            'PULocationID': list(range(100)),
            'DOLocationID': list(range(1, 101))
        }
        df = pd.DataFrame(data)

        result = compute_top_routes(df, limit_rows=10, top_n_routes=5)

        # Should only process first 10 rows
        # Since each row has unique pairs, should get up to 5 unique pairs
        assert len(result) <= 5

    def test_compute_top_routes_top_n_limit(self):
        """Test that top_n_routes limits the output."""
        # Create dataframe with many unique pairs
        data = {
            'PULocationID': list(range(20)),
            'DOLocationID': list(range(1, 21))
        }
        df = pd.DataFrame(data)

        result = compute_top_routes(df, limit_rows=100, top_n_routes=5)

        assert len(result) <= 5


class TestOptimizeRouteSelection:
    """Test suite for optimize_route_selection function."""

    def test_optimize_route_selection_no_existing(self):
        """Test with no existing routes - all should be returned."""
        routes = [(1, 2, 10), (2, 3, 8), (3, 4, 6)]
        existing_routes = set()

        result = optimize_route_selection(routes, existing_routes)

        assert result == routes

    def test_optimize_route_selection_some_existing(self):
        """Test with some existing routes - should filter out existing ones."""
        routes = [(1, 2, 10), (2, 3, 8), (3, 4, 6)]
        existing_routes = {(1, 2), (3, 4)}  # (1,2) and (3,4) already exist

        result = optimize_route_selection(routes, existing_routes)

        expected = [(2, 3, 8)]  # Only (2,3) should remain
        assert result == expected

    def test_optimize_route_selection_all_existing(self):
        """Test with all routes existing - should return empty list."""
        routes = [(1, 2, 10), (2, 3, 8)]
        existing_routes = {(1, 2), (2, 3)}

        result = optimize_route_selection(routes, existing_routes)

        assert result == []

    def test_optimize_route_selection_empty_input(self):
        """Test with empty input routes."""
        routes = []
        existing_routes = {(1, 2)}

        result = optimize_route_selection(routes, existing_routes)

        assert result == []


class TestValidateRoutePair:
    """Test suite for validate_route_pair function."""

    def test_validate_route_pair_valid(self):
        """Test valid route pairs."""
        assert validate_route_pair(1, 2) is True
        assert validate_route_pair(100, 200) is True
        assert validate_route_pair(999, 1000) is True

    def test_validate_route_pair_same_zone(self):
        """Test invalid route pairs with same pickup and dropoff."""
        assert validate_route_pair(1, 1) is False
        assert validate_route_pair(5, 5) is False

    def test_validate_route_pair_negative_pickup(self):
        """Test invalid route pairs with negative pickup zone."""
        assert validate_route_pair(-1, 2) is False
        assert validate_route_pair(0, 2) is False

    def test_validate_route_pair_negative_dropoff(self):
        """Test invalid route pairs with negative dropoff zone."""
        assert validate_route_pair(1, -2) is False
        assert validate_route_pair(1, 0) is False

    def test_validate_route_pair_both_negative(self):
        """Test invalid route pairs with both zones negative."""
        assert validate_route_pair(-1, -2) is False
        assert validate_route_pair(0, 0) is False