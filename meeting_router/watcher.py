"""File system watcher for monitoring transcript files."""

import logging
import time
from typing import Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class FileWatcher:
    """Watches a directory for new meeting transcript files."""
    
    TRANSCRIPT_PATTERN = "meeting_transcript_*.txt"
    
    def __init__(self, watch_directory: str, callback: Callable[[str], None]):
        """Initialize file watcher.
        
        Args:
            watch_directory: Directory to monitor for new files.
            callback: Function to call when a new transcript file is detected.
        """
        self.watch_directory = watch_directory
        self.callback = callback
        self.observer = None
        self._setup_observer()
    
    def _setup_observer(self) -> None:
        """Set up the watchdog observer."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler, FileCreatedEvent
            
            class TranscriptHandler(FileSystemEventHandler):
                """Handler for transcript file events."""
                
                def __init__(self, callback: Callable[[str], None]):
                    self.callback = callback
                
                def on_created(self, event):
                    """Handle file creation events."""
                    if isinstance(event, FileCreatedEvent):
                        file_path = event.src_path
                        if self._matches_pattern(file_path):
                            logger.info(f"Detected new transcript: {file_path}")
                            self.callback(file_path)
                
                def _matches_pattern(self, file_path: str) -> bool:
                    """Check if file matches transcript pattern."""
                    from fnmatch import fnmatch
                    filename = Path(file_path).name
                    return fnmatch(filename, FileWatcher.TRANSCRIPT_PATTERN)
            
            self.observer = Observer()
            event_handler = TranscriptHandler(self.callback)
            self.observer.schedule(event_handler, self.watch_directory, recursive=False)
            
            logger.info(f"Set up file watcher for {self.watch_directory}")
        except ImportError:
            logger.error("watchdog not installed. Install with: pip install watchdog")
            self.observer = None
        except Exception as e:
            logger.error(f"Failed to set up file watcher: {e}")
            self.observer = None
    
    def start(self) -> None:
        """Start watching for files."""
        if self.observer is None:
            logger.error("Observer not initialized, cannot start watching")
            return
        
        self.observer.start()
        logger.info(f"Started watching {self.watch_directory}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self) -> None:
        """Stop watching for files."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped file watcher")
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read the contents of a file.
        
        Args:
            file_path: Path to the file to read.
            
        Returns:
            File contents as a string.
            
        Raises:
            Exception: If file cannot be read.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Read file: {file_path} ({len(content)} bytes)")
            return content
        except UnicodeDecodeError:
            # Fallback to latin-1 encoding
            logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
