# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create Python package structure with modules for config, parsing, nlp, backends, notification, and main orchestrator
  - Create requirements.txt with all necessary dependencies (watchdog, transformers, torch, requests, atlassian-python-api, py-trello, slack-sdk, pytest, hypothesis)
  - Set up basic logging configuration
  - Create configuration schema and loading mechanism
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 1.1 Write property test for configuration loading
  - **Property 13: Configuration loading round-trip**
  - **Validates: Requirements 4.1**

- [x] 1.2 Write property test for sentiment threshold validation
  - **Property 14: Sentiment threshold validation**
  - **Validates: Requirements 4.2**

- [x] 1.3 Write property test for task backend validation
  - **Property 15: Task backend validation**
  - **Validates: Requirements 4.3**

- [x] 1.4 Write property test for notification endpoint acceptance
  - **Property 16: Notification endpoint acceptance**
  - **Validates: Requirements 4.4**

- [x] 1.5 Write property test for configuration defaults
  - **Property 17: Configuration defaults**
  - **Validates: Requirements 4.5**

- [x] 2. Implement transcript parser
  - Create TranscriptParser class with speaker segment extraction
  - Implement regex-based speaker label recognition
  - Implement speaker name normalization logic
  - Handle multi-line speaker segments
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 2.1 Write property test for speaker label recognition
  - **Property 32: Speaker label recognition**
  - **Validates: Requirements 8.1**

- [x] 2.2 Write property test for multi-sentence speaker attribution
  - **Property 33: Multi-sentence speaker attribution**
  - **Validates: Requirements 8.3**

- [x] 2.3 Write property test for speaker name normalization
  - **Property 34: Speaker name normalization consistency**
  - **Validates: Requirements 8.5**

- [x] 2.4 Write unit tests for transcript parser
  - Test parsing of well-formed transcripts
  - Test handling of various speaker name formats
  - Test empty transcripts
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 3. Implement action item extractor
  - Create ActionItemExtractor class with pattern matching
  - Define regex patterns for all action phrases ("I will", "Need to", "Let's follow up on", "Someone should", etc.)
  - Implement task description extraction logic
  - Implement owner attribution from speaker segments
  - Handle multiple action items per speaker
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3.1 Write property test for action pattern detection
  - **Property 4: Action pattern detection completeness**
  - **Validates: Requirements 2.1**

- [x] 3.2 Write property test for task description extraction
  - **Property 5: Task description extraction completeness**
  - **Validates: Requirements 2.2**

- [x] 3.3 Write property test for owner attribution
  - **Property 6: Owner attribution correctness**
  - **Validates: Requirements 2.3**

- [x] 3.4 Write property test for multiple action items per speaker
  - **Property 7: Multiple action items per speaker**
  - **Validates: Requirements 2.4**

- [x] 3.5 Write unit tests for action item extractor
  - Test detection of each action phrase pattern
  - Test handling of quoted or hypothetical contexts
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Implement sentiment analyzer
  - Create SentimentAnalyzer class with decision point detection
  - Integrate transformers library with pre-trained sentiment model (distilbert-base-uncased-finetuned-sst-2-english)
  - Implement decision phrase pattern matching
  - Implement context extraction (surrounding sentences)
  - Implement threshold-based risk point flagging
  - Handle sentiment analysis errors gracefully
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.1 Write property test for decision point detection
  - **Property 8: Decision point detection completeness**
  - **Validates: Requirements 3.1**

- [x] 4.2 Write property test for sentiment context inclusion
  - **Property 9: Sentiment context inclusion**
  - **Validates: Requirements 3.2**

- [x] 4.3 Write property test for risk flagging threshold
  - **Property 10: Risk flagging threshold correctness**
  - **Validates: Requirements 3.3**

- [x] 4.4 Write property test for risk point context completeness
  - **Property 11: Risk point context completeness**
  - **Validates: Requirements 3.4**

- [x] 4.5 Write property test for sentiment analysis error continuation
  - **Property 12: Sentiment analysis error continuation**
  - **Validates: Requirements 3.5**

- [x] 4.6 Write unit tests for sentiment analyzer
  - Test sentiment scoring with sample texts
  - Test context extraction around decision points
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Implement task backend interface and implementations
  - Create abstract TaskBackend interface
  - Implement MarkdownBackend with file writing
  - Implement JiraBackend with REST API integration
  - Implement TrelloBackend with REST API integration
  - Handle task creation errors and implement retry logic
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [x] 5.1 Write property test for task creation completeness
  - **Property 18: Task creation for all action items**
  - **Validates: Requirements 5.1**

- [x] 5.2 Write property test for task title population
  - **Property 19: Task title population**
  - **Validates: Requirements 5.2**

- [x] 5.3 Write property test for task owner assignment
  - **Property 20: Task owner assignment**
  - **Validates: Requirements 5.3**

