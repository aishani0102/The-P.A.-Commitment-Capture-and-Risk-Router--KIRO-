# Meeting Router - Complete Pipeline Workflow

## 🔄 End-to-End Processing Pipeline

```mermaid
flowchart TD
    Start([New Transcript File]) --> Watch{Watch Mode?}
    
    Watch -->|Yes| Watcher[File Watcher<br/>Monitors Directory]
    Watch -->|No| Direct[Direct File Processing]
    
    Watcher -->|Detects New File| Process[Process Transcript]
    Direct --> Process
    
    Process --> Read[Read Transcript File]
    Read --> Parse[Parse Transcript<br/>Extract Speaker Segments]
    
    Parse --> NLP{NLP Processing}
    
    NLP --> Extract[Action Item Extraction<br/>Pattern Matching]
    NLP --> Sentiment[Sentiment Analysis<br/>Risk Detection]
    
    Extract --> Actions[Action Items List]
    Sentiment --> Risks[Risk Points List]
    
    Actions --> CreateTasks[Create Tasks]
    
    CreateTasks --> Backend{Task Backend?}
    
    Backend -->|Markdown| MD[Write to tasks.md]
    Backend -->|JIRA| JIRA[Create JIRA Issues]
    Backend -->|Trello| Trello[Create Trello Cards]
    
    MD --> TaskList[Created Tasks List]
    JIRA --> TaskList
    Trello --> TaskList
    
    TaskList --> Summary[Generate Summary<br/>Markdown Format]
    Risks --> Summary
    
    Summary --> Notify{Notification Service?}
    
    Notify -->|Slack| SlackPost[Post to Slack Channel]
    Notify -->|Teams| TeamsPost[Post to Teams Webhook]
    Notify -->|File/Fallback| FilePost[Save to summaries/]
    
    SlackPost --> Complete([Processing Complete])
    TeamsPost --> Complete
    FilePost --> Complete
    
    Complete --> Dashboard[Dashboard Displays Results]
    
    style Start fill:#90EE90
    style Complete fill:#87CEEB
    style Dashboard fill:#FFD700
    style NLP fill:#FFB6C1
    style Backend fill:#DDA0DD
    style Notify fill:#F0E68C
```

---

## 📊 Detailed Component Workflow

### 1. File Watching & Ingestion

```mermaid
sequenceDiagram
    participant User
    participant FileWatcher
    participant Orchestrator
    participant FileSystem
    
    User->>FileSystem: Drop transcript file<br/>(meeting_transcript_*.txt)
    FileWatcher->>FileSystem: Monitor directory
    FileSystem-->>FileWatcher: File detected
    FileWatcher->>FileWatcher: Validate filename pattern
    FileWatcher->>Orchestrator: Trigger process_transcript()
    Orchestrator->>FileSystem: Read file content
    FileSystem-->>Orchestrator: Return transcript text
```

**Key Points:**
- Watches configured directory (default: `./transcripts`)
- Only processes files matching pattern: `meeting_transcript_*.txt`
- Triggers processing automatically on new file detection
- Can also process single files directly via CLI

---

### 2. Transcript Parsing

```mermaid
flowchart LR
    A[Raw Transcript Text] --> B[TranscriptParser]
    B --> C{Line Matches<br/>Speaker Pattern?}
    C -->|Yes| D[Start New Segment]
    C -->|No| E[Continue Current Segment]
    D --> F[SpeakerSegment Object]
    E --> F
    F --> G[List of Speaker Segments]
    
    style A fill:#E6E6FA
    style G fill:#98FB98
```

**Pattern Recognition:**
```
Speaker Name: Dialogue text here.
```

**Output Structure:**
```python
SpeakerSegment(
    speaker="John Doe",
    text="I will complete the report by Friday",
    start_position=125
)
```

---

### 3. NLP Processing Pipeline

