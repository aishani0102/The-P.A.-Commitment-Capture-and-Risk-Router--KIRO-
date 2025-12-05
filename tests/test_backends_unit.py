"""Unit tests for task backends."""

import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import pytest

from meeting_router.backends import MarkdownBackend, JiraBackend, TrelloBackend
from meeting_router.models import ActionItem


def test_markdown_backend_create_task():
    """Test creating a task with Markdown backend."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        action_item = ActionItem(
            owner="Alice",
            task_description="Complete the report",
            context_quote="I will complete the report by Friday"
        )
        
        task = backend.create_task(action_item)
        
        assert task.task_id
        assert task.url
        assert task.title == "Complete the report"
        
        # Verify file content
        with open(temp_file, 'r') as f:
            content = f.read()
        
        assert "Alice" in content
        assert "Complete the report" in content
        assert "I will complete the report by Friday" in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_markdown_backend_file_initialization():
    """Test that Markdown backend initializes file with header."""
    temp_file = tempfile.mktemp(suffix='.md')
    
    try:
        backend = MarkdownBackend(temp_file)
        
        # File should exist
        assert os.path.exists(temp_file)
        
        # Should have header
        with open(temp_file, 'r') as f:
            content = f.read()
        
        assert "Meeting Action Items" in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_markdown_backend_multiple_tasks():
    """Test creating multiple tasks."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        action_items = [
            ActionItem("Alice", "Task 1", "Context 1"),
            ActionItem("Bob", "Task 2", "Context 2"),
            ActionItem("Charlie", "Task 3", "Context 3"),
        ]
        
        tasks = [backend.create_task(item) for item in action_items]
        
        assert len(tasks) == 3
        
        # All tasks should have unique IDs
        task_ids = [t.task_id for t in tasks]
        assert len(task_ids) == len(set(task_ids))
        
        # Verify all tasks in file
        with open(temp_file, 'r') as f:
            content = f.read()
        
        for item in action_items:
            assert item.owner in content
            assert item.task_description in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@patch('meeting_router.backends.Jira')
def test_jira_backend_create_task(mock_jira_class):
    """Test creating a task with JIRA backend."""
    # Mock JIRA client
    mock_jira = Mock()
    mock_jira.issue_create.return_value = {"key": "PROJ-123"}
    mock_jira_class.return_value = mock_jira
    
    backend = JiraBackend(
        jira_url="https://test.atlassian.net",
        api_token="test_token",
        project_key="PROJ"
    )
    
    action_item = ActionItem(
        owner="Alice",
        task_description="Complete the API integration",
        context_quote="I will complete the API integration"
    )
    
    task = backend.create_task(action_item)
    
    assert task.task_id == "PROJ-123"
    assert task.url == "https://test.atlassian.net/browse/PROJ-123"
    assert task.title == "Complete the API integration"
    
    # Verify JIRA API was called correctly
    mock_jira.issue_create.assert_called_once()
    call_args = mock_jira.issue_create.call_args[1]['fields']
    assert call_args['project']['key'] == "PROJ"
    assert "Complete the API integration" in call_args['summary']


@patch('meeting_router.backends.Jira')
def test_jira_backend_initialization_failure(mock_jira_class):
    """Test JIRA backend handles initialization failure."""
    mock_jira_class.side_effect = Exception("Connection failed")
    
    backend = JiraBackend(
        jira_url="https://test.atlassian.net",
        api_token="test_token",
        project_key="PROJ"
    )
    
    # Should handle initialization failure gracefully
    assert backend.jira is None


@patch('meeting_router.backends.Jira')
def test_jira_backend_create_task_failure(mock_jira_class):
    """Test JIRA backend handles task creation failure."""
    mock_jira = Mock()
    mock_jira.issue_create.side_effect = Exception("API error")
    mock_jira_class.return_value = mock_jira
    
    backend = JiraBackend(
        jira_url="https://test.atlassian.net",
        api_token="test_token",
        project_key="PROJ"
    )
    
    action_item = ActionItem("Alice", "Task", "Context")
    
    # Should raise exception on failure
    with pytest.raises(Exception):
        backend.create_task(action_item)


@patch('meeting_router.backends.TrelloClient')
def test_trello_backend_create_task(mock_trello_class):
    """Test creating a task with Trello backend."""
    # Mock Trello client
    mock_client = Mock()
    mock_list = Mock()
    mock_card = Mock()
    mock_card.id = "card123"
    mock_card.url = "https://trello.com/c/card123"
    mock_list.add_card.return_value = mock_card
    mock_client.get_list.return_value = mock_list
    mock_trello_class.return_value = mock_client
    
    backend = TrelloBackend(
        api_key="test_key",
        api_token="test_token",
        board_id="board123",
        list_id="list123"
    )
    
    action_item = ActionItem(
        owner="Bob",
        task_description="Review the PR",
        context_quote="I need to review the PR"
    )
    
    task = backend.create_task(action_item)
    
    assert task.task_id == "card123"
    assert task.url == "https://trello.com/c/card123"
    assert task.title == "Review the PR"
    
    # Verify Trello API was called correctly
    mock_list.add_card.assert_called_once()


@patch('meeting_router.backends.TrelloClient')
def test_trello_backend_initialization_failure(mock_trello_class):
    """Test Trello backend handles initialization failure."""
    mock_trello_class.side_effect = Exception("Connection failed")
    
    backend = TrelloBackend(
        api_key="test_key",
        api_token="test_token",
        board_id="board123",
        list_id="list123"
    )
    
    # Should handle initialization failure gracefully
    assert backend.client is None


@patch('meeting_router.backends.TrelloClient')
def test_trello_backend_create_task_failure(mock_trello_class):
    """Test Trello backend handles task creation failure."""
    mock_client = Mock()
    mock_client.get_list.side_effect = Exception("API error")
    mock_trello_class.return_value = mock_client
    
    backend = TrelloBackend(
        api_key="test_key",
        api_token="test_token",
        board_id="board123",
        list_id="list123"
    )
    
    action_item = ActionItem("Bob", "Task", "Context")
    
    # Should raise exception on failure
    with pytest.raises(Exception):
        backend.create_task(action_item)


def test_markdown_backend_task_id_format():
    """Test that task IDs follow expected format."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        action_item = ActionItem("Alice", "Task", "Context")
        task = backend.create_task(action_item)
        
        # Task ID should start with "task_"
        assert task.task_id.startswith("task_")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_markdown_backend_url_format():
    """Test that URLs follow file:// format."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        action_item = ActionItem("Alice", "Task", "Context")
        task = backend.create_task(action_item)
        
        # URL should start with "file://"
        assert task.url.startswith("file://")
        # URL should contain task ID as anchor
        assert f"#{task.task_id}" in task.url
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_markdown_backend_timestamp_included():
    """Test that timestamps are included in markdown tasks."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        action_item = ActionItem("Alice", "Task", "Context")
        backend.create_task(action_item)
        
        # Read file
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # Should contain "Created:" timestamp
        assert "Created:" in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
