# Design Document

## Overview

The Enhanced Meeting Router is a Python-based automation system that monitors a local directory for meeting transcript files, processes them using natural language processing techniques, and automatically distributes the results to project management and communication platforms. The system follows an event-driven architecture with a file watcher triggering a processing pipeline that includes NLP analysis, API integrations, and notification delivery.

The core design philosophy emphasizes modularity, configurability, and fault tolerance. Each major function (file watching, NLP processing, task creation, notification) is isolated into separate components with clear interfaces, allowing for easy testing and future extensibility.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  File Watcher   │ (Monitors directory for new transcripts)
└────────┬────────┘
         │ Triggers on new file
         ▼
┌─────────────────┐
│ Transcript      │ (Parses speaker-identified text)
│ Parser          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ NLP Processor   │ (Extracts action items & analyzes sentiment)
│                 │
│ ┌─────────────┐ │
│ │Action Item  │ │
│ │Extractor    │ │
│ └─────────────┘ │
│ ┌─────────────┐ │
│ │Sentiment    │ │
│ │Analyzer     │ │
│ └─────────────┘ │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Task Router     │ (Creates tasks in configured backend)
│                 │
│ ┌─────────────┐ │
│ │JIRA Client  │ │
│ ├─────────────┤ │
│ │Trello Client│ │
│ ├─────────────┤ │
│ │Markdown     │ │
│ │Writer       │ │
│ └─────────────┘ │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Notification    │ (Posts summary to team channels)
│ Service         │
│                 │
│ ┌─────────────┐ │
│ │Slack Client │ │
│ ├─────────────┤ │
│ │Teams Client │ │
│ └─────────────┘ │
└─────────────────┘
```

### Component Interaction Flow

1. **File Watcher** detects new transcript file → triggers processing
2. **Transcript Parser** reads file → extracts speaker segments
3. **NLP Processor** analyzes segments → produces action items and risk points
4. **Task Router** receives action items → creates tasks via selected backend API
5. **Notification Service** receives results → generates and posts summary digest

## Components and Interfaces

### 1. Configuration Manager

**Responsibility:** Load and validate configuration parameters from environment variables or config file.

**Interface:**
```python
class Config:
    watch_directory: str
    sentiment_threshold: float  # 0.0 to 1.0
    task_backend: str  # "JIRA", "Trello", or "Markdown"
    notification_endpoint: str  # Slack channel ID or Teams webhook URL
    jira_url: Optional[str]
    jira_api_token: Optional[str]
    trello_api_key: Optional[str]
    trello_api_token: Optional[str]
    slack_bot_token: Optional[str]
    
    @classmethod
    def load() -> Config
```

### 2. File Watcher

**Responsibility:** Monitor directory for new transcript files and trigger processing.

**Interface:**
```python
class FileWatcher:
    def __init__(self, watch_directory: str, callback: Callable[[str], None])
    def start() -> None
    def stop() -> None
```

**Implementation Notes:**
- Uses `watchdog` library for cross-platform file system monitoring
- Filters for files matching pattern `meeting_transcript_*.txt`
- Passes full file path to callback function

### 3. Transcript Parser

**Responsibility:** Parse speaker-identified transcript text into structured segments.

**Interface:**
```python
@dataclass
class SpeakerSegment:
    speaker: str
    text: str
    start_position: int

class TranscriptParser:
    def parse(self, transcript_text: str) -> List[SpeakerSegment]
```

**Implementation Notes:**
- Uses regex to identify speaker patterns: `^([A-Za-z0-9\s\.]+):\s*(.+)$`
- Handles multi-line speaker segments
- Normalizes speaker names (trim whitespace, title case)

### 4. Action Item Extractor

**Responsibility:** Identify action items and their owners from transcript segments.

**Interface:**
```python
@dataclass
class ActionItem:
    owner: str
    task_description: str
    context_quote: str
    