```mermaid
flowchart TD
    Segments[Speaker Segments] --> Split{Split Processing}
    
    Split --> Path1[Action Item Extraction]
    Split --> Path2[Sentiment Analysis]
    
    Path1 --> Patterns[Pattern Matching]
    Patterns --> P1["I will..."]
    Patterns --> P2["I'll..."]
    Patterns --> P3["Need to..."]
    Patterns --> P4["We need to..."]
    Patterns --> P5["Someone should..."]
    
    P1 --> ActionItems[Action Items]
    P2 --> ActionItems
    P3 --> ActionItems
    P4 --> ActionItems
    P5 --> ActionItems
    
    Path2 --> FindDecisions[Find Decision Points]
    FindDecisions --> D1["We decided..."]
    FindDecisions --> D2["We agreed..."]
    FindDecisions --> D3["The decision is..."]
    
    D1 --> Model[Sentiment Model<br/>DistilBERT]
    D2 --> Model
    D3 --> Model
    
    Model --> Score{Score < Threshold?}
    Score -->|Yes| RiskPoints[Risk Points]
    Score -->|No| Ignore[Ignore]
    
    ActionItems --> Output[NLP Results]
    RiskPoints --> Output
    
    style ActionItems fill:#90EE90
    style RiskPoints fill:#FFB6C1
    style Output fill:#87CEEB
```

**Action Item Extraction:**
- Uses regex pattern matching
- Identifies commitment phrases
- Extracts owner, task description, and context

**Sentiment Analysis:**
- Identifies decision points in transcript
- Analyzes surrounding context (±2 sentences)
- Uses DistilBERT model for sentiment scoring
- Flags decisions with negative sentiment as risks

---

### 4. Task Creation Flow

```mermaid
flowchart TD
    ActionItems[Action Items] --> Loop{For Each<br/>Action Item}
    
    Loop --> Backend{Backend Type?}
    
    Backend -->|Markdown| MD[Markdown Backend]
    Backend -->|JIRA| JB[JIRA Backend]
    Backend -->|Trello| TB[Trello Backend]
    
    MD --> MD1[Generate Task ID]
    MD1 --> MD2[Append to tasks.md]
    MD2 --> MD3[Create File URL]
    MD3 --> Task1[CreatedTask Object]
    
    JB --> JB1[Initialize JIRA Client]
    JB1 --> JB2[Create Issue via API]
    JB2 --> JB3[Get Issue Key & URL]
    JB3 --> Task2[CreatedTask Object]
    
    TB --> TB1[Initialize Trello Client]
    TB1 --> TB2[Create Card via API]
    TB2 --> TB3[Get Card ID & URL]
    TB3 --> Task3[CreatedTask Object]
    
    Task1 --> Collect[Collect All Tasks]
    Task2 --> Collect
    Task3 --> Collect
    
    Collect --> Error{Any Errors?}
    Error -->|Yes| Placeholder[Create Error Placeholder]
    Error -->|No| Continue[Continue Processing]
    
    Placeholder --> TaskList[Created Tasks List]
    Continue --> TaskList
    
    style MD fill:#FFE4B5
    style JB fill:#B0E0E6
    style TB fill:#DDA0DD
    style TaskList fill:#90EE90
```

**Error Handling:**
- If task creation fails, creates placeholder with "ERROR" ID
- Processing continues for remaining tasks
- Errors logged but don't stop pipeline

---

### 5. Summary Generation

```mermaid
flowchart LR
    Input[Processing Results] --> Header[Generate Header<br/>with Timestamp]
    Header --> Decisions[Extract Key Decisions<br/>Pattern Matching]
    Decisions --> Actions[Format Action Items<br/>with Task Links]
    Actions --> Risks{Risk Points<br/>Exist?}
    Risks -->|Yes| RiskSection[Add Risk Section]
    Risks -->|No| Skip[Skip Risk Section]
    RiskSection --> Combine[Combine Sections]
    Skip --> Combine
    Combine --> Markdown[Markdown Summary]
    
    style Input fill:#E6E6FA
    style Markdown fill:#90EE90
```

**Summary Structure:**
```markdown
# Meeting Summary - 2024-12-05 14:30:00

## Key Decisions
- Decided to use PostgreSQL for the database

## Action Items
- **John Doe**: Complete the API integration
  - [task_20241205_143000](file://tasks.md#task_20241205_143000)
  - Context: "I will complete the API integration by Friday"

## 🚨 Risk Points for Review
- **Sentiment Score: 0.25**
  - "we decided to use PostgreSQL"
  - Context: Discussion showed concerns about migration
```

