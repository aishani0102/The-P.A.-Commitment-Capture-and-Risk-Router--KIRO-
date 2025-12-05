# Enhanced Meeting Router

An automated system that processes meeting transcripts to extract action items, detect potential risks through sentiment analysis, and automatically creates tasks in project management tools while notifying team members through communication platforms.

## Features

- **Automatic Transcript Processing**: Monitors a directory for new meeting transcript files
- **Action Item Extraction**: Identifies commitments and tasks from meeting discussions
- **Sentiment Analysis**: Detects potential risks through negative sentiment in decision points
- **Multi-Platform Task Creation**: Creates tasks in JIRA, Trello, or Markdown files
- **Team Notifications**: Posts summaries to Slack or Microsoft Teams
- **Error Resilience**: Continues processing even when individual steps fail

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Dependencies

- `watchdog`: File system monitoring
- `transformers`: NLP and sentiment analysis
- `torch`: Backend for transformers
- `requests`: HTTP client for API calls
- `atlassian-python-api`: JIRA integration
- `py-trello`: Trello integration
- `slack-sdk`: Slack integration

## Configuration

### Option 1: Configuration File

Create a `config.json` file (see `config.example.json` for template):

```json
{
  "watch_directory": "./transcripts",
  "sentiment_threshold": 0.3,
  "task_backend": "Markdown",
  "notification_endpoint": "",
  "markdown_output_file": "./tasks.md",
  "summary_output_dir": "./summaries",
  "log_level": "INFO"
}
```

### Option 2: Environment Variables

```bash
export MEETING_ROUTER_WATCH_DIR="./transcripts"
export MEETING_ROUTER_SENTIMENT_THRESHOLD="0.3"
export MEETING_ROUTER_TASK_BACKEND="Markdown"
export MEETING_ROUTER_LOG_LEVEL="INFO"
```

### Configuration Options

- **watch_directory**: Directory to monitor for transcript files (default: `./transcripts`)
- **sentiment_threshold**: Threshold for flagging negative sentiment (0.0-1.0, default: 0.3)
- **task_backend**: Where to create tasks - "JIRA", "Trello", or "Markdown" (default: "Markdown")
- **notification_endpoint**: Slack channel ID or Teams webhook URL
- **markdown_output_file**: Output file for Markdown backend (default: `./tasks.md`)
- **summary_output_dir**: Directory for summary files (default: `./summaries`)
- **log_level**: Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: "INFO")

## API Credentials Setup

### JIRA

1. Generate an API token at https://id.atlassian.com/manage-profile/security/api-tokens
2. Set environment variables:

```bash
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_API_TOKEN="your_api_token"
export JIRA_PROJECT_KEY="TEAM"
```

### Trello

1. Get your API key at https://trello.com/app-key
2. Generate a token using the link on that page
3. Set environment variables:

```bash
export TRELLO_API_KEY="your_api_key"
export TRELLO_API_TOKEN="your_api_token"
export TRELLO_BOARD_ID="your_board_id"
export TRELLO_LIST_ID="your_list_id"
```

### Slack

1. Create a Slack app at https://api.slack.com/apps
2. Add the `chat:write` bot scope
3. Install the app to your workspace
4. Set environment variables:

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_CHANNEL_ID="C1234567890"
```

### Microsoft Teams

1. Create an incoming webhook in your Teams channel
2. Set environment variable:

```bash
export TEAMS_WEBHOOK_URL="https://your-company.webhook.office.com/webhookb2/..."
```

## Usage

### Web Dashboard

View processed meetings, summaries, and tasks in a web interface:

```bash
python run_dashboard.py
```

Then open your browser to: **http://localhost:5000**

Dashboard features:
- 📊 Statistics overview (meetings, action items, tasks, risks)
- 📝 List of all meeting summaries
- 🔍 View detailed summaries with formatted Markdown
- ✅ Browse all created tasks
- 🎨 Clean, modern interface

**Dashboard Options:**
```bash
python run_dashboard.py --host 0.0.0.0 --port 5000 --debug
```

### Watch Mode (Continuous Monitoring)

```bash
python -m meeting_router.main --config config.json
```

The system will continuously monitor the watch directory for new transcript files.

### Process Single File

```bash
python -m meeting_router.main --process-file transcripts/meeting_transcript_example.txt
```

### Command-Line Options

- `--config PATH`: Path to configuration file (JSON format)
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--process-file PATH`: Process a single transcript file instead of watching

