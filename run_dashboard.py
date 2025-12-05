#!/usr/bin/env python3
"""Run the Meeting Router dashboard."""

import argparse
from meeting_router.dashboard import run_dashboard


def main():
    parser = argparse.ArgumentParser(description='Meeting Router Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║    The P.A. (Procrastinator's Assistant) Dashboard      ║
║         Commitment Capture and Risk Router               ║
╚══════════════════════════════════════════════════════════╝

🚀 Starting dashboard server...
📍 URL: http://{args.host}:{args.port}
🔍 Debug mode: {'ON' if args.debug else 'OFF'}

Press Ctrl+C to stop the server
""")
    
    run_dashboard(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
