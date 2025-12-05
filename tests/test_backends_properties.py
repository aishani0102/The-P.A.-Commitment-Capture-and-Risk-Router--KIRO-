"""Property-based tests for task backends."""

from hypothesis import given, strategies as st, assume
import tempfile
import os
import pytest

from meeting_router.backends import MarkdownBackend, TaskBackend
from meeting_router.models import ActionItem


# Custom strategies
@st.composite
def action_items(draw):
    """Generate action items."""
    owner = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))))
    task = draw(st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_characters='\n\r')))
    context = draw(st.text(min_size=5, max_size=200, alphabet=st.characters(blacklist_characters='\n\r')))
    
    assume(owner.strip() and task.strip() and context.strip())
    
    return ActionItem(
        owner=owner.strip(),
        task_description=task.strip(),
        context_quote=context.strip()
    )


# Feature: meeting-router, Property 18: Task creation for all action items
# For any list of N action items, the task router should attempt to create exactly N tasks
@given(action_items_list=st.lists(action_items(), min_size=1, max_size=10))
def test_task_creation_completeness(action_items_list):
    """Test that all action items result in task creation attempts."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        created_tasks = []
        for action_item in action_items_list:
            task = backend.create_task(action_item)
            created_tasks.append(task)
        
        # Should create exactly N tasks for N action items
        assert len(created_tasks) == len(action_items_list)
        
        # All tasks should have valid IDs
        for task in created_tasks:
            assert task.task_id
            assert task.url
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Feature: meeting-router, Property 19: Task title population
# For any created task, the title should be non-empty and derived from the action item description
@given(action_item=action_items())
def test_task_title_population(action_item):
    """Test that task titles are populated correctly."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        created_task = backend.create_task(action_item)
        
        # Title should be non-empty
        assert created_task.title
        assert len(created_task.title.strip()) > 0
        
        # Title should be derived from action item description
        assert created_task.title == action_item.task_description
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Feature: meeting-router, Property 20: Task owner assignment
# For any action item with an identified owner, the created task should be assigned to that owner
@given(action_item=action_items())
def test_task_owner_assignment(action_item):
    """Test that task owners are assigned correctly."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        created_task = backend.create_task(action_item)
        
        # Read the markdown file to verify owner is recorded
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # Owner should be in the file
        assert action_item.owner in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Feature: meeting-router, Property 21: Task description context inclusion
# For any created task, the description should contain the direct quote from the transcript
@given(action_item=action_items())
def test_task_description_context_inclusion(action_item):
    """Test that task descriptions include context quotes."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        created_task = backend.create_task(action_item)
        
        # Read the markdown file to verify context is included
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # Context quote should be in the file
        assert action_item.context_quote in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Feature: meeting-router, Property 22: Markdown backend round-trip
# For any task created via Markdown backend, reading the file should contain task details
@given(action_item=action_items())
def test_markdown_backend_round_trip(action_item):
    """Test that tasks written to markdown can be read back."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        # Create task
        created_task = backend.create_task(action_item)
        
        # Read back from file
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # Verify all key information is present
        assert created_task.task_id in content
        assert action_item.owner in content
        assert action_item.task_description in content
        assert action_item.context_quote in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@given(
    action_items_list=st.lists(action_items(), min_size=2, max_size=5)
)
def test_multiple_tasks_round_trip(action_items_list):
    """Test that multiple tasks can be written and read back."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        # Create multiple tasks
        created_tasks = []
        for action_item in action_items_list:
            task = backend.create_task(action_item)
            created_tasks.append(task)
        
        # Read back from file
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # All tasks should be in the file
        for task, action_item in zip(created_tasks, action_items_list):
            assert task.task_id in content
            assert action_item.owner in content
            assert action_item.task_description in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Test task ID uniqueness
@given(action_items_list=st.lists(action_items(), min_size=2, max_size=5))
def test_task_id_uniqueness(action_items_list):
    """Test that each task gets a unique ID."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        task_ids = []
        for action_item in action_items_list:
            task = backend.create_task(action_item)
            task_ids.append(task.task_id)
        
        # All task IDs should be unique
        assert len(task_ids) == len(set(task_ids))
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Test URL generation
@given(action_item=action_items())
def test_task_url_generation(action_item):
    """Test that task URLs are generated correctly."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
    
    try:
        backend = MarkdownBackend(temp_file)
        
        created_task = backend.create_task(action_item)
        
        # URL should be non-empty
        assert created_task.url
        
        # URL should reference the file
        assert temp_file in created_task.url or created_task.task_id in created_task.url
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Test file creation if not exists
def test_file_creation_if_not_exists():
    """Test that the markdown file is created if it doesn't exist."""
    temp_file = tempfile.mktemp(suffix='.md')
    
    try:
        # File should not exist yet
        assert not os.path.exists(temp_file)
        
        # Create backend
        backend = MarkdownBackend(temp_file)
        
        # File should now exist
        assert os.path.exists(temp_file)
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Test appending to existing file
@given(action_items_list=st.lists(action_items(), min_size=2, max_size=3))
def test_appending_to_existing_file(action_items_list):
    """Test that tasks are appended to existing file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        temp_file = f.name
        f.write("# Existing content\n\n")
    
    try:
        backend = MarkdownBackend(temp_file)
        
        # Create tasks
        for action_item in action_items_list:
            backend.create_task(action_item)
        
        # Read file
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # Should contain existing content and new tasks
        assert "Existing content" in content
        for action_item in action_items_list:
            assert action_item.task_description in content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
