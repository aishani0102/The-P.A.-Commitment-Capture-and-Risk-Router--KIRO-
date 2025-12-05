#!/usr/bin/env python3
"""Generate demo data for the Meeting Router dashboard."""

import os
from datetime import datetime, timedelta

# Create directories
os.makedirs('summaries', exist_ok=True)
os.makedirs('transcripts', exist_ok=True)

# Generate sample summaries
summaries = [
    {
        'date': datetime.now() - timedelta(days=2),
        'content': """# Meeting Summary - 2024-01-13 10:00:00

## Key Decisions
- Decided to migrate to microservices architecture
- Agreed to use Kubernetes for container orchestration

## Action Items
- **Alice**: Complete the architecture design document
  - [TASK-101](file://./tasks.md#task_20240113_100000_001)
  - Context: "I will complete the architecture design document by next week"

- **Bob**: Research Kubernetes deployment options
  - [TASK-102](file://./tasks.md#task_20240113_100000_002)
  - Context: "Need to research Kubernetes deployment options"

- **Charlie**: Set up development environment
  - [TASK-103](file://./tasks.md#task_20240113_100000_003)
  - Context: "Someone should set up the development environment"

## 🚨 Risk Points for Review
- **Sentiment Score: 0.28**
  - "we decided to migrate to microservices architecture"
  - Context: Team expressed concerns about the complexity and timeline for migration
"""
    },
    {
        'date': datetime.now() - timedelta(days=1),
        'content': """# Meeting Summary - 2024-01-14 14:30:00

## Key Decisions
- Decided to use React for the frontend
- Agreed on weekly sprint planning meetings

## Action Items
- **Diana**: Create React component library
  - [TASK-104](file://./tasks.md#task_20240114_143000_001)
  - Context: "I will create the React component library"

- **Eve**: Set up CI/CD pipeline
  - [TASK-105](file://./tasks.md#task_20240114_143000_002)
  - Context: "I'll set up the CI/CD pipeline this week"
"""
    },
    {
        'date': datetime.now(),
        'content': """# Meeting Summary - 2024-01-15 09:00:00

## Key Decisions
- Decided to implement feature flags for gradual rollout
- Agreed to use PostgreSQL for the main database

## Action Items
- **Frank**: Implement feature flag system
  - [TASK-106](file://./tasks.md#task_20240115_090000_001)
  - Context: "I will implement the feature flag system"

- **Grace**: Design database schema
  - [TASK-107](file://./tasks.md#task_20240115_090000_002)
  - Context: "Need to design the database schema"

- **Henry**: Write API documentation
  - [TASK-108](file://./tasks.md#task_20240115_090000_003)
  - Context: "Someone should write the API documentation"

- **Iris**: Set up monitoring and alerts
  - [TASK-109](file://./tasks.md#task_20240115_090000_004)
  - Context: "I can set up monitoring and alerts"

## 🚨 Risk Points for Review
- **Sentiment Score: 0.25**
  - "we decided to implement feature flags"
  - Context: Discussion revealed concerns about added complexity and testing overhead
"""
    }
]

# Write summaries
for summary in summaries:
    filename = f"summary_{summary['date'].strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join('summaries', filename)
    
    with open(filepath, 'w') as f:
        f.write(summary['content'])
    
    print(f"✅ Created {filename}")

# Generate tasks.md
tasks_content = """# Meeting Action Items

## task_20240113_100000_001
- **Owner**: Alice
- **Task**: Complete the architecture design document
- **Context**: "I will complete the architecture design document by next week"
- **Created**: 2024-01-13 10:00:00

## task_20240113_100000_002
- **Owner**: Bob
- **Task**: Research Kubernetes deployment options
- **Context**: "Need to research Kubernetes deployment options"
- **Created**: 2024-01-13 10:00:00

## task_20240113_100000_003
- **Owner**: Charlie
- **Task**: Set up development environment
- **Context**: "Someone should set up the development environment"
- **Created**: 2024-01-13 10:00:00

## task_20240114_143000_001
- **Owner**: Diana
- **Task**: Create React component library
- **Context**: "I will create the React component library"
- **Created**: 2024-01-14 14:30:00

## task_20240114_143000_002
- **Owner**: Eve
- **Task**: Set up CI/CD pipeline
- **Context**: "I'll set up the CI/CD pipeline this week"
- **Created**: 2024-01-14 14:30:00

## task_20240115_090000_001
- **Owner**: Frank
- **Task**: Implement feature flag system
- **Context**: "I will implement the feature flag system"
- **Created**: 2024-01-15 09:00:00

## task_20240115_090000_002
- **Owner**: Grace
- **Task**: Design database schema
- **Context**: "Need to design the database schema"
- **Created**: 2024-01-15 09:00:00

## task_20240115_090000_003
- **Owner**: Henry
- **Task**: Write API documentation
- **Context**: "Someone should write the API documentation"
- **Created**: 2024-01-15 09:00:00

## task_20240115_090000_004
- **Owner**: Iris
- **Task**: Set up monitoring and alerts
- **Context**: "I can set up monitoring and alerts"
- **Created**: 2024-01-15 09:00:00
"""

with open('tasks.md', 'w') as f:
    f.write(tasks_content)

print("✅ Created tasks.md")

print("""
╔══════════════════════════════════════════════════════════╗
║         Demo Data Generated Successfully! 🎉             ║
╚══════════════════════════════════════════════════════════╝

📊 Created:
   - 3 meeting summaries
   - 9 tasks
   - 2 risk points

🚀 Next steps:
   1. Run: python run_dashboard.py
   2. Open: http://localhost:5000
   3. Explore the dashboard!

""")
