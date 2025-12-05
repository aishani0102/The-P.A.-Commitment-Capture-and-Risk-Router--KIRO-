"""Property-based tests for configuration loading and validation."""

import json
import os
import tempfile
from hypothesis import given, strategies as st
import pytest

from meeting_router.config import Config


# Feature: meeting-router, Property 13: Configuration loading round-trip
# For any valid configuration file, loading the configuration should produce a Config object with values matching the file contents
@given(
    watch_dir=st.text(min_size=1, max_size=100),
    sentiment_threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    task_backend=st.sampled_from(["JIRA", "Trello", "Markdown"]),
    notification_endpoint=st.text(min_size=0, max_size=200)
)
def test_config_loading_round_trip(watch_dir, sentiment_threshold, task_backend, notification_endpoint):
    """Test that configuration values are correctly loaded from a file."""
    # Create a temporary config file
    config_data = {
        "watch_directory": watch_dir,
        "sentiment_threshold": sentiment_threshold,
        "task_backend": task_backend,
        "notification_endpoint": notification_endpoint
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        # Load configuration
        config = Config.load(config_path)
        
        # Verify values match
        assert config.watch_directory == watch_dir
        assert config.sentiment_threshold == sentiment_threshold
        assert config.task_backend == task_backend
        assert config.notification_endpoint == notification_endpoint
    finally:
        # Clean up
        os.unlink(config_path)


# Feature: meeting-router, Property 14: Sentiment threshold validation
# For any decimal value, the configuration should accept it as a sentiment threshold if and only if it is between 0.0 and 1.0 inclusive
@given(threshold=st.floats(allow_nan=False, allow_infinity=False))
def test_sentiment_threshold_validation(threshold):
    """Test that sentiment threshold is validated to be between 0.0 and 1.0."""
    config_data = {
        "sentiment_threshold": threshold
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        config = Config.load(config_path)
        
        # If threshold is valid, it should be preserved
        # If invalid, it should be set to default (0.3)
        if 0.0 <= threshold <= 1.0:
            assert config.sentiment_threshold == threshold
        else:
            assert config.sentiment_threshold == 0.3  # Default value
    finally:
        os.unlink(config_path)


# Feature: meeting-router, Property 15: Task backend validation
# For any string value, the configuration should accept it as a task backend if and only if it is "JIRA", "Trello", or "Markdown"
@given(backend=st.text(min_size=0, max_size=50))
def test_task_backend_validation(backend):
    """Test that task backend is validated to be one of the allowed values."""
    config_data = {
        "task_backend": backend
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        config = Config.load(config_path)
        
        # If backend is valid, it should be preserved
        # If invalid, it should be set to default ("Markdown")
        valid_backends = ["JIRA", "Trello", "Markdown"]
        if backend in valid_backends:
            assert config.task_backend == backend
        else:
            assert config.task_backend == "Markdown"  # Default value
    finally:
        os.unlink(config_path)


# Feature: meeting-router, Property 16: Notification endpoint acceptance
# For any non-empty string, the configuration should accept it as a notification endpoint
@given(endpoint=st.text(min_size=0, max_size=200))
def test_notification_endpoint_acceptance(endpoint):
    """Test that any string is accepted as a notification endpoint."""
    config_data = {
        "notification_endpoint": endpoint
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        config = Config.load(config_path)
        
        # Any string should be accepted
        assert config.notification_endpoint == endpoint
    finally:
        os.unlink(config_path)


# Feature: meeting-router, Property 17: Configuration defaults
# For any configuration with missing required parameters, the system should apply default values and log a warning
def test_configuration_defaults():
    """Test that default values are applied when parameters are missing."""
    # Create empty config file
    config_data = {}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        config = Config.load(config_path)
        
        # Verify default values are applied
        assert config.watch_directory == "./transcripts"
        assert config.sentiment_threshold == 0.3
        assert config.task_backend == "Markdown"
        assert config.notification_endpoint == ""
    finally:
        os.unlink(config_path)


@given(
    missing_params=st.lists(
        st.sampled_from(["watch_directory", "sentiment_threshold", "task_backend", "notification_endpoint"]),
        min_size=1,
        max_size=4,
        unique=True
    )
)
def test_configuration_defaults_property(missing_params):
    """Property test that defaults are applied for any combination of missing parameters."""
    # Create config with some parameters missing
    all_params = {
        "watch_directory": "/some/path",
        "sentiment_threshold": 0.5,
        "task_backend": "JIRA",
        "notification_endpoint": "slack://channel"
    }
    
    # Remove the specified parameters
    config_data = {k: v for k, v in all_params.items() if k not in missing_params}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        config = Config.load(config_path)
        
        # Verify that config loads successfully and has valid values
        assert config is not None
        assert 0.0 <= config.sentiment_threshold <= 1.0
        assert config.task_backend in ["JIRA", "Trello", "Markdown"]
        assert isinstance(config.notification_endpoint, str)
        assert isinstance(config.watch_directory, str)
    finally:
        os.unlink(config_path)
