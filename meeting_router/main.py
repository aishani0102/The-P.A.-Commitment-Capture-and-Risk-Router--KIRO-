"""Main entry point for the Meeting Router application."""

import argparse
import logging
import sys
import signal

from .config import Config
from .orchestrator import MeetingRouter


def setup_logging(log_level: str) -> None:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('meeting_router.log')
        ]
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Enhanced Meeting Router')
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (JSON format)'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level'
    )
    parser.add_argument(
        '--process-file',
        type=str,
        help='Process a single transcript file instead of watching'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config.load(args.config)
    
    # Override log level if specified
    if args.log_level:
        config.log_level = args.log_level
    
    # Set up logging
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Enhanced Meeting Router")
    
    # Create orchestrator
    router = MeetingRouter(config)
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal, stopping...")
        router.file_watcher.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Process single file or start watching
    if args.process_file:
        logger.info(f"Processing single file: {args.process_file}")
        router.process_transcript(args.process_file)
    else:
        logger.info("Starting in watch mode")
        router.start_watching()


if __name__ == '__main__':
    main()
