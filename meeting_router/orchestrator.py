"""Main orchestrator for the Meeting Router system."""

import logging
from typing import List

from .config import Config
from .parser import TranscriptParser
from .nlp import ActionItemExtractor, SentimentAnalyzer
from .backends import TaskBackend, MarkdownBackend, JiraBackend, TrelloBackend
from .summary import SummaryGenerator
from .notification import NotificationService, SlackNotificationService, TeamsNotificationService, FileNotificationService
from .watcher import FileWatcher
from .models import ProcessingResults, CreatedTask

logger = logging.getLogger(__name__)


class MeetingRouter:
    """Main orchestrator for processing meeting transcripts."""
    
    def __init__(self, config: Config):
        """Initialize the Meeting Router.
        
        Args:
            config: Configuration object.
        """
        self.config = config
        
        # Initialize components
        self.parser = TranscriptParser()
        self.action_extractor = ActionItemExtractor()
        self.sentiment_analyzer = SentimentAnalyzer(config.sentiment_threshold)
        self.summary_generator = SummaryGenerator()
        
        # Initialize task backend
        self.task_backend = self._create_task_backend()
        
        # Initialize notification service
        self.notification_service = self._create_notification_service()
        
        # Initialize file watcher
        self.file_watcher = FileWatcher(
            config.watch_directory,
            self.process_transcript
        )
        
        logger.info("Meeting Router initialized")
    
    def _create_task_backend(self) -> TaskBackend:
        """Create the appropriate task backend based on configuration.
        
        Returns:
            TaskBackend instance.
        """
        if self.config.task_backend == "JIRA":
            if not (self.config.jira_url and self.config.jira_api_token):
                logger.error("JIRA backend selected but credentials missing, falling back to Markdown")
                return MarkdownBackend(self.config.markdown_output_file)
            return JiraBackend(
                self.config.jira_url,
                self.config.jira_api_token,
                self.config.jira_project_key
            )
        elif self.config.task_backend == "Trello":
            if not (self.config.trello_api_key and self.config.trello_api_token):
                logger.error("Trello backend selected but credentials missing, falling back to Markdown")
                return MarkdownBackend(self.config.markdown_output_file)
            return TrelloBackend(
                self.config.trello_api_key,
                self.config.trello_api_token,
                self.config.trello_board_id,
                self.config.trello_list_id
            )
        else:  # Markdown
            return MarkdownBackend(self.config.markdown_output_file)
    
    def _create_notification_service(self) -> NotificationService:
        """Create the appropriate notification service based on configuration.
        
        Returns:
            NotificationService instance.
        """
        endpoint = self.config.notification_endpoint
        
        if endpoint.startswith("slack://") or self.config.slack_bot_token:
            if not self.config.slack_bot_token:
                logger.error("Slack endpoint specified but token missing, falling back to file")
                return FileNotificationService(self.config.summary_output_dir)
            
            channel_id = endpoint.replace("slack://", "") if endpoint.startswith("slack://") else self.config.slack_channel_id
            return SlackNotificationService(self.config.slack_bot_token, channel_id)
        
        elif endpoint.startswith("https://") and "webhook.office.com" in endpoint:
            return TeamsNotificationService(endpoint)
        
        elif self.config.teams_webhook_url:
            return TeamsNotificationService(self.config.teams_webhook_url)
        
        else:
            # Default to file-based notification
            return FileNotificationService(self.config.summary_output_dir)
    
    def process_transcript(self, file_path: str) -> None:
        """Process a meeting transcript file.
        
        Args:
            file_path: Path to the transcript file.
        """
        logger.info(f"Processing transcript: {file_path}")
        correlation_id = file_path  # Use file path as correlation ID
        
        try:
            # Read file
            try:
                transcript_text = FileWatcher.read_file(file_path)
            except Exception as e:
                logger.error(f"[{correlation_id}] Failed to read file: {e}")
                return
            
            # Parse transcript
            try:
                segments = self.parser.parse(transcript_text)
                if not segments:
                    logger.warning(f"[{correlation_id}] No speaker segments found in transcript")
            except Exception as e:
                logger.error(f"[{correlation_id}] Failed to parse transcript: {e}")
                segments = []
            
            # Extract action items
            try:
                action_items = self.action_extractor.extract(segments)
            except Exception as e:
                logger.error(f"[{correlation_id}] Failed to extract action items: {e}")
                action_items = []
            
            # Analyze sentiment for risk points
            try:
                risk_points = self.sentiment_analyzer.analyze(transcript_text, segments)
            except Exception as e:
                logger.error(f"[{correlation_id}] Failed to analyze sentiment: {e}")
                risk_points = []
            
            # Create tasks
            created_tasks = []
            for action_item in action_items:
                try:
                    task = self.task_backend.create_task(action_item)
                    created_tasks.append(task)
                except Exception as e:
                    logger.error(f"[{correlation_id}] Failed to create task for '{action_item.task_description}': {e}")
                    # Create a placeholder task to maintain alignment
                    created_tasks.append(CreatedTask(
                        task_id="ERROR",
                        url="#",
                        title=f"FAILED: {action_item.task_description}"
                    ))
            
            # Generate summary
            try:
                results = ProcessingResults(
                    action_items=action_items,
                    created_tasks=created_tasks,
                    risk_points=risk_points,
                    transcript_text=transcript_text
                )
                summary = self.summary_generator.generate(results)
            except Exception as e:
                logger.error(f"[{correlation_id}] Failed to generate summary: {e}")
                summary = f"# Error Processing Transcript\n\nFailed to generate summary: {e}"
            
            # Post notification
            try:
                success = self.notification_service.post_message(summary)
                if not success:
                    # Fallback to file
                    logger.warning(f"[{correlation_id}] Notification failed, saving to file")
                    fallback = FileNotificationService(self.config.summary_output_dir)
                    fallback.post_message(summary)
            except Exception as e:
                logger.error(f"[{correlation_id}] Failed to post notification: {e}")
                # Fallback to file
                try:
                    fallback = FileNotificationService(self.config.summary_output_dir)
                    fallback.post_message(summary)
                except Exception as e2:
                    logger.error(f"[{correlation_id}] Fallback notification also failed: {e2}")
            
            logger.info(f"[{correlation_id}] Completed processing transcript")
        
        except Exception as e:
            logger.error(f"[{correlation_id}] Unexpected error during processing: {e}", exc_info=True)
    
    def start_watching(self) -> None:
        """Start watching for new transcript files."""
        logger.info("Starting Meeting Router in watch mode")
        self.file_watcher.start()
