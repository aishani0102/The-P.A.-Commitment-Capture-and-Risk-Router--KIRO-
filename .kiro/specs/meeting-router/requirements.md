# Requirements Document

## Introduction

The Enhanced Meeting Router is an automation system designed to eliminate repetitive administrative tasks that follow team meetings. The system processes meeting transcripts to extract action items, detect potential risks through sentiment analysis, and automatically creates tasks in project management tools while notifying team members through communication platforms. This solution addresses the context-switching overhead and manual work involved in post-meeting administration.

## Glossary

- **Meeting Router**: The automated system that processes meeting transcripts and routes information to appropriate platforms
- **Transcript**: A text file containing speaker-identified meeting dialogue in the format "Speaker Name: dialogue text"
- **Action Item**: A commitment or task identified in the transcript that requires future work
- **Owner**: The person responsible for completing an action item, identified as the speaker who made the commitment
- **Risk Point**: A discussion segment flagged due to negative sentiment indicating potential disagreement or confusion
- **Sentiment Score**: A numerical value (0.0 to 1.0) representing the emotional tone of text, where lower values indicate negative sentiment
- **Summary Digest**: A formatted report containing meeting decisions, action items, and risk points
- **Task Backend**: The project management system (JIRA, Trello, or Markdown) where tasks are created
- **Notification Endpoint**: The Slack channel or Teams URL where the summary digest is posted

## Requirements

### Requirement 1

**User Story:** As a team member, I want the system to automatically detect when a new meeting transcript is available, so that I don't have to manually trigger the processing workflow.

#### Acceptance Criteria

1. WHEN a new text file matching the pattern "meeting_transcript_*.txt" is created in the monitored folder THEN the Meeting Router SHALL initiate the transcript processing workflow
2. WHEN monitoring the folder THEN the Meeting Router SHALL continuously watch for new file creation events without manual intervention
3. WHEN a file is detected THEN the Meeting Router SHALL read the complete file contents as a single text string
4. WHEN reading the transcript file THEN the Meeting Router SHALL handle files of varying sizes without memory errors
5. WHEN the file format is invalid or unreadable THEN the Meeting Router SHALL log an error and continue monitoring without crashing

### Requirement 2

**User Story:** As a team member, I want the system to extract action items from meeting transcripts, so that no commitments are forgotten or lost in lengthy discussions.

#### Acceptance Criteria

1. WHEN scanning transcript text THEN the Meeting Router SHALL identify phrases indicating commitment including "I will", "Need to", "Let's follow up on", and "Someone should"
2. WHEN an action item phrase is detected THEN the Meeting Router SHALL extract the complete task description from the surrounding context
3. WHEN an action item is identified THEN the Meeting Router SHALL determine the Owner as the speaker who made the commitment
4. WHEN multiple action items exist in a single speaker's statement THEN the Meeting Router SHALL extract each action item separately with the same owner
5. WHEN action item phrases appear in quoted or hypothetical contexts THEN the Meeting Router SHALL include them in extraction (conservative approach)

### Requirement 3

**User Story:** As a project manager, I want the system to detect potential risks in meeting discussions through sentiment analysis, so that I can proactively address areas of disagreement or confusion.

#### Acceptance Criteria

1. WHEN processing the transcript THEN the Meeting Router SHALL identify key discussion points containing phrases like "We decided", "The final choice is", "We agreed", and "The decision is"
2. WHEN a key discussion point is identified THEN the Meeting Router SHALL perform sentiment analysis on the surrounding sentences (preceding and following context)
3. WHEN the sentiment score is below the configured Sentiment Threshold THEN the Meeting Router SHALL flag the text segment as a Risk Point
4. WHEN flagging a Risk Point THEN the Meeting Router SHALL capture the complete context including the decision statement and surrounding dialogue
5. WHEN sentiment analysis fails for a segment THEN the Meeting Router SHALL log the error and continue processing remaining segments

### Requirement 4

**User Story:** As a system administrator, I want to configure the automation behavior through external parameters, so that the system can adapt to different team workflows and preferences.

#### Acceptance Criteria

