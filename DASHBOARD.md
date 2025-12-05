# Meeting Router Dashboard 🎯

A beautiful web interface for viewing meeting summaries, tasks, and statistics.

## Features

### 📊 Statistics Dashboard
- **Total Meetings**: Count of processed transcripts
- **Action Items**: Total action items extracted
- **Tasks Created**: Number of tasks in the system
- **Risk Points**: Discussions flagged for review

### 📝 Meeting Summaries
- View all processed meeting summaries
- See action item counts at a glance
- Identify meetings with risk points
- Click to view full formatted summaries

### ✅ Tasks View
- Browse all created tasks in a table
- See task IDs, owners, descriptions, and timestamps
- Filter and search capabilities

### 🎨 Modern UI
- Clean, professional design
- Responsive layout (works on mobile)
- Smooth animations and transitions
- Color-coded badges and indicators

## Quick Start

### 1. Generate Demo Data

```bash
python demo.py
```

This creates sample summaries and tasks so you can see the dashboard in action immediately.

### 2. Start the Dashboard

```bash
python run_dashboard.py
```

### 3. Open Your Browser

Navigate to: **http://localhost:5000**

## Dashboard Pages

### Home (`/`)
The main dashboard showing:
- Statistics cards at the top
- List of recent meeting summaries
- Quick access to view each summary

### Summary View (`/summary/<filename>`)
Detailed view of a specific meeting summary:
- Formatted Markdown rendering
- Key decisions highlighted
- Action items with owner names
- Risk points (if any)
- Raw Markdown source

### Tasks (`/tasks`)
Table view of all tasks:
- Task ID (clickable)
- Owner name
- Task description
- Creation timestamp

## API Endpoints

The dashboard also provides JSON API endpoints:

### `GET /api/summaries`
Returns all summaries with metadata:
```json
[
  {
    "filename": "summary_20240115_090000.md",
    "timestamp": "2024-01-15 09:00:00",
    "action_items_count": 4,
    "has_risks": true,
    "content": "..."
  }
]
```

### `GET /api/summary/<filename>`
Returns a specific summary:
```json
{
  "filename": "summary_20240115_090000.md",
  "content": "# Meeting Summary...",
  "html": "<h1>Meeting Summary...</h1>"
}
```

### `GET /api/tasks`
Returns all tasks:
```json
[
  {
    "task_id": "task_20240115_090000_001",
    "owner": "Alice",
    "task": "Complete the report",
    "context": "I will complete the report",
    "created": "2024-01-15 09:00:00"
  }
]
```

### `GET /api/statistics`
Returns overall statistics:
```json
{
  "total_meetings": 3,
  "total_action_items": 12,
  "total_tasks": 9,
  "total_risks": 2,
  "transcripts_processed": 3
}
```

## Configuration

The dashboard reads from:
- `./summaries/` - Meeting summary files
- `./tasks.md` - Task list (Markdown backend)
- `./transcripts/` - Processed transcript files

You can customize these paths in `meeting_router/dashboard.py`:

```python
dashboard_data = DashboardData(
    summary_dir="./summaries",
    tasks_file="./tasks.md",
    transcripts_dir="./transcripts"
)
```

## Running Options

### Default (localhost:5000)
```bash
python run_dashboard.py
```

### Custom Port
```bash
python run_dashboard.py --port 8080
```

### Accessible from Network
```bash
python run_dashboard.py --host 0.0.0.0
```

### Debug Mode
```bash
python run_dashboard.py --debug
```

### All Options
```bash
python run_dashboard.py --host 0.0.0.0 --port 8080 --debug
```

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, vanilla JavaScript
- **Markdown Rendering**: Python-Markdown library
- **Styling**: Custom CSS with modern design patterns

## Design Philosophy

The dashboard follows these principles:

1. **Simplicity**: Clean, uncluttered interface
2. **Speed**: Fast loading, minimal dependencies
3. **Accessibility**: Works on all devices and screen sizes
4. **Clarity**: Information is easy to find and understand
5. **Beauty**: Professional appearance with smooth animations

## Browser Support

Works on all modern browsers:
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## Screenshots

### Dashboard Home
- Statistics cards showing key metrics
- List of recent meetings with badges
- Clean, card-based layout

### Summary View
- Formatted Markdown with proper styling
- Syntax highlighting for code blocks
- Clear section headers
- Risk points prominently displayed

### Tasks View
- Sortable table of all tasks
- Easy to scan and find information
- Responsive design

## Extending the Dashboard

### Add New Pages

1. Create a new route in `dashboard.py`:
```python
@app.route('/my-page')
def my_page():
    return render_template('my_page.html')
```

2. Create the template in `templates/my_page.html`

3. Add navigation link in `base.html`

### Add New API Endpoints

```python
@app.route('/api/my-endpoint')
def api_my_endpoint():
    data = {"key": "value"}
    return jsonify(data)
```

### Customize Styling

Edit `templates/base.html` and modify the `<style>` section.

## Troubleshooting

### Dashboard won't start
- Check that Flask is installed: `pip install flask`
- Verify port 5000 is not in use
- Try a different port: `--port 8080`

### No data showing
- Run `python demo.py` to generate sample data
- Check that `summaries/` directory exists
- Verify files are in the correct format

### Styling looks broken
- Clear browser cache
- Check browser console for errors
- Verify templates are in `meeting_router/templates/`

## Future Enhancements

Potential additions:
- 🔍 Search and filter functionality
- 📈 Charts and graphs for trends
- 🔔 Real-time updates via WebSockets
- 👥 User authentication
- 📱 Progressive Web App (PWA) support
- 🌙 Dark mode toggle
- 📊 Export to PDF/Excel
- 🔗 Integration with calendar apps

## Contributing

To add features to the dashboard:

1. Modify `meeting_router/dashboard.py` for backend logic
2. Update templates in `meeting_router/templates/`
3. Test thoroughly
4. Update this documentation

Enjoy your Meeting Router Dashboard! 🚀