class ActionItemExtractor:
    ACTION_PATTERNS = [
        r"I will\s+(.+)",
        r"I'll\s+(.+)",
        r"Need to\s+(.+)",
        r"Let's follow up on\s+(.+)",
        r"Someone should\s+(.+)",
        r"We need to\s+(.+)",
        r"I can\s+(.+)",
        r"I should\s+(.+)"
    ]
    
    def extract(self, segments: List[SpeakerSegment]) -> List[ActionItem]
```

**Implementation Notes:**
- Scans each segment for action patterns using regex
- Extracts task description from matched pattern
- Assigns owner as the speaker of the segment
- Captures full sentence as context quote

### 5. Sentiment Analyzer

**Responsibility:** Detect risk points through sentiment analysis of key discussion segments.

**Interface:**
```python
@dataclass
class RiskPoint:
    text_segment: str
    sentiment_score: float
    context: str

class SentimentAnalyzer:
    DECISION_PATTERNS = [
        r"We decided",
        r"The final choice is",
        r"We agreed",
        r"The decision is",
        r"We're going with"
    ]
    
    def __init__(self, sentiment_threshold: float)
    def analyze(self, transcript_text: str, segments: List[SpeakerSegment]) -> List[RiskPoint]
```

**Implementation Notes:**
- Uses `transformers` library with pre-trained sentiment model (e.g., `distilbert-base-uncased-finetuned-sst-2-english`)
- Identifies decision points using pattern matching
- Analyzes sentiment of surrounding context (±2 sentences)
- Flags segments with sentiment score below threshold

### 6. Task Backend Interface

**Responsibility:** Abstract interface for creating tasks across different platforms.

**Interface:**
```python
@dataclass
class CreatedTask:
    task_id: str
    url: str
    title: str
    
class TaskBackend(ABC):
    @abstractmethod
    def create_task(self, action_item: ActionItem) -> CreatedTask
    
class JiraBackend(TaskBackend):
    def __init__(self, jira_url: str, api_token: str, project_key: str)
    def create_task(self, action_item: ActionItem) -> CreatedTask
    
class TrelloBackend(TaskBackend):
    def __init__(self, api_key: str, api_token: str, board_id: str, list_id: str)
    def create_task(self, action_item: ActionItem) -> CreatedTask
    
class MarkdownBackend(TaskBackend):
    def __init__(self, output_file: str)
    def create_task(self, action_item: ActionItem) -> CreatedTask
```

**Implementation Notes:**
- JIRA: Uses REST API v3 with bearer token authentication
- Trello: Uses REST API with API key/token authentication
- Markdown: Appends to local file with timestamp and generates local file URLs

### 7. Summary Generator

**Responsibility:** Generate formatted Markdown summary digest from processing results.

**Interface:**
```python
@dataclass
class ProcessingResults:
    action_items: List[ActionItem]
    created_tasks: List[CreatedTask]
    risk_points: List[RiskPoint]
    transcript_text: str

class SummaryGenerator:
    def generate(self, results: ProcessingResults) -> str
```

**Implementation Notes:**
- Extracts key decisions from non-action-item text
- Formats action items with owner and task links
- Includes risk points section if any detected
- Returns Markdown-formatted string

### 8. Notification Service

**Responsibility:** Post summary digest to configured communication platform.

**Interface:**
```python
class NotificationService(ABC):
    @abstractmethod
    def post_message(self, markdown_content: str) -> bool
    
class SlackNotificationService(NotificationService):
    def __init__(self, bot_token: str, channel_id: str)
    def post_message(self, markdown_content: str) -> bool
    
class TeamsNotificationService(NotificationService):
    def __init__(self, webhook_url: str)
    def post_message(self, markdown_content: str) -> bool
```

**Implementation Notes:**
- Slack: Uses Web API with bot token, converts Markdown to Slack blocks
- Teams: Uses incoming webhook, converts Markdown to Adaptive Card format
- Implements retry logic with exponential backoff

### 9. Main Orchestrator

**Responsibility:** Coordinate the entire processing pipeline.

**Interface:**
```python
class MeetingRouter:
    def __init__(self, config: Config)
    def process_transcript(self, file_path: str) -> None
    def start_watching(self) -> None