## Transcript Format

Transcripts should be text files with speaker-identified dialogue:

```
Speaker Name: Dialogue text here.
Another Speaker: More dialogue.
Speaker Name: Continuation of dialogue
on multiple lines.
```

### Naming Convention

Transcript files must match the pattern: `meeting_transcript_*.txt`

Examples:
- `meeting_transcript_2024-01-15.txt`
- `meeting_transcript_standup_monday.txt`
- `meeting_transcript_planning_session.txt`

### Example Transcript

See `transcripts/meeting_transcript_example.txt` for a complete example.

## Action Item Patterns

The system recognizes the following commitment phrases:

- "I will..."
- "I'll..."
- "Need to..."
- "Let's follow up on..."
- "Someone should..."
- "We need to..."
- "I can..."
- "I should..."

## Decision Point Patterns

The system identifies decisions using these phrases:

- "We decided..."
- "The final choice is..."
- "We agreed..."
- "The decision is..."
- "We're going with..."

## Output

### Task Creation

Tasks are created in the configured backend with:
- **Title**: Action item description
- **Owner**: Speaker who made the commitment
- **Description**: Context quote from the transcript

### Summary Digest

A Markdown summary is generated containing:
- **Meeting timestamp**
- **Key Decisions**: Important decisions made during the meeting
- **Action Items**: List of tasks with owners and links
- **Risk Points**: Flagged discussions with negative sentiment

### Example Summary

```markdown
# Meeting Summary - 2024-01-15 14:30:00

## Key Decisions
- Decided to use PostgreSQL for the new feature database

## Action Items
- **Jane**: Finish the API integration by Friday
  - [TASK-1](https://example.com/TASK-1)
  - Context: "I will finish the API integration by Friday"

- **John Doe**: Review Jane's PR
  - [TASK-2](https://example.com/TASK-2)
  - Context: "I need to review Jane's PR"

## 🚨 Risk Points for Review
- **Sentiment Score: 0.25**
  - "we decided to use PostgreSQL for the new feature"
  - Context: Discussion showed concerns about migration complexity
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=meeting_router

# Run specific test file
pytest tests/test_parser_unit.py

# Run property-based tests
pytest tests/test_*_properties.py
```

## Logging

Logs are written to:
- Console (stdout)
- `meeting_router.log` file

Log entries include:
- Timestamp
- Component name
- Log level
- Message
- Correlation ID (file path) for tracking transcript processing

## Troubleshooting

### No action items detected

- Check that transcript uses recognized action phrases
- Verify speaker labels are in format "Speaker Name: text"
- Review logs for parsing errors

### Sentiment analysis not working

- Ensure `transformers` and `torch` are installed
- Check that sentiment model downloads successfully
- Review logs for model loading errors

### Task creation fails

- Verify API credentials are correct
- Check network connectivity
- Review logs for authentication errors
- Ensure project/board/list IDs are valid

### Notifications not posting

- Verify webhook URLs or bot tokens
- Check channel IDs are correct
- Review logs for API errors
- Check that fallback files are created in summary directory

## Architecture

The system follows a modular architecture:

1. **File Watcher**: Monitors directory for new transcripts
2. **Transcript Parser**: Extracts speaker segments
3. **NLP Processor**: Identifies action items and analyzes sentiment
4. **Task Router**: Creates tasks in configured backend
5. **Summary Generator**: Formats results as Markdown
6. **Notification Service**: Posts summaries to team channels

## Contributing

This project uses property-based testing with Hypothesis to ensure correctness. When adding features:

1. Update requirements in `requirements.md`
2. Add correctness properties to `design.md`
3. Implement property-based tests
4. Implement the feature
5. Run full test suite

## License

[Your License Here]

## Support

For issues or questions, please [open an issue](https://github.com/your-repo/issues).
