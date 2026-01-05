"""Pytest fixtures for hackles tests"""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_bh():
    """Mock BloodHoundCE instance for testing queries."""
    bh = MagicMock()
    bh.run_query.return_value = []
    bh._accumulated_results = []
    bh.accumulated_results = []
    bh.clear_results_cache = MagicMock()
    return bh


@pytest.fixture
def mock_bh_with_results():
    """Mock BloodHoundCE instance that returns sample results."""
    bh = MagicMock()
    bh._accumulated_results = []
    bh.accumulated_results = []
    bh.clear_results_cache = MagicMock()

    def mock_query(query, params=None):
        # Return sample results based on query content
        if "User" in query and "hasspn" in query:
            return [{"name": "SVC_TEST@DOMAIN.COM", "enabled": True, "admincount": False}]
        elif "Computer" in query:
            return [{"name": "WS01.DOMAIN.COM", "os": "Windows 10", "enabled": True}]
        elif "Group" in query:
            return [{"name": "DOMAIN ADMINS@DOMAIN.COM", "objectid": "S-1-5-21-xxx-512"}]
        return []

    bh.run_query = mock_query
    return bh


@pytest.fixture
def sample_user_results():
    """Sample user query results."""
    return [
        {"name": "ADMIN@DOMAIN.COM", "enabled": True, "admincount": True},
        {"name": "USER1@DOMAIN.COM", "enabled": True, "admincount": False},
        {"name": "SVC_ACCOUNT@DOMAIN.COM", "enabled": True, "hasspn": True},
    ]


@pytest.fixture
def sample_computer_results():
    """Sample computer query results."""
    return [
        {"name": "DC01.DOMAIN.COM", "os": "Windows Server 2019", "enabled": True},
        {"name": "WS01.DOMAIN.COM", "os": "Windows 10", "enabled": True, "haslaps": False},
        {"name": "SRV01.DOMAIN.COM", "os": "Windows Server 2016", "enabled": True},
    ]


@pytest.fixture
def sample_path_results():
    """Sample path finding results."""
    return [
        {
            "nodes": ["USER@DOMAIN.COM", "GROUP@DOMAIN.COM", "DC01.DOMAIN.COM"],
            "node_types": ["User", "Group", "Computer"],
            "relationships": ["MemberOf", "AdminTo"],
            "path_length": 2,
        }
    ]


@pytest.fixture
def mock_config():
    """Configure the real config object for testing.

    Rather than patching the config module (which doesn't work well due to
    import caching), we configure the real singleton with test-appropriate values.
    """
    from hackles.core.config import config

    # Save original values
    original_values = {
        "quiet_mode": config.quiet_mode,
        "debug_mode": config.debug_mode,
        "no_color": config.no_color,
        "output_format": config.output_format,
        "owned_cache": config.owned_cache.copy(),
        "severity_filter": config.severity_filter.copy(),
        "show_progress": config.show_progress,
    }

    # Set test values
    config.quiet_mode = False
    config.debug_mode = False
    config.no_color = True
    config.output_format = "table"
    config.owned_cache = {}
    config.severity_filter = set()
    config.show_progress = False

    yield config

    # Restore original values
    config.quiet_mode = original_values["quiet_mode"]
    config.debug_mode = original_values["debug_mode"]
    config.no_color = original_values["no_color"]
    config.output_format = original_values["output_format"]
    config.owned_cache = original_values["owned_cache"]
    config.severity_filter = original_values["severity_filter"]
    config.show_progress = original_values["show_progress"]