```

## Data Models

### Configuration Schema

```python
{
    "watch_directory": "/path/to/transcripts",
    "sentiment_threshold": 0.3,
    "task_backend": "JIRA",
    "notification_endpoint": "slack://C1234567890",
    "jira": {
        "url": "https://company.atlassian.net",
        "api_token": "...",
        "project_key": "TEAM"
    },
    "trello": {
        "api_key": "...",
        "api_token": "...",
        "board_id": "...",
        "list_id": "..."
    },
    "slack": {
        "bot_token": "xoxb-..."
    },
    "teams": {
        "webhook_url": "https://..."
    }
}
```

### Transcript Format

```
Speaker 1: Welcome everyone to today's standup.
Jane: Thanks. I will finish the API integration by Friday.
John Doe: I need to review Jane's PR. Also, we decided to use PostgreSQL for the new feature.
Speaker 1: Sounds good. Someone should update the documentation.
```

### Summary Digest Format

```markdown
# Meeting Summary - [Timestamp]

## Key Decisions
- Decided to use PostgreSQL for the new feature

## Action Items
- **Jane**: Finish the API integration by Friday
  - [JIRA-123](https://company.atlassian.net/browse/JIRA-123)
  - Context: "I will finish the API integration by Friday"

- **John Doe**: Review Jane's PR
  - [JIRA-124](https://company.atlassian.net/browse/JIRA-124)
  - Context: "I need to review Jane's PR"

- **Unknown**: Update the documentation
  - [JIRA-125](https://company.atlassian.net/browse/JIRA-125)
  - Context: "Someone should update the documentation"

## 🚨 Risk Points for Review
- **Sentiment Score: 0.25**
  - "we decided to use PostgreSQL for the new feature"
  - Context: Discussion showed concerns about migration complexity
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: File pattern matching correctness
*For any* filename, the file watcher should trigger processing if and only if the filename matches the pattern "meeting_transcript_*.txt"
**Validates: Requirements 1.1**

### Property 2: File content round-trip
*For any* file content written to a transcript file, reading the file after detection should produce identical content
**Validates: Requirements 1.3**

### Property 3: Error resilience
*For any* invalid or unreadable file, the system should log an error and continue monitoring without crashing
**Validates: Requirements 1.5**

### Property 4: Action pattern detection completeness
*For any* transcript containing action phrases ("I will", "Need to", "Let's follow up on", "Someone should"), all instances should be identified by the extractor
**Validates: Requirements 2.1**

### Property 5: Task description extraction completeness
*For any* detected action item phrase, the extracted task description should be non-empty and contain the relevant context from the original text
**Validates: Requirements 2.2**

### Property 6: Owner attribution correctness
*For any* action item extracted from a speaker segment, the owner should match the speaker of that segment
**Validates: Requirements 2.3**

### Property 7: Multiple action items per speaker
*For any* speaker segment containing N action item phrases, exactly N action items should be extracted, all with the same owner
**Validates: Requirements 2.4**

### Property 8: Decision point detection completeness
*For any* transcript containing decision phrases ("We decided", "The final choice is", "We agreed", "The decision is"), all instances should be identified for sentiment analysis
**Validates: Requirements 3.1**

### Property 9: Sentiment context inclusion
*For any* identified decision point, the sentiment analysis should include surrounding sentences (preceding and following context)
**Validates: Requirements 3.2**

### Property 10: Risk flagging threshold correctness
*For any* sentiment score and threshold value, a risk point should be flagged if and only if the score is below the threshold
**Validates: Requirements 3.3**

### Property 11: Risk point context completeness
*For any* flagged risk point, the captured context should include the decision statement and surrounding dialogue
**Validates: Requirements 3.4**

### Property 12: Sentiment analysis error continuation
*For any* sentiment analysis failure on a segment, the system should continue processing remaining segments without termination
**Validates: Requirements 3.5**

### Property 13: Configuration loading round-trip
*For any* valid configuration file, loading the configuration should produce a Config object with values matching the file contents
**Validates: Requirements 4.1**

### Property 14: Sentiment threshold validation
*For any* decimal value, the configuration should accept it as a sentiment threshold if and only if it is between 0.0 and 1.0 inclusive
**Validates: Requirements 4.2**

### Property 15: Task backend validation
*For any* string value, the configuration should accept it as a task backend if and only if it is "JIRA", "Trello", or "Markdown"
**Validates: Requirements 4.3**

### Property 16: Notification endpoint acceptance
*For any* non-empty string, the configuration should accept it as a notification endpoint
**Validates: Requirements 4.4**

### Property 17: Configuration defaults
*For any* configuration with missing required parameters, the system should apply default values and log a warning
**Validates: Requirements 4.5**

### Property 18: Task creation for all action items
*For any* list of N action items, the task router should attempt to create exactly N tasks
**Validates: Requirements 5.1**

### Property 19: Task title population
*For any* created task, the title should be non-empty and derived from the action item description
**Validates: Requirements 5.2**

### Property 20: Task owner assignment
*For any* action item with an identified owner, the created task should be assigned to that owner
**Validates: Requirements 5.3**

### Property 21: Task description context inclusion
*For any* created task, the description should contain the direct quote from the transcript as specified in the action item's context
**Validates: Requirements 5.4**

### Property 22: Markdown backend round-trip
*For any* task created via the Markdown backend, reading the markdown file should contain an entry with the task's timestamp, owner, and description
**Validates: Requirements 5.7**

### Property 23: Task creation error continuation
*For any* task creation failure, the system should continue processing remaining action items and include the failure in the summary digest
**Validates: Requirements 5.8**

### Property 24: Summary digest format validity
*For any* processing results, the generated summary digest should be valid Markdown
**Validates: Requirements 6.1**

### Property 25: Summary decisions section inclusion
*For any* generated summary digest, it should contain a high-level summary section with key decisions
**Validates: Requirements 6.2**

### Property 26: Summary action items completeness
*For any* list of created tasks, all tasks should appear in the summary digest with owner names and task links
**Validates: Requirements 6.3**

### Property 27: Risk points section conditional inclusion
*For any* processing results, the summary digest should include a "🚨 Risk Points for Review" section if and only if risk points were detected
**Validates: Requirements 6.4**

### Property 28: Digest posting failure fallback
*For any* posting failure, the system should save the digest to a local file and log the error
**Validates: Requirements 6.8**

### Property 29: Error logging completeness
*For any* error encountered during processing, a log entry should be created containing timestamp, context, and error details
**Validates: Requirements 7.1**

### Property 30: Error continuation
*For any* error at a processing step, the system should continue to subsequent steps where possible rather than terminating
**Validates: Requirements 7.2**

### Property 31: Retry logic correctness
*For any* rate limiting error, the system should retry up to three times with exponential backoff delays
**Validates: Requirements 7.4**

### Property 32: Speaker label recognition
*For any* text in the format "Speaker Name: dialogue text", the parser should recognize it as a speaker segment
**Validates: Requirements 8.1**

### Property 33: Multi-sentence speaker attribution
*For any* speaker segment containing multiple sentences, all sentences until the next speaker label should be attributed to that speaker
**Validates: Requirements 8.3**

### Property 34: Speaker name normalization consistency
*For any* speaker name with varying whitespace or capitalization, the normalized form should be consistent across all occurrences
**Validates: Requirements 8.5**

## Error Handling

### Error Categories and Strategies

1. **File System Errors**
   - Invalid file format: Log error, skip file, continue monitoring
   - File read failure: Log error with file path, continue monitoring
   - Permission errors: Log error, continue monitoring

2. **Parsing Errors**
   - Malformed speaker labels: Mark owner as "Unknown", continue processing
   - Empty transcript: Generate summary indicating no content found
   - Encoding errors: Attempt UTF-8 decoding, fallback to latin-1, log warning

3. **NLP Processing Errors**
   - Sentiment analysis failure: Log error, skip sentiment for that segment, continue
   - Model loading failure: Log critical error, disable sentiment analysis, continue with action item extraction

4. **API Integration Errors**
   - Authentication failure: Log specific error, fail fast with clear message
   - Rate limiting: Implement exponential backoff (1s, 2s, 4s), retry up to 3 times
   - Network timeout: Retry with backoff, log error if all retries fail
   - Task creation failure: Log error, continue with remaining tasks, include failure in summary

5. **Notification Errors**
   - Posting failure: Save digest to local file, log error with fallback location
   - Format conversion error: Log error, attempt plain text fallback

### Logging Strategy

- Use structured logging with JSON format for easy parsing
- Log levels: DEBUG (detailed flow), INFO (major steps), WARNING (recoverable issues), ERROR (failures), CRITICAL (system-level failures)
- Include correlation ID for each transcript processing session
- Log file rotation: Daily rotation with 30-day retention

## Testing Strategy

### Unit Testing

The system will use `pytest` as the testing framework with the following unit test coverage:

1. **Configuration Loading**
   - Test loading from environment variables
   - Test loading from JSON config file
   - Test default value application
   - Test validation of threshold ranges
   - Test validation of backend options

2. **Transcript Parsing**
   - Test parsing of well-formed transcripts
   - Test handling of various speaker name formats
   - Test multi-line speaker segments
   - Test empty transcripts

3. **Action Item Extraction**
   - Test detection of each action phrase pattern
   - Test owner attribution
   - Test task description extraction
   - Test handling of multiple action items per speaker

4. **Sentiment Analysis**
   - Test decision point detection
   - Test sentiment scoring
   - Test threshold comparison
   - Test context extraction

5. **Task Backend Implementations**
   - Test Markdown file writing and reading
   - Test JIRA API request formatting (mocked)
   - Test Trello API request formatting (mocked)
   - Test error handling for each backend

6. **Summary Generation**
   - Test Markdown formatting
   - Test inclusion of all required sections
   - Test conditional risk points section
   - Test link formatting

### Property-Based Testing

The system will use `hypothesis` for property-based testing in Python. Each property-based test will be configured to run a minimum of 100 iterations.

**Property-Based Test Requirements:**
- Each test must be tagged with a comment explicitly referencing the correctness property from this design document
- Tag format: `# Feature: meeting-router, Property {number}: {property_text}`
- Each correctness property must be implemented by a single property-based test
- Tests should use custom strategies to generate realistic test data (transcripts, action items, etc.)

**Key Property Tests:**

1. **File Pattern Matching** (Property 1)
   - Generate random filenames, verify only matching patterns trigger processing

2. **File Content Round-Trip** (Property 2)
   - Generate random file contents, verify read content matches written content

3. **Action Pattern Detection** (Property 4)
   - Generate transcripts with varying numbers of action phrases, verify all are detected

4. **Owner Attribution** (Property 6)
   - Generate random speaker segments with action items, verify correct owner assignment

5. **Multiple Actions Per Speaker** (Property 7)
   - Generate speaker segments with N action items, verify exactly N items extracted

6. **Threshold Comparison** (Property 10)
   - Generate random sentiment scores and thresholds, verify correct flagging logic

7. **Configuration Validation** (Properties 14, 15)
   - Generate random configuration values, verify validation logic

8. **Task Creation Completeness** (Property 18)
   - Generate N action items, verify N task creation attempts

9. **Markdown Round-Trip** (Property 22)
   - Generate random tasks, write to markdown, read back, verify content

10. **Speaker Name Normalization** (Property 34)
    - Generate speaker names with varying whitespace/capitalization, verify consistent normalization

### Integration Testing

Integration tests will verify end-to-end workflows:

1. **Full Pipeline Test**
   - Place test transcript file in watch directory
   - Verify action items extracted
   - Verify tasks created (using Markdown backend)
   - Verify summary generated
   - Verify summary saved to file

2. **API Integration Tests** (Optional, requires test credentials)
   - Test JIRA task creation with test instance
   - Test Trello card creation with test board
   - Test Slack message posting with test channel

### Test Data Generators

Custom Hypothesis strategies for generating test data:

```python
@st.composite
def speaker_names(draw):
    """Generate realistic speaker names"""
    formats = [
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        st.from_regex(r"Speaker \d+", fullmatch=True),
        st.from_regex(r"[A-Z]\. [A-Z][a-z]+", fullmatch=True)
    ]
    return draw(st.one_of(formats))

@st.composite
def action_items(draw):
    """Generate action item text"""
    patterns = ["I will", "Need to", "Let's follow up on", "Someone should"]
    pattern = draw(st.sampled_from(patterns))
    task = draw(st.text(min_size=5, max_size=100))
    return f"{pattern} {task}"

@st.composite
def transcripts(draw):
    """Generate full transcript text"""
    num_speakers = draw(st.integers(min_value=1, max_value=5))
    num_segments = draw(st.integers(min_value=1, max_value=20))
    
    segments = []
    for _ in range(num_segments):
        speaker = draw(speaker_names())
        text = draw(st.text(min_size=10, max_size=200))
        segments.append(f"{speaker}: {text}")
    
    return "\n".join(segments)
```

## Dependencies

### Core Libraries

- **Python 3.9+**: Base runtime
- **watchdog**: File system monitoring
- **transformers**: Pre-trained NLP models for sentiment analysis
- **torch**: Backend for transformers library
- **requests**: HTTP client for API calls
- **python-dotenv**: Environment variable management

### API Client Libraries

- **atlassian-python-api**: JIRA REST API client
- **py-trello**: Trello REST API client
- **slack-sdk**: Slack Web API client

### Testing Libraries

- **pytest**: Unit testing framework
- **hypothesis**: Property-based testing framework
- **pytest-mock**: Mocking utilities
- **pytest-cov**: Code coverage reporting

### Development Tools

- **black**: Code formatting
- **mypy**: Static type checking
- **pylint**: Code linting
- **pre-commit**: Git hooks for code quality

## Deployment Considerations

### Environment Setup

1. **Configuration File**: Create `config.json` or use environment variables
2. **API Credentials**: Securely store API tokens (use environment variables or secrets manager)
3. **Watch Directory**: Ensure directory exists and has appropriate permissions
4. **Log Directory**: Create directory for log files with write permissions

### Running the System

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MEETING_ROUTER_CONFIG=/path/to/config.json
export JIRA_API_TOKEN=your_token_here
export SLACK_BOT_TOKEN=your_token_here

# Run the meeting router
python -m meeting_router.main
```

### Monitoring and Maintenance

- Monitor log files for errors and warnings
- Set up alerts for critical errors (authentication failures, repeated API errors)
- Periodically review flagged risk points for false positives
- Update sentiment model if accuracy degrades
- Rotate API tokens according to security policies

## Future Enhancements

1. **Multi-language Support**: Extend NLP processing to support transcripts in multiple languages
2. **Custom Action Patterns**: Allow users to define custom regex patterns for action item detection
3. **Priority Detection**: Analyze text for urgency indicators and set task priorities
4. **Meeting Type Classification**: Automatically categorize meetings (standup, planning, retrospective) and adjust processing
5. **Speaker Identification**: Integrate with speech-to-text services for automatic speaker identification
6. **Dashboard**: Web interface for viewing processing history and statistics
7. **Webhook Triggers**: Support triggering via webhooks instead of file watching
8. **Email Notifications**: Send individual emails to task assignees