- [x] 5.4 Write property test for task description context
  - **Property 21: Task description context inclusion**
  - **Validates: Requirements 5.4**

- [x] 5.5 Write property test for markdown backend round-trip
  - **Property 22: Markdown backend round-trip**
  - **Validates: Requirements 5.7**

- [x] 5.6 Write property test for task creation error continuation
  - **Property 23: Task creation error continuation**
  - **Validates: Requirements 5.8**

- [x] 5.7 Write unit tests for task backends
  - Test Markdown file writing and reading
  - Test JIRA API request formatting (mocked)
  - Test Trello API request formatting (mocked)
  - Test error handling for each backend
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [x] 6. Implement summary generator
  - Create SummaryGenerator class
  - Implement key decisions extraction from non-action-item text
  - Implement Markdown formatting for action items with links
  - Implement conditional risk points section
  - Ensure valid Markdown output
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6.1 Write property test for summary digest format validity
  - **Property 24: Summary digest format validity**
  - **Validates: Requirements 6.1**

- [x] 6.2 Write property test for summary decisions section
  - **Property 25: Summary decisions section inclusion**
  - **Validates: Requirements 6.2**

- [x] 6.3 Write property test for summary action items completeness
  - **Property 26: Summary action items completeness**
  - **Validates: Requirements 6.3**

- [x] 6.4 Write property test for risk points section conditional inclusion
  - **Property 27: Risk points section conditional inclusion**
  - **Validates: Requirements 6.4**

- [x] 6.5 Write unit tests for summary generator
  - Test Markdown formatting
  - Test link formatting
  - Test section inclusion logic
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 7. Implement notification service
  - Create abstract NotificationService interface
  - Implement SlackNotificationService with Web API integration
  - Implement TeamsNotificationService with webhook integration
  - Convert Markdown to platform-specific formats (Slack blocks, Teams Adaptive Cards)
  - Implement retry logic with exponential backoff
  - Implement fallback to local file on posting failure
  - _Requirements: 6.5, 6.6, 6.7, 6.8, 7.4_

- [x] 7.1 Write property test for digest posting failure fallback
  - **Property 28: Digest posting failure fallback**
  - **Validates: Requirements 6.8**

- [x] 7.2 Write property test for retry logic
  - **Property 31: Retry logic correctness**
  - **Validates: Requirements 7.4**

- [x] 7.3 Write unit tests for notification service
  - Test Markdown to Slack blocks conversion
  - Test Markdown to Teams Adaptive Card conversion
  - Test retry logic with mocked failures
  - Test fallback file writing
  - _Requirements: 6.5, 6.6, 6.7, 6.8, 7.4_

- [x] 8. Implement file watcher
  - Create FileWatcher class using watchdog library
  - Implement file pattern matching for "meeting_transcript_*.txt"
  - Implement callback mechanism for triggering processing
  - Handle file reading with error handling
  - Implement continuous monitoring without manual intervention
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 8.1 Write property test for file pattern matching
  - **Property 1: File pattern matching correctness**
  - **Validates: Requirements 1.1**

- [x] 8.2 Write property test for file content round-trip
  - **Property 2: File content round-trip**
  - **Validates: Requirements 1.3**

- [x] 8.3 Write property test for error resilience
  - **Property 3: Error resilience**
  - **Validates: Requirements 1.5**

- [x] 8.4 Write unit tests for file watcher
  - Test file detection with matching patterns
  - Test file detection with non-matching patterns
  - Test file reading with various sizes
  - Test error handling for invalid files
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 9. Implement main orchestrator and error handling
  - Create MeetingRouter class that coordinates all components
  - Implement process_transcript method that runs the full pipeline
  - Implement comprehensive error logging with timestamp, context, and details
  - Implement error continuation logic (continue processing on non-fatal errors)
  - Implement start_watching method to begin file monitoring
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 9.1 Write property test for error logging completeness
  - **Property 29: Error logging completeness**
  - **Validates: Requirements 7.1**

- [x] 9.2 Write property test for error continuation
  - **Property 30: Error continuation**
  - **Validates: Requirements 7.2**

- [x] 9.3 Write unit tests for main orchestrator
  - Test full pipeline with valid transcript
  - Test error handling at various stages
  - Test logging output
  - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [x] 10. Create main entry point and CLI
  - Create main.py with command-line interface
  - Implement configuration loading from file or environment
  - Implement graceful shutdown handling (SIGINT, SIGTERM)
  - Add command-line arguments for config file path and log level
  - Create example configuration file template
  - _Requirements: 4.1, 4.5_

- [x] 11. Create example transcript and documentation
  - Create sample meeting_transcript_example.txt file
  - Create README.md with setup instructions
  - Document configuration options
  - Document API credential setup for JIRA, Trello, Slack, Teams
  - Create example config.json file
  - _Requirements: All_

- [x] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