---

### 6. Notification & Storage

```mermaid
flowchart TD
    Summary[Markdown Summary] --> Check{Notification<br/>Configured?}
    
    Check -->|Slack| Slack[Slack Service]
    Check -->|Teams| Teams[Teams Service]
    Check -->|None/File| File[File Service]
    
    Slack --> S1[Convert to Slack mrkdwn]
    S1 --> S2[Post via Slack API]
    S2 --> S3{Success?}
    S3 -->|No| Fallback1[Fallback to File]
    S3 -->|Yes| Done1[Complete]
    
    Teams --> T1[Create Adaptive Card]
    T1 --> T2[Post to Webhook]
    T2 --> T3{Success?}
    T3 -->|No| Fallback2[Fallback to File]
    T3 -->|Yes| Done2[Complete]
    
    File --> F1[Generate Filename<br/>summary_YYYYMMDD_HHMMSS.md]
    F1 --> F2[Save to summaries/]
    F2 --> Done3[Complete]
    
    Fallback1 --> F1
    Fallback2 --> F1
    
    Done1 --> Store[Summary Stored]
    Done2 --> Store
    Done3 --> Store
    
    style Store fill:#90EE90
    style Fallback1 fill:#FFB6C1
    style Fallback2 fill:#FFB6C1
```

**Retry Logic:**
- 3 retry attempts with exponential backoff (1s, 2s, 4s)
- Automatic fallback to file storage on failure
- Ensures no data loss

---

### 7. Dashboard Display

```mermaid
flowchart TD
    User[User Opens Browser] --> Dashboard[Flask Dashboard<br/>Port 8000]
    
    Dashboard --> Routes{Route?}
    
    Routes -->|/| Home[Home Page]
    Routes -->|/summary/:id| Detail[Summary Detail]
    Routes -->|/tasks| Tasks[Tasks View]
    
    Home --> H1[Read summaries/ directory]
    H1 --> H2[Parse summary files]
    H2 --> H3[Calculate statistics]
    H3 --> H4[Render home template]
    
    Detail --> D1[Read specific summary]
    D1 --> D2[Convert Markdown to HTML]
    D2 --> D3[Render detail template]
    
    Tasks --> T1[Read tasks.md]
    T1 --> T2[Parse task entries]
    T2 --> T3[Render tasks template]
    
    H4 --> Display[Display to User]
    D3 --> Display
    T3 --> Display
    
    style Dashboard fill:#FFD700
    style Display fill:#87CEEB
```

**Dashboard Features:**
- **Statistics Cards**: Total meetings, action items, tasks, risks
- **Summary List**: All processed meetings with timestamps
- **Detail View**: Full formatted summary with Markdown rendering
- **Tasks View**: Table of all created tasks

---

## 🔍 Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input
        T[Transcript File]
    end
    
    subgraph Processing
        P[Parser] --> E[Extractor]
        E --> S[Sentiment]
        S --> B[Backend]
    end
    
    subgraph Storage
        TM[tasks.md]
        SM[summaries/]
        J[JIRA/Trello]
    end
    
    subgraph Output
        D[Dashboard]
        N[Notifications]
    end
    
    T --> P
    B --> TM
    B --> J
    S --> SM
    SM --> D
    SM --> N
    TM --> D
    J --> D
    
    style Input fill:#E6E6FA
    style Processing fill:#FFE4B5
    style Storage fill:#90EE90
    style Output fill:#87CEEB