1. WHEN the Meeting Router initializes THEN the system SHALL load configuration parameters from an external configuration file or environment variables
2. WHERE configuration is provided THEN the Meeting Router SHALL accept a Sentiment Threshold parameter as a decimal value between 0.0 and 1.0
3. WHERE configuration is provided THEN the Meeting Router SHALL accept a Task Backend parameter with valid values of "JIRA", "Trello", or "Markdown"
4. WHERE configuration is provided THEN the Meeting Router SHALL accept a Notification Endpoint parameter specifying the Slack channel ID or Teams webhook URL
5. WHEN required configuration parameters are missing THEN the Meeting Router SHALL use sensible default values and log a warning

### Requirement 5

**User Story:** As a team member, I want action items automatically created as tickets in our project management system, so that tasks are immediately trackable without manual data entry.

#### Acceptance Criteria

1. WHEN an action item is extracted THEN the Meeting Router SHALL create a new task in the configured Task Backend
2. WHEN creating a task THEN the Meeting Router SHALL populate the task title with a concise summary of the action item
3. WHEN creating a task THEN the Meeting Router SHALL assign the task to the identified Owner
4. WHEN creating a task THEN the Meeting Router SHALL populate the task description with the direct quote from the transcript as context
5. WHERE the Task Backend is "JIRA" THEN the Meeting Router SHALL use the JIRA REST API to create issues with appropriate authentication
6. WHERE the Task Backend is "Trello" THEN the Meeting Router SHALL use the Trello REST API to create cards with appropriate authentication
7. WHERE the Task Backend is "Markdown" THEN the Meeting Router SHALL append task entries to a local markdown file with timestamp and owner information
8. WHEN task creation fails for any action item THEN the Meeting Router SHALL log the error, continue processing remaining items, and include the failure in the summary digest

### Requirement 6

**User Story:** As a team member, I want to receive an organized summary of the meeting with links to created tasks, so that I have a single reference point for all meeting outcomes.

#### Acceptance Criteria

1. WHEN all action items are processed THEN the Meeting Router SHALL generate a Summary Digest in Markdown format
2. WHEN generating the Summary Digest THEN the Meeting Router SHALL include a high-level summary section containing key decisions from non-action-item text
3. WHEN generating the Summary Digest THEN the Meeting Router SHALL include a bulleted list of action items with owner names and direct links to created tasks
4. WHEN Risk Points are detected THEN the Meeting Router SHALL include a section titled "🚨 Risk Points for Review" containing the flagged text segments with context
5. WHEN the Summary Digest is complete THEN the Meeting Router SHALL post the digest to the configured Notification Endpoint
6. WHERE the Notification Endpoint is a Slack channel THEN the Meeting Router SHALL use the Slack Web API to post the formatted message
7. WHERE the Notification Endpoint is a Teams webhook THEN the Meeting Router SHALL use the Teams webhook API to post the formatted message
8. WHEN posting the digest fails THEN the Meeting Router SHALL save the digest to a local file and log the error

### Requirement 7

**User Story:** As a developer, I want the system to handle errors gracefully and provide clear logging, so that I can troubleshoot issues and ensure reliable operation.

#### Acceptance Criteria

1. WHEN any processing step encounters an error THEN the Meeting Router SHALL log the error with timestamp, context, and error details
2. WHEN an error occurs THEN the Meeting Router SHALL continue processing subsequent steps where possible rather than terminating completely
3. WHEN API calls fail due to authentication errors THEN the Meeting Router SHALL log specific authentication failure messages
4. WHEN API calls fail due to rate limiting THEN the Meeting Router SHALL implement exponential backoff retry logic up to three attempts
5. WHEN the transcript file contains no identifiable action items THEN the Meeting Router SHALL generate a summary digest indicating no action items were found

### Requirement 8

**User Story:** As a team member, I want the system to parse speaker-identified transcripts correctly, so that action items are attributed to the right people.

#### Acceptance Criteria

1. WHEN parsing transcript text THEN the Meeting Router SHALL recognize speaker labels in the format "Speaker Name: dialogue text"
2. WHEN parsing transcript text THEN the Meeting Router SHALL handle various speaker name formats including "Speaker 1", "Jane", "John Doe", and "J. Smith"
3. WHEN a speaker label is followed by multiple sentences THEN the Meeting Router SHALL attribute all text until the next speaker label to that speaker
4. WHEN speaker labels are inconsistent or missing THEN the Meeting Router SHALL handle the text gracefully and mark action items with "Unknown" owner
5. WHEN extracting owner information THEN the Meeting Router SHALL normalize speaker names for consistent task assignment
