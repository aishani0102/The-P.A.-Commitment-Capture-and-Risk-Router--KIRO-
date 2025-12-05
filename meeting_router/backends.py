"""Task backend implementations for creating tasks in various systems."""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import os
from typing import Optional

from .models import ActionItem, CreatedTask

logger = logging.getLogger(__name__)


class TaskBackend(ABC):
    """Abstract interface for task creation backends."""
    
    @abstractmethod
    def create_task(self, action_item: ActionItem) -> CreatedTask:
        """Create a task from an action item.
        
        Args:
            action_item: The action item to create a task for.
            
        Returns:
            CreatedTask object with task details.
        """
        pass


class MarkdownBackend(TaskBackend):
    """Backend that writes tasks to a Markdown file."""
    
    def __init__(self, output_file: str):
        """Initialize Markdown backend.
        
        Args:
            output_file: Path to the markdown file to write tasks to.
        """
        self.output_file = output_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the output file exists."""
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w') as f:
                f.write("# Meeting Action Items\n\n")
    
    def create_task(self, action_item: ActionItem) -> CreatedTask:
        """Create a task by appending to markdown file.
        
        Args:
            action_item: The action item to create a task for.
            
        Returns:
            CreatedTask object with local file reference.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Append to markdown file
        with open(self.output_file, 'a') as f:
            f.write(f"## {task_id}\n")
            f.write(f"- **Owner**: {action_item.owner}\n")
            f.write(f"- **Task**: {action_item.task_description}\n")
            f.write(f"- **Context**: \"{action_item.context_quote}\"\n")
            f.write(f"- **Created**: {timestamp}\n\n")
        
        # Generate local file URL
        abs_path = os.path.abspath(self.output_file)
        url = f"file://{abs_path}#{task_id}"
        
        logger.info(f"Created markdown task: {task_id}")
        
        return CreatedTask(
            task_id=task_id,
            url=url,
            title=action_item.task_description
        )


class JiraBackend(TaskBackend):
    """Backend that creates tasks in JIRA."""
    
    def __init__(self, jira_url: str, api_token: str, project_key: str):
        """Initialize JIRA backend.
        
        Args:
            jira_url: Base URL of JIRA instance.
            api_token: API token for authentication.
            project_key: JIRA project key to create issues in.
        """
        self.jira_url = jira_url.rstrip('/')
        self.api_token = api_token
        self.project_key = project_key
        self.jira = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize JIRA client."""
        try:
            from atlassian import Jira
            self.jira = Jira(
                url=self.jira_url,
                token=self.api_token
            )
            logger.info("Initialized JIRA client")
        except ImportError:
            logger.error("atlassian-python-api not installed. Install with: pip install atlassian-python-api")
            self.jira = None
        except Exception as e:
            logger.error(f"Failed to initialize JIRA client: {e}")
            self.jira = None
    
    def create_task(self, action_item: ActionItem) -> CreatedTask:
        """Create a task in JIRA.
        
        Args:
            action_item: The action item to create a task for.
            
        Returns:
            CreatedTask object with JIRA issue details.
            
        Raises:
            Exception: If JIRA client is not initialized or task creation fails.
        """
        if self.jira is None:
            raise Exception("JIRA client not initialized")
        
        # Create issue
        issue_dict = {
            "project": {"key": self.project_key},
            "summary": action_item.task_description[:255],  # JIRA has length limits
            "description": f"Context: {action_item.context_quote}\n\nOwner: {action_item.owner}",
            "issuetype": {"name": "Task"},
        }
        
        try:
            issue = self.jira.issue_create(fields=issue_dict)
            issue_key = issue["key"]
            issue_url = f"{self.jira_url}/browse/{issue_key}"
            
            logger.info(f"Created JIRA issue: {issue_key}")
            
            return CreatedTask(
                task_id=issue_key,
                url=issue_url,
                title=action_item.task_description
            )
        except Exception as e:
            logger.error(f"Failed to create JIRA issue: {e}")
            raise


class TrelloBackend(TaskBackend):
    """Backend that creates tasks in Trello."""
    
    def __init__(self, api_key: str, api_token: str, board_id: str, list_id: str):
        """Initialize Trello backend.
        
        Args:
            api_key: Trello API key.
            api_token: Trello API token.
            board_id: ID of the Trello board.
            list_id: ID of the list to create cards in.
        """
        self.api_key = api_key
        self.api_token = api_token
        self.board_id = board_id
        self.list_id = list_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Trello client."""
        try:
            from trello import TrelloClient
            self.client = TrelloClient(
                api_key=self.api_key,
                token=self.api_token
            )
            logger.info("Initialized Trello client")
        except ImportError:
            logger.error("py-trello not installed. Install with: pip install py-trello")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Trello client: {e}")
            self.client = None
    
    def create_task(self, action_item: ActionItem) -> CreatedTask:
        """Create a task in Trello.
        
        Args:
            action_item: The action item to create a task for.
            
        Returns:
            CreatedTask object with Trello card details.
            
        Raises:
            Exception: If Trello client is not initialized or task creation fails.
        """
        if self.client is None:
            raise Exception("Trello client not initialized")
        
        try:
            # Get the list
            trello_list = self.client.get_list(self.list_id)
            
            # Create card
            description = f"Context: {action_item.context_quote}\n\nOwner: {action_item.owner}"
            card = trello_list.add_card(
                name=action_item.task_description,
                desc=description
            )
            
            logger.info(f"Created Trello card: {card.id}")
            
            return CreatedTask(
                task_id=card.id,
                url=card.url,
                title=action_item.task_description
            )
        except Exception as e:
            logger.error(f"Failed to create Trello card: {e}")
            raise
