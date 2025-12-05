#!/usr/bin/env python3
"""Simple HTTP server dashboard for Meeting Router (no Flask required)."""

import http.server
import socketserver
import json
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re

PORT = 8000

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the dashboard."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/index.html':
            self.serve_dashboard()
        elif path == '/api/summaries':
            self.serve_api_summaries()
        elif path == '/api/statistics':
            self.serve_api_statistics()
        elif path.startswith('/summary/'):
            filename = path.replace('/summary/', '')
            self.serve_summary(filename)
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve the main dashboard page."""
        stats = self.get_statistics()
        summaries = self.get_summaries()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The P.A. - Procrastinator's Assistant</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #2c3e50; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header h1 {{ font-size: 2rem; font-weight: 600; }}
        .header p {{ opacity: 0.9; margin-top: 0.5rem; }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .stat-card {{ background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); transition: transform 0.3s; }}
        .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        .stat-card h3 {{ color: #7f8c8d; font-size: 0.9rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-card .value {{ font-size: 2.5rem; font-weight: 700; color: #667eea; margin-top: 0.5rem; }}
        .card {{ background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 1.5rem; }}
        .card h2 {{ color: #2c3e50; margin-bottom: 1rem; font-size: 1.5rem; }}
        .summary-list {{ list-style: none; }}
        .summary-item {{ padding: 1rem; border-bottom: 1px solid #ecf0f1; transition: background 0.3s; }}
        .summary-item:hover {{ background: #f8f9fa; }}
        .summary-item:last-child {{ border-bottom: none; }}
        .summary-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
        .summary-title {{ font-weight: 600; color: #2c3e50; }}
        .summary-time {{ color: #7f8c8d; font-size: 0.9rem; }}
        .summary-meta {{ display: flex; gap: 1rem; font-size: 0.9rem; color: #7f8c8d; margin-bottom: 1rem; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500; }}
        .badge-primary {{ background: #e3f2fd; color: #1976d2; }}
        .badge-danger {{ background: #ffebee; color: #c62828; }}
        .btn {{ display: inline-block; padding: 0.5rem 1.5rem; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-weight: 500; transition: all 0.3s; }}
        .btn:hover {{ background: #5568d3; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3); }}
        .empty-state {{ text-align: center; padding: 3rem; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 The P.A. (Procrastinator's Assistant)</h1>
        <p>Commitment Capture and Risk Router</p>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Meetings</h3>
                <div class="value">{stats['total_meetings']}</div>
            </div>
            <div class="stat-card">
                <h3>Action Items</h3>
                <div class="value">{stats['total_action_items']}</div>
            </div>
            <div class="stat-card">
                <h3>Tasks Created</h3>
                <div class="value">{stats['total_tasks']}</div>
            </div>
            <div class="stat-card">
                <h3>Risk Points</h3>
                <div class="value">{stats['total_risks']}</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Recent Meeting Summaries</h2>
            {'<ul class="summary-list">' if summaries else '<div class="empty-state"><h3>No summaries yet</h3><p>Process a meeting transcript to see summaries here</p></div>'}
            {''.join([f'''
                <li class="summary-item">
                    <div class="summary-header">
                        <div class="summary-title">Meeting Summary</div>
                        <div class="summary-time">{s['timestamp']}</div>
                    </div>
                    <div class="summary-meta">
                        <span class="badge badge-primary">{s['action_items_count']} action items</span>
                        {'<span class="badge badge-danger">⚠️ Has risk points</span>' if s['has_risks'] else ''}
                    </div>
                    <a href="/summary/{s['filename']}" class="btn">View Summary</a>
                </li>
            ''' for s in summaries])}
            {'</ul>' if summaries else ''}
        </div>
    </div>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_summary(self, filename):
        """Serve a specific summary."""
        filepath = os.path.join('summaries', filename)
        
        if not os.path.exists(filepath):
            self.send_error(404, "Summary not found")
            return
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Simple markdown to HTML conversion
        html_content = content.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html_content = html_content.replace('- **', '<li><strong>').replace('**:', '</strong>:')
        html_content = html_content.replace('- ', '<li>')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{filename}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 2rem; line-height: 1.6; }}
        h1, h2 {{ color: #2c3e50; margin-top: 2rem; }}
        .btn {{ display: inline-block; padding: 0.5rem 1.5rem; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-bottom: 2rem; }}
        pre {{ background: #f8f9fa; padding: 1rem; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <a href="/" class="btn">← Back to Dashboard</a>
    <pre>{content}</pre>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_api_summaries(self):
        """Serve summaries API."""
        summaries = self.get_summaries()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(summaries).encode())
    
    def serve_api_statistics(self):
        """Serve statistics API."""
        stats = self.get_statistics()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())
    
    def get_summaries(self):
        """Get all summary files."""
        summaries = []
        summary_dir = 'summaries'
        
        if not os.path.exists(summary_dir):
            return summaries
        
        for filename in os.listdir(summary_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(summary_dir, filename)
                
                try:
                    timestamp_str = filename.replace('summary_', '').replace('.md', '')
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                except:
                    timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                with open(filepath, 'r') as f:
                    content = f.read()
                
                action_items_count = content.count('**') // 2
                has_risks = '🚨' in content or 'Risk Points' in content
                
                summaries.append({
                    'filename': filename,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'action_items_count': action_items_count,
                    'has_risks': has_risks
                })
        
        summaries.sort(key=lambda x: x['timestamp'], reverse=True)
        return summaries
    
    def get_statistics(self):
        """Get overall statistics."""
        summaries = self.get_summaries()
        
        total_action_items = sum(s['action_items_count'] for s in summaries)
        total_risks = sum(1 for s in summaries if s['has_risks'])
        
        # Count tasks
        total_tasks = 0
        if os.path.exists('tasks.md'):
            with open('tasks.md', 'r') as f:
                content = f.read()
                total_tasks = content.count('## task_')
        
        return {
            'total_meetings': len(summaries),
            'total_action_items': total_action_items,
            'total_tasks': total_tasks,
            'total_risks': total_risks
        }


def run_server(port=8000):
    """Run the dashboard server."""
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════╗
║    The P.A. (Procrastinator's Assistant) Dashboard      ║
║         Commitment Capture and Risk Router               ║
╚══════════════════════════════════════════════════════════╝

🚀 Server running on port {port}
📍 Open: http://localhost:{port}

Press Ctrl+C to stop the server
""")
        httpd.serve_forever()


if __name__ == '__main__':
    run_server(PORT)
