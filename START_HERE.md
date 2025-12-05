# 🚀 Start Here - Meeting Router Dashboard

Welcome! Here's how to get your dashboard running in **2 minutes**.

## Option 1: Quick Demo (Recommended)

See the dashboard with sample data immediately:

```bash
# Step 1: Install Flask
pip install flask markdown

# Step 2: Generate demo data
python demo.py

# Step 3: Start dashboard
python run_dashboard.py
```

**Open browser to: http://localhost:5000** 🎉

You'll see:
- ✅ 3 meeting summaries
- ✅ 9 tasks
- ✅ 2 risk points
- ✅ Beautiful statistics dashboard

## Option 2: Process Real Transcript

Process the included example transcript:

```bash
# Step 1: Install minimal dependencies
pip install flask markdown

# Step 2: Process example
python -m meeting_router.main --process-file transcripts/meeting_transcript_example.txt

# Step 3: Start dashboard
python run_dashboard.py
```

**Open browser to: http://localhost:5000**

## What You'll See

### 📊 Dashboard Home
- Statistics cards (meetings, action items, tasks, risks)
- List of meeting summaries
- Click "View Summary" to see details

### 📝 Summary View
- Formatted meeting summary
- Key decisions
- Action items with owners
- Risk points (if any)

### ✅ Tasks View
- Table of all tasks
- Owner, description, timestamps

## Next Steps

### Add Your Own Meetings

1. Create a transcript file:
   ```
   transcripts/meeting_transcript_mymeeting.txt
   ```

2. Format with speaker labels:
   ```
   Alice: I will complete the report by Friday.
   Bob: Need to review the code.
   ```

3. Process it:
   ```bash
   python -m meeting_router.main --process-file transcripts/meeting_transcript_mymeeting.txt
   ```

4. Refresh dashboard to see new summary!

### Enable Auto-Processing

Run in watch mode to automatically process new transcripts:

```bash
python -m meeting_router.main --config config.json
```

Drop any `meeting_transcript_*.txt` file in the `transcripts/` folder and it will be processed automatically!

## Troubleshooting

### "Module not found" error
Install Flask:
```bash
pip install flask markdown
```

### Port 5000 in use
Use a different port:
```bash
python run_dashboard.py --port 8080
```

### No summaries showing
1. Run `python demo.py` to generate sample data
2. Or process a transcript first
3. Refresh the browser

## Documentation

- **QUICKSTART.md** - Detailed getting started guide
- **DASHBOARD.md** - Complete dashboard documentation
- **README.md** - Full system documentation

## Features

✨ **Automatic Processing**: Drop transcript files and they're processed automatically  
📊 **Statistics**: See metrics at a glance  
📝 **Summaries**: Beautiful formatted meeting summaries  
✅ **Tasks**: Track all action items  
⚠️ **Risk Detection**: Identify potential issues through sentiment analysis  
🎨 **Modern UI**: Clean, responsive design  

## Support

Having issues? Check:
1. Python 3.9+ is installed
2. Flask is installed (`pip install flask markdown`)
3. Files are in the correct directories
4. Port 5000 is available

Enjoy your automated meeting management! 🎯