```

---

## ⚙️ Configuration Flow

```mermaid
flowchart TD
    Start([Application Start]) --> Load{Config Source?}
    
    Load -->|config.json| File[Load from File]
    Load -->|Environment| Env[Load from ENV vars]
    Load -->|None| Default[Use Defaults]
    
    File --> Merge[Merge Configuration]
    Env --> Merge
    Default --> Merge
    
    Merge --> Validate[Validate Settings]
    
    Validate --> Backend{Task Backend?}
    Backend -->|Markdown| BM[Initialize Markdown]
    Backend -->|JIRA| BJ[Initialize JIRA<br/>Check Credentials]
    Backend -->|Trello| BT[Initialize Trello<br/>Check Credentials]
    
    BJ --> CredCheck{Credentials<br/>Valid?}
    BT --> CredCheck
    CredCheck -->|No| Fallback[Fallback to Markdown]
    CredCheck -->|Yes| Continue
    
    BM --> Continue[Continue Initialization]
    Fallback --> Continue
    
    Continue --> Notify{Notification?}
    Notify -->|Slack| NS[Initialize Slack Client]
    Notify -->|Teams| NT[Initialize Teams Webhook]
    Notify -->|None| NF[Use File Service]
    
    NS --> Ready
    NT --> Ready
    NF --> Ready[System Ready]
    
    style Start fill:#90EE90
    style Ready fill:#87CEEB
    style Fallback fill:#FFB6C1
```

---

## 🎯 Complete System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        Browser[Web Browser]
        CLI[Command Line]
    end
    
    subgraph "Application Layer"
        Dashboard[Flask Dashboard<br/>Port 8000]
        Main[Main Entry Point]
        Orchestrator[Meeting Router<br/>Orchestrator]
    end
    
    subgraph "Processing Layer"
        Parser[Transcript Parser]
        Extractor[Action Item Extractor]
        Sentiment[Sentiment Analyzer]
        Summary[Summary Generator]
    end
    
    subgraph "Integration Layer"
        MarkdownB[Markdown Backend]
        JiraB[JIRA Backend]
        TrelloB[Trello Backend]
        SlackN[Slack Notifier]
        TeamsN[Teams Notifier]
        FileN[File Notifier]
    end
    
    subgraph "Storage Layer"
        FS[File System]
        Transcripts[(transcripts/)]
        Summaries[(summaries/)]
        Tasks[(tasks.md)]
    end
    
    subgraph "External Services"
        JIRA[JIRA API]
        Trello[Trello API]
        Slack[Slack API]
        Teams[Teams Webhook]
    end
    
    Browser --> Dashboard
    CLI --> Main
    Main --> Orchestrator
    Dashboard --> Summaries
    Dashboard --> Tasks
    
    Orchestrator --> Parser
    Orchestrator --> Extractor
    Orchestrator --> Sentiment
    Orchestrator --> Summary
    
    Parser --> Extractor
    Extractor --> MarkdownB
    Extractor --> JiraB
    Extractor --> TrelloB
    
    Summary --> SlackN
    Summary --> TeamsN
    Summary --> FileN
    
    MarkdownB --> Tasks
    JiraB --> JIRA
    TrelloB --> Trello
    
    SlackN --> Slack
    TeamsN --> Teams
    FileN --> Summaries
    
    Transcripts --> Parser
    
    style Browser fill:#FFD700
    style Dashboard fill:#FFD700
    style Orchestrator fill:#87CEEB
    style FS fill:#90EE90
```

---

## 📝 Processing States

```mermaid
stateDiagram-v2
    [*] --> Idle: System Started
    
    Idle --> Watching: Start Watch Mode
    Idle --> Processing: Process Single File
    
    Watching --> FileDetected: New File Found
    FileDetected --> Processing: Begin Processing
    
    Processing --> Parsing: Read File
    Parsing --> Extracting: Parse Segments
    Extracting --> Analyzing: Extract Actions
    Analyzing --> Creating: Analyze Sentiment
    Creating --> Summarizing: Create Tasks
    Summarizing --> Notifying: Generate Summary
    Notifying --> Complete: Post Notification
    
    Complete --> Watching: Return to Watch
    Complete --> Idle: Single File Done
    
    Processing --> Error: Exception Occurred
    Error --> Logging: Log Error
    Logging --> Watching: Continue Watch
    Logging --> Idle: Single File Failed
    
    state Processing {
        [*] --> ReadFile
        ReadFile --> ParseTranscript
        ParseTranscript --> ExtractActions
        ExtractActions --> AnalyzeSentiment
        AnalyzeSentiment --> CreateTasks
        CreateTasks --> GenerateSummary
        GenerateSummary --> PostNotification
        PostNotification --> [*]
    }
```

