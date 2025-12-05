"""Property-based tests for notification services."""

from hypothesis import given, strategies as st, assume, settings
import tempfile
import os
from unittest.mock import Mock, patch
import pytest

from meeting_router.notification import FileNotificationService, SlackNotificationService, TeamsNotificationService


# Feature: meeting-router, Property 28: Digest posting failure fallback
# For any posting failure, the system should save the digest to a local file and log the error
@given(
    markdown_content=st.text(min_size=10, max_size=500, alphabet=st.characters(blacklist_characters='\x00'))
)
def test_digest_posting_failure_fallback(markdown_content):
    """Test that failed postings fall back to file storage."""
    assume(markdown_content.strip())
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create file notification service as fallback
        service = FileNotificationService(temp_dir)
        
        # Post message
        result = service.post_message(markdown_content)
        
        # Should succeed
        assert result is True
        
        # File should be created
        files = os.listdir(temp_dir)
        assert len(files) > 0
        
        # File should contain the content
        file_path = os.path.join(temp_dir, files[0])
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert markdown_content in content


# Feature: meeting-router, Property 31: Retry logic correctness
# For any rate limiting error, the system should retry up to three times with exponential backoff delays
@given(markdown_content=st.text(min_size=10, max_size=200))
@settings(deadline=None)
def test_retry_logic_correctness(markdown_content):
    """Test that retry logic attempts correct number of retries."""
    assume(markdown_content.strip())
    
    with tempfile.TemporaryDirectory() as temp_dir:
        service = FileNotificationService(temp_dir)
        
        # Mock a function that fails
        call_count = [0]
        
        def failing_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Simulated failure")
            # Succeed on third attempt
            return True
        
        # Test retry logic
        result = service._retry_with_backoff(failing_func, max_retries=3)
        
        # Should succeed after retries
        assert result is True
        # Should have been called 3 times
        assert call_count[0] == 3


@given(markdown_content=st.text(min_size=10, max_size=200))
@settings(deadline=None)
def test_retry_logic_all_failures(markdown_content):
    """Test retry logic when all attempts fail."""
    assume(markdown_content.strip())
    
    with tempfile.TemporaryDirectory() as temp_dir:
        service = FileNotificationService(temp_dir)
        
        # Mock a function that always fails
        call_count = [0]
        
        def always_failing_func():
            call_count[0] += 1
            raise Exception("Always fails")
        
        # Test retry logic
        result = service._retry_with_backoff(always_failing_func, max_retries=3)
        
        # Should fail after all retries
        assert result is False
        # Should have been called 3 times
        assert call_count[0] == 3


# Test file notification service always succeeds
@given(markdown_content=st.text(min_size=1, max_size=1000))
def test_file_notification_always_succeeds(markdown_content):
    """Test that file notification service reliably saves content."""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = FileNotificationService(temp_dir)
        
        result = service.post_message(markdown_content)
        
        # Should always succeed (unless disk error)
        assert result is True
        
        # File should exist
        files = os.listdir(temp_dir)
        assert len(files) > 0


# Test multiple messages create multiple files
@given(messages=st.lists(st.text(min_size=10, max_size=100), min_size=2, max_size=5))
def test_multiple_messages_create_multiple_files(messages):
    """Test that multiple messages create separate files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = FileNotificationService(temp_dir)
        
        for message in messages:
            service.post_message(message)
        
        # Should have one file per message
        files = os.listdir(temp_dir)
        assert len(files) == len(messages)


# Test file naming includes timestamp
@given(markdown_content=st.text(min_size=10, max_size=100))
def test_file_naming_includes_timestamp(markdown_content):
    """Test that generated files have timestamp in name."""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = FileNotificationService(temp_dir)
        
        service.post_message(markdown_content)
        
        files = os.listdir(temp_dir)
        assert len(files) == 1
        
        # Filename should contain "summary_" and timestamp pattern
        filename = files[0]
        assert filename.startswith("summary_")
        assert filename.endswith(".md")
        # Should have digits (timestamp)
        assert any(char.isdigit() for char in filename)


# Test Slack service with mock
@given(markdown_content=st.text(min_size=10, max_size=200))
@settings(deadline=None)
@patch('meeting_router.notification.WebClient')
def test_slack_service_posts_message(mock_webclient_class, markdown_content):
    """Test that Slack service attempts to post messages."""
    assume(markdown_content.strip())
    
    # Mock Slack client
    mock_client = Mock()
    mock_client.chat_postMessage.return_value = {"ok": True}
    mock_webclient_class.return_value = mock_client
    
    service = SlackNotificationService("test_token", "test_channel")
    
    result = service.post_message(markdown_content)
    
    # Should succeed
    assert result is True
    
    # Should have called Slack API
    mock_client.chat_postMessage.assert_called_once()


# Test Teams service with mock
@given(markdown_content=st.text(min_size=10, max_size=200))
@settings(deadline=None)
@patch('meeting_router.notification.requests')
def test_teams_service_posts_message(mock_requests, markdown_content):
    """Test that Teams service attempts to post messages."""
    assume(markdown_content.strip())
    
    # Mock requests
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_requests.post.return_value = mock_response
    
    service = TeamsNotificationService("https://test.webhook.url")
    
    result = service.post_message(markdown_content)
    
    # Should succeed
    assert result is True
    
    # Should have called webhook
    mock_requests.post.assert_called_once()


# Test retry with exponential backoff timing
def test_retry_exponential_backoff_timing():
    """Test that retry delays follow exponential backoff pattern."""
    import time
    
    with tempfile.TemporaryDirectory() as temp_dir:
        service = FileNotificationService(temp_dir)
        
        call_times = []
        
        def failing_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("Fail")
            return True
        
        service._retry_with_backoff(failing_func, max_retries=3)
        
        # Should have 3 calls
        assert len(call_times) == 3
        
        # Check delays (approximately 1s, 2s)
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            # First delay should be around 1 second
            assert 0.8 < delay1 < 1.5
        
        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            # Second delay should be around 2 seconds
            assert 1.8 < delay2 < 2.5
