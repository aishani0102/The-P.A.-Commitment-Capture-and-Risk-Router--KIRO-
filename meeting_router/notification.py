"""Notification services for posting summaries to communication platforms."""

from abc import ABC, abstractmethod
import logging
import time
from typing import Optional
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService(ABC):
    """Abstract interface for notification services."""
    
    @abstractmethod
    def post_message(self, markdown_content: str) -> bool:
        """Post a message to the notification endpoint.
        
        Args:
            markdown_content: Message content in Markdown format.
            
        Returns:
            True if posting succeeded, False otherwise.
        """
        pass
    
    def _retry_with_backoff(self, func, max_retries: int = 3) -> bool:
        """Retry a function with exponential backoff.
        
        Args:
            func: Function to retry.
            max_retries: Maximum number of retry attempts.
            
        Returns:
            True if function succeeded, False otherwise.
        """
        for attempt in range(max_retries):
            try:
                func()
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed: {e}")
                    return False
        return False


class SlackNotificationService(NotificationService):
    """Notification service for Slack."""
    
    def __init__(self, bot_token: str, channel_id: str):
        """Initialize Slack notification service.
        
        Args:
            bot_token: Slack bot token.
            channel_id: Slack channel ID to post to.
        """
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Slack client."""
        try:
            from slack_sdk import WebClient
            self.client = WebClient(token=self.bot_token)
            logger.info("Initialized Slack client")
        except ImportError:
            logger.error("slack-sdk not installed. Install with: pip install slack-sdk")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Slack client: {e}")
            self.client = None
    
    def post_message(self, markdown_content: str) -> bool:
        """Post message to Slack channel.
        
        Args:
            markdown_content: Message content in Markdown format.
            
        Returns:
            True if posting succeeded, False otherwise.
        """
        if self.client is None:
            logger.error("Slack client not initialized")
            return False
        
        def post():
            # Convert markdown to Slack mrkdwn format
            slack_text = self._convert_markdown_to_slack(markdown_content)
            
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=slack_text,
                mrkdwn=True
            )
            
            if not response["ok"]:
                raise Exception(f"Slack API error: {response.get('error', 'Unknown error')}")
            
            logger.info(f"Posted message to Slack channel {self.channel_id}")
        
        return self._retry_with_backoff(post)
    
    def _convert_markdown_to_slack(self, markdown: str) -> str:
        """Convert Markdown to Slack mrkdwn format.
        
        Args:
            markdown: Markdown text.
            
        Returns:
            Slack mrkdwn formatted text.
        """
        # Basic conversion (Slack mrkdwn is similar to Markdown)
        # Headers: ## -> *bold*
        text = markdown.replace("## ", "*").replace("#", "*")
        return text


class TeamsNotificationService(NotificationService):
    """Notification service for Microsoft Teams."""
    
    def __init__(self, webhook_url: str):
        """Initialize Teams notification service.
        
        Args:
            webhook_url: Teams incoming webhook URL.
        """
        self.webhook_url = webhook_url
    
    def post_message(self, markdown_content: str) -> bool:
        """Post message to Teams channel via webhook.
        
        Args:
            markdown_content: Message content in Markdown format.
            
        Returns:
            True if posting succeeded, False otherwise.
        """
        import requests
        
        def post():
            # Create adaptive card payload
            payload = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                            "type": "AdaptiveCard",
                            "version": "1.2",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "text": markdown_content,
                                    "wrap": True
                                }
                            ]
                        }
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Posted message to Teams webhook")
        
        return self._retry_with_backoff(post)


class FileNotificationService(NotificationService):
    """Fallback notification service that saves to a local file."""
    
    def __init__(self, output_dir: str):
        """Initialize file notification service.
        
        Args:
            output_dir: Directory to save summary files to.
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def post_message(self, markdown_content: str) -> bool:
        """Save message to a local file.
        
        Args:
            markdown_content: Message content in Markdown format.
            
        Returns:
            True (always succeeds unless disk error).
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                f.write(markdown_content)
            
            logger.info(f"Saved summary to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save summary to file: {e}")
            return False
