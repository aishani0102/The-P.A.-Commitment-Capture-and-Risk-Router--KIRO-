"""Configuration management for Meeting Router."""

import json
import os
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration for the Meeting Router system."""
    
    watch_directory: str = "./transcripts"
    sentiment_threshold: float = 0.3
    task_backend: str = "Markdown"
    notification_endpoint: str = ""
    
    # JIRA configuration
    jira_url: Optional[str] = None
    jira_api_token: Optional[str] = None
    jira_project_key: Optional[str] = "TEAM"
    
    # Trello configuration
    trello_api_key: Optional[str] = None
    trello_api_token: Optional[str] = None
    trello_board_id: Optional[str] = None
    trello_list_id: Optional[str] = None
    
    # Slack configuration
    slack_bot_token: Optional[str] = None
    slack_channel_id: Optional[str] = None
    
    # Teams configuration
    teams_webhook_url: Optional[str] = None
    
    # Output configuration
    markdown_output_file: str = "./tasks.md"
    summary_output_dir: str = "./summaries"
    log_level: str = "INFO"
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from file or environment variables.
        
        Args:
            config_path: Path to JSON configuration file. If None, uses environment variables.
            
        Returns:
            Config object with loaded values.
        """
        config = cls()
        
        # Try to load from config file
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    config._load_from_dict(data)
                    logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config file {config_path}: {e}. Using defaults.")
        
        # Override with environment variables
        config._load_from_env()
        
        # Validate configuration
        config._validate()
        
        return config
    
    def _load_from_dict(self, data: dict) -> None:
        """Load configuration from dictionary."""
        self.watch_directory = data.get("watch_directory", self.watch_directory)
        self.sentiment_threshold = data.get("sentiment_threshold", self.sentiment_threshold)
        self.task_backend = data.get("task_backend", self.task_backend)
        self.notification_endpoint = data.get("notification_endpoint", self.notification_endpoint)
        
        # JIRA config
        if "jira" in data:
            jira = data["jira"]
            self.jira_url = jira.get("url")
            self.jira_api_token = jira.get("api_token")
            self.jira_project_key = jira.get("project_key", self.jira_project_key)
        
        # Trello config
        if "trello" in data:
            trello = data["trello"]
            self.trello_api_key = trello.get("api_key")
            self.trello_api_token = trello.get("api_token")
            self.trello_board_id = trello.get("board_id")
            self.trello_list_id = trello.get("list_id")
        
        # Slack config
        if "slack" in data:
            slack = data["slack"]
            self.slack_bot_token = slack.get("bot_token")
            self.slack_channel_id = slack.get("channel_id")
        
        # Teams config
        if "teams" in data:
            teams = data["teams"]
            self.teams_webhook_url = teams.get("webhook_url")
        
        # Output config
        self.markdown_output_file = data.get("markdown_output_file", self.markdown_output_file)
        self.summary_output_dir = data.get("summary_output_dir", self.summary_output_dir)
        self.log_level = data.get("log_level", self.log_level)
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        self.watch_directory = os.getenv("MEETING_ROUTER_WATCH_DIR", self.watch_directory)
        
        threshold = os.getenv("MEETING_ROUTER_SENTIMENT_THRESHOLD")
        if threshold:
            try:
                self.sentiment_threshold = float(threshold)
            except ValueError:
                logger.warning(f"Invalid sentiment threshold in env: {threshold}")
        
        self.task_backend = os.getenv("MEETING_ROUTER_TASK_BACKEND", self.task_backend)
        self.notification_endpoint = os.getenv("MEETING_ROUTER_NOTIFICATION_ENDPOINT", self.notification_endpoint)
        
        # JIRA
        self.jira_url = os.getenv("JIRA_URL", self.jira_url)
        self.jira_api_token = os.getenv("JIRA_API_TOKEN", self.jira_api_token)
        self.jira_project_key = os.getenv("JIRA_PROJECT_KEY", self.jira_project_key)
        
        # Trello
        self.trello_api_key = os.getenv("TRELLO_API_KEY", self.trello_api_key)
        self.trello_api_token = os.getenv("TRELLO_API_TOKEN", self.trello_api_token)
        self.trello_board_id = os.getenv("TRELLO_BOARD_ID", self.trello_board_id)
        self.trello_list_id = os.getenv("TRELLO_LIST_ID", self.trello_list_id)
        
        # Slack
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN", self.slack_bot_token)
        self.slack_channel_id = os.getenv("SLACK_CHANNEL_ID", self.slack_channel_id)
        
        # Teams
        self.teams_webhook_url = os.getenv("TEAMS_WEBHOOK_URL", self.teams_webhook_url)
        
        # Output
        self.markdown_output_file = os.getenv("MEETING_ROUTER_MARKDOWN_FILE", self.markdown_output_file)
        self.summary_output_dir = os.getenv("MEETING_ROUTER_SUMMARY_DIR", self.summary_output_dir)
        self.log_level = os.getenv("MEETING_ROUTER_LOG_LEVEL", self.log_level)
    
    def _validate(self) -> None:
        """Validate configuration values."""
        # Validate sentiment threshold
        if not (0.0 <= self.sentiment_threshold <= 1.0):
            logger.warning(
                f"Sentiment threshold {self.sentiment_threshold} out of range [0.0, 1.0]. "
                f"Using default 0.3"
            )
            self.sentiment_threshold = 0.3
        
        # Validate task backend
        valid_backends = ["JIRA", "Trello", "Markdown"]
        if self.task_backend not in valid_backends:
            logger.warning(
                f"Invalid task backend '{self.task_backend}'. "
                f"Must be one of {valid_backends}. Using 'Markdown'"
            )
            self.task_backend = "Markdown"
        
        # Warn about missing backend-specific config
        if self.task_backend == "JIRA" and not (self.jira_url and self.jira_api_token):
            logger.warning("JIRA backend selected but credentials not configured")
        
        if self.task_backend == "Trello" and not (self.trello_api_key and self.trello_api_token):
            logger.warning("Trello backend selected but credentials not configured")
        
        # Create directories if they don't exist
        os.makedirs(self.watch_directory, exist_ok=True)
        os.makedirs(self.summary_output_dir, exist_ok=True)