---

## 🚦 Error Handling Flow

```mermaid
flowchart TD
    Process[Processing Step] --> Try{Try Operation}
    
    Try -->|Success| Next[Continue to Next Step]
    Try -->|Error| Log[Log Error]
    
    Log --> Critical{Critical<br/>Error?}
    
    Critical -->|Yes| Stop[Stop Processing]
    Critical -->|No| Fallback{Fallback<br/>Available?}
    
    Fallback -->|Yes| UseFallback[Use Fallback]
    Fallback -->|No| Continue[Continue with Partial Results]
    
    UseFallback --> Next
    Continue --> Next
    
    Stop --> SaveState[Save Partial Results]
    SaveState --> Notify[Notify User]
    
    style Log fill:#FFB6C1
    style Stop fill:#FF6B6B
    style Next fill:#90EE90
```

**Error Handling Strategy:**
- **Non-Critical Errors**: Log and continue (e.g., single task creation failure)
- **Critical Errors**: Stop processing, save state, notify user
- **Fallback Mechanisms**: Markdown backend, file notifications
- **Retry Logic**: 3 attempts with exponential backoff for API calls

---

## 📊 Performance Metrics

```mermaid
flowchart LR
    Input[Transcript File] --> M1[File Read Time]
    M1 --> M2[Parse Time]
    M2 --> M3[NLP Processing Time]
    M3 --> M4[Task Creation Time]
    M4 --> M5[Summary Generation Time]
    M5 --> M6[Notification Time]
    M6 --> Output[Total Processing Time]
    
    style Input fill:#E6E6FA
    style Output fill:#90EE90
```

**Typical Processing Times:**
- File Read: < 100ms
- Parsing: 100-500ms
- NLP Processing: 1-3 seconds (sentiment model)
- Task Creation: 100ms-2s (depends on backend)
- Summary Generation: < 100ms
- Notification: 500ms-2s (API calls)

**Total**: ~3-8 seconds per transcript

---

## 🔄 Watch Mode Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Watcher
    participant Orchestrator
    participant FileSystem
    
    User->>CLI: python -m meeting_router.main
    CLI->>Watcher: start_watching()
    Watcher->>FileSystem: Monitor ./transcripts
    
    Note over Watcher,FileSystem: Continuous monitoring...
    
    User->>FileSystem: Add transcript file
    FileSystem-->>Watcher: File created event
    Watcher->>Watcher: Validate filename
    Watcher->>Orchestrator: process_transcript(path)
    
    Orchestrator->>Orchestrator: Complete processing pipeline
    Orchestrator-->>Watcher: Processing complete
    
    Note over Watcher,FileSystem: Resume monitoring...
    
    User->>CLI: Ctrl+C
    CLI->>Watcher: stop()
    Watcher->>Watcher: Cleanup
    Watcher-->>CLI: Stopped
    CLI-->>User: Exit
```

---

## 🎯 Quick Reference

### Input
- **Format**: Text file with speaker labels
- **Pattern**: `meeting_transcript_*.txt`
- **Location**: `./transcripts/` directory

### Processing
- **Parser**: Extracts speaker segments
- **Extractor**: Identifies action items (8 patterns)
- **Analyzer**: Detects risks (sentiment < threshold)

### Output
- **Tasks**: Markdown file, JIRA issues, or Trello cards
- **Summary**: Markdown file in `./summaries/`
- **Notifications**: Slack, Teams, or file

### Access
- **Dashboard**: http://localhost:8000
- **Logs**: `meeting_router.log`
- **Tasks**: `tasks.md`

---

## 🔧 Customization Points

```mermaid
mindmap
  root((Meeting Router))
    Configuration
      Watch Directory
      Sentiment Threshold
      Log Level
    Task Backend
      Markdown
      JIRA
      Trello
    Notifications
      Slack
      Teams
      File
    NLP Patterns
      Action Phrases
      Decision Phrases
    Output Format
      Summary Template
      Task Format
```

