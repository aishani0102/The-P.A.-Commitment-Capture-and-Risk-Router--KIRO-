"""Web dashboard for Meeting Router."""

from flask import Flask, render_template, jsonify, send_from_directory
import os
import json
from datetime import datetime
from pathlib import Path
import markdown
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)


class DashboardData:
    """Manages data for the dashboard."""
    
    def __init__(self, summary_dir="./summaries", tasks_file="./tasks.md", transcripts_dir="./transcripts"):
        self.summary_dir = summary_dir
        self.tasks_file = tasks_file
        self.transcripts_dir = transcripts_dir
    
    def get_summaries(self):
        """Get all summary files with metadata."""
        summaries = []
        
        if not os.path.exists(self.summary_dir):
            return summaries
        
        for filename in os.listdir(self.summary_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.summary_dir, filename)
                
                # Extract timestamp from filename (format: summary_YYYYMMDD_HHMMSS.md)
                try:
                    timestamp_str = filename.replace('summary_', '').replace('.md', '')
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                except:
                    timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                # Read file content
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Extract key info
                action_items_count = content.count('**') // 2  # Rough estimate
                has_risks = '🚨' in content or 'Risk Points' in content
                
                summaries.append({
                    'filename': filename,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'timestamp_iso': timestamp.isoformat(),
                    'action_items_count': action_items_count,
                    'has_risks': has_risks,
                    'content': content
                })
        
        # Sort by timestamp, newest first
        summaries.sort(key=lambda x: x['timestamp_iso'], reverse=True)
        
        return summaries
    
    def get_summary_content(self, filename):
        """Get content of a specific summary file."""
        filepath = os.path.join(self.summary_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        return content
    
    def get_tasks(self):
        """Get all tasks from the tasks file."""
        if not os.path.exists(self.tasks_file):
            return []
        
        tasks = []
        
        with open(self.tasks_file, 'r') as f:
            content = f.read()
        
        # Parse markdown tasks
        lines = content.split('\n')
        current_task = None
        
        for line in lines:
            if line.startswith('## task_'):
                if current_task:
                    tasks.append(current_task)
                
                task_id = line.replace('## ', '').strip()
                current_task = {
                    'task_id': task_id,
                    'owner': '',
                    'task': '',
                    'context': '',
                    'created': ''
                }
            elif current_task and line.startswith('- **Owner**:'):
                current_task['owner'] = line.replace('- **Owner**:', '').strip()
            elif current_task and line.startswith('- **Task**:'):
                current_task['task'] = line.replace('- **Task**:', '').strip()
            elif current_task and line.startswith('- **Context**:'):
                current_task['context'] = line.replace('- **Context**:', '').strip()
            elif current_task and line.startswith('- **Created**:'):
                current_task['created'] = line.replace('- **Created**:', '').strip()
        
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def get_statistics(self):
        """Get overall statistics."""
        summaries = self.get_summaries()
        tasks = self.get_tasks()
        
        total_action_items = sum(s['action_items_count'] for s in summaries)
        total_risks = sum(1 for s in summaries if s['has_risks'])
        
        # Count transcripts processed
        transcripts_count = 0
        if os.path.exists(self.transcripts_dir):
            transcripts_count = len([f for f in os.listdir(self.transcripts_dir) if f.startswith('meeting_transcript_')])
        
        return {
            'total_meetings': len(summaries),
            'total_action_items': total_action_items,
            'total_tasks': len(tasks),
            'total_risks': total_risks,
            'transcripts_processed': transcripts_count
        }


# Initialize dashboard data
dashboard_data = DashboardData()


@app.route('/')
def index():
    """Main dashboard page."""
    stats = dashboard_data.get_statistics()
    summaries = dashboard_data.get_summaries()
    
    return render_template('dashboard.html', stats=stats, summaries=summaries)


@app.route('/api/summaries')
def api_summaries():
    """API endpoint for summaries."""
    summaries = dashboard_data.get_summaries()
    return jsonify(summaries)


@app.route('/api/summary/<filename>')
def api_summary(filename):
    """API endpoint for a specific summary."""
    content = dashboard_data.get_summary_content(filename)
    
    if content is None:
        return jsonify({'error': 'Summary not found'}), 404
    
    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
    
    return jsonify({
        'filename': filename,
        'content': content,
        'html': html_content
    })


@app.route('/api/tasks')
def api_tasks():
    """API endpoint for tasks."""
    tasks = dashboard_data.get_tasks()
    return jsonify(tasks)


@app.route('/api/statistics')
def api_statistics():
    """API endpoint for statistics."""
    stats = dashboard_data.get_statistics()
    return jsonify(stats)


@app.route('/summary/<filename>')
def view_summary(filename):
    """View a specific summary."""
    content = dashboard_data.get_summary_content(filename)
    
    if content is None:
        return "Summary not found", 404
    
    # Parse action items from the summary
    action_items = parse_action_items(content)
    risk_points = parse_risk_points(content)
    key_decisions = parse_key_decisions(content)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
    
    return render_template('summary.html', 
                         filename=filename, 
                         content=html_content, 
                         markdown=content,
                         action_items=action_items,
                         risk_points=risk_points,
                         key_decisions=key_decisions)


def parse_action_items(content):
    """Parse action items from summary content."""
    action_items = []
    lines = content.split('\n')
    in_action_section = False
    current_item = None
    
    for line in lines:
        if '## Action Items' in line:
            in_action_section = True
            continue
        elif line.startswith('##'):
            in_action_section = False
            continue
        
        if in_action_section and line.strip():
            if line.startswith('- **'):
                # New action item
                if current_item:
                    action_items.append(current_item)
                
                # Parse owner and task
                parts = line.split('**:', 1)
                if len(parts) == 2:
                    owner = parts[0].replace('- **', '').strip()
                    task = parts[1].strip()
                    current_item = {
                        'owner': owner,
                        'task': task,
                        'task_link': '',
                        'context': ''
                    }
            elif current_item and '- [' in line and '](' in line:
                # Task link
                import re
                match = re.search(r'\[(.*?)\]\((.*?)\)', line)
                if match:
                    link = match.group(2)
                    current_item['task_link'] = link
                    # Extract task ID from anchor (e.g., file://./tasks.md#task_20240113_100000_001)
                    if '#' in link:
                        current_item['task_id'] = link.split('#')[1]
                    else:
                        current_item['task_id'] = match.group(1)
            elif current_item and '- Context:' in line:
                # Context
                current_item['context'] = line.replace('- Context:', '').strip().strip('"')
    
    if current_item:
        action_items.append(current_item)
    
    return action_items


def parse_risk_points(content):
    """Parse risk points from summary content."""
    risk_points = []
    lines = content.split('\n')
    in_risk_section = False
    current_risk = None
    
    for line in lines:
        if '## 🚨 Risk Points' in line or '## Risk Points' in line:
            in_risk_section = True
            continue
        elif line.startswith('##'):
            in_risk_section = False
            continue
        
        if in_risk_section and line.strip():
            if '**Sentiment Score:' in line:
                if current_risk:
                    risk_points.append(current_risk)
                
                # Extract score
                import re
                match = re.search(r'(\d+\.\d+)', line)
                score = match.group(1) if match else '0.0'
                current_risk = {
                    'score': score,
                    'text': '',
                    'context': ''
                }
            elif current_risk and line.startswith('  - "'):
                current_risk['text'] = line.strip('- "')
            elif current_risk and '- Context:' in line:
                current_risk['context'] = line.replace('- Context:', '').strip()
    
    if current_risk:
        risk_points.append(current_risk)
    
    return risk_points


def parse_key_decisions(content):
    """Parse key decisions from summary content."""
    decisions = []
    lines = content.split('\n')
    in_decisions_section = False
    
    for line in lines:
        if '## Key Decisions' in line:
            in_decisions_section = True
            continue
        elif line.startswith('##'):
            in_decisions_section = False
            continue
        
        if in_decisions_section and line.startswith('- '):
            decisions.append(line.replace('- ', '').strip())
    
    return decisions


@app.route('/tasks')
def view_tasks():
    """View all tasks."""
    tasks = dashboard_data.get_tasks()
    return render_template('tasks.html', tasks=tasks)


def run_dashboard(host='0.0.0.0', port=8000, debug=False):
    """Run the dashboard server."""
    logger.info(f"Starting dashboard on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard(debug=True)
