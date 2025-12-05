# Quick Start Guide

Get the Meeting Router dashboard up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install flask markdown
```

(The full dependencies can be installed later with `pip install -r requirements.txt`)

## Step 2: Process the Example Transcript

```bash
python -m meeting_router.main --process-file transcripts/meeting_transcript_example.txt
```

This will:
- ✅ Parse the example meeting transcript
- ✅ Extract action items
- ✅ Create tasks in `tasks.md`
- ✅ Generate a summary in `summaries/`

## Step 3: Start the Dashboard

```bash
python run_dashboard.py
```

## Step 4: Open Your Browser

Navigate to: **http://localhost:5000**

You should see:
- 📊 Statistics showing 1 meeting processed
- 📝 The generated summary
- ✅ All extracted tasks

## What You'll See

### Dashboard Home
- **Total Meetings**: Number of transcripts processed
- **Action Items**: Total action items extracted
- **Tasks Created**: Tasks in your task management system
- **Risk Points**: Discussions flagged for review

### Meeting Summaries
Each summary shows:
- Meeting timestamp
- Key decisions made
- Action items with owners and links
- Risk points (if any negative sentiment detected)

### Tasks View
A table of all tasks with:
- Task ID
- Owner
- Task description
- Creation timestamp

## Next Steps

### Process Your Own Transcripts

1. Create a transcript file in the `transcripts/` folder:
   ```
   transcripts/meeting_transcript_2024-01-15.txt
   ```

2. Format it with speaker labels:
   ```
   Alice: I will complete the report by Friday.
   Bob: Need to review the code changes.
   ```

3. Process it:
   ```bash
   python -m meeting_router.main --process-file transcripts/meeting_transcript_2024-01-15.txt
   ```

4. Refresh the dashboard to see the new summary!

### Enable Continuous Monitoring

Run in watch mode to automatically process new transcripts:

```bash
python -m meeting_router.main --config config.json
```

Now any file matching `meeting_transcript_*.txt` added to the `transcripts/` folder will be automatically processed!

### Configure Task Backends

Edit `config.json` to use JIRA or Trello instead of Markdown:

```json
{
  "task_backend": "JIRA",
  "jira": {
    "url": "https://your-company.atlassian.net",
    "api_token": "your_token",
    "project_key": "TEAM"
  }
}
```

See the main README.md for full configuration options.

## Troubleshooting

### Dashboard shows no summaries
- Make sure you've processed at least one transcript
- Check that the `summaries/` directory exists
- Verify files are being created in `summaries/`

### Port 5000 already in use
Run on a different port:
```bash
python run_dashboard.py --port 8080
```

### Can't access from other machines
Bind to all interfaces:
```bash
python run_dashboard.py --host 0.0.0.0
```

## Tips

- 💡 The dashboard auto-refreshes when you reload the page
- 💡 Summaries are sorted newest first
- 💡 Click "View Summary" to see the full formatted report
- 💡 The dashboard works great on mobile devices too!

Enjoy your automated meeting management! 🎉
