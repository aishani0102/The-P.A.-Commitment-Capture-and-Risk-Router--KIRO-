# Meeting Router - Complete Hosting Guide

## 🚀 Deployment Flowchart

```mermaid
flowchart TD
    Start([Start Hosting Process]) --> Choice{Hosting Type?}
    
    Choice -->|Local Development| Local[Local Hosting]
    Choice -->|Cloud Deployment| Cloud[Cloud Hosting]
    Choice -->|Docker Container| Docker[Docker Deployment]
    
    %% Local Hosting Path
    Local --> L1[Install Python 3.9+]
    L1 --> L2[Clone/Download Repository]
    L2 --> L3[Install Dependencies<br/>pip install -r requirements.txt]
    L3 --> L4[Create config.json]
    L4 --> L5{Test with Demo?}
    L5 -->|Yes| L6[Run: python demo.py]
    L5 -->|No| L7[Add Transcripts]
    L6 --> L8[Start Dashboard<br/>python run_dashboard.py]
    L7 --> L8
    L8 --> L9[Access: http://localhost:5000]
    L9 --> LocalDone([Local Hosting Complete])
    
    %% Cloud Hosting Path
    Cloud --> C1{Cloud Provider?}
    C1 -->|AWS| AWS[AWS Deployment]
    C1 -->|Heroku| Heroku[Heroku Deployment]
    C1 -->|DigitalOcean| DO[DigitalOcean Deployment]
    C1 -->|Azure| Azure[Azure Deployment]
    
    AWS --> C2[Setup EC2 Instance]
    Heroku --> C3[Create Heroku App]
    DO --> C4[Create Droplet]
    Azure --> C5[Create App Service]
    
    C2 --> C6[Install Dependencies]
    C3 --> C6
    C4 --> C6
    C5 --> C6
    
    C6 --> C7[Configure Environment Variables]
    C7 --> C8[Setup File Storage]
    C8 --> C9[Configure Firewall/Security]
    C9 --> C10[Deploy Application]
    C10 --> C11[Setup Process Manager<br/>systemd/supervisor]
    C11 --> C12[Configure Domain/SSL]
    C12 --> CloudDone([Cloud Hosting Complete])
    
    %% Docker Path
    Docker --> D1[Create Dockerfile]
    D1 --> D2[Create docker-compose.yml]
    D2 --> D3[Build Image<br/>docker build -t meeting-router .]
    D3 --> D4[Run Container<br/>docker-compose up -d]
    D4 --> D5[Mount Volumes for Data]
    D5 --> D6[Access: http://localhost:5000]
    D6 --> DockerDone([Docker Hosting Complete])
    
    %% Post-Deployment
    LocalDone --> Monitor[Monitoring & Maintenance]
    CloudDone --> Monitor
    DockerDone --> Monitor
    
    Monitor --> M1[Check Logs]
    M1 --> M2[Monitor Resource Usage]
    M2 --> M3[Backup Data]
    M3 --> M4[Update Dependencies]
    M4 --> End([System Running])
```

## 📋 Detailed Hosting Options

### Option 1: Local Development Hosting

**Best for:** Testing, development, personal use

**Steps:**
1. **Prerequisites**
   - Python 3.9 or higher
   - pip package manager
   - 2GB RAM minimum

2. **Installation**
   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd meeting-router
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**
   ```bash
   # Copy example config
   cp config.example.json config.json
   
   # Edit config.json with your settings
   nano config.json
   ```

4. **Run Application**
   ```bash
   # Option A: Dashboard only
   python run_dashboard.py
   
   # Option B: With auto-processing
   python -m meeting_router.main --config config.json
   ```

5. **Access**
   - Open browser: `http://localhost:5000`

---

### Option 2: Cloud Hosting (Production)

#### AWS EC2 Deployment

```mermaid
flowchart LR
    A[Launch EC2 Instance] --> B[Ubuntu 22.04 LTS]
    B --> C[Install Python & Dependencies]
    C --> D[Clone Repository]
    D --> E[Configure Application]
    E --> F[Setup Nginx Reverse Proxy]
    F --> G[Configure SSL with Let's Encrypt]
    G --> H[Setup systemd Service]
    H --> I[Start Application]
```

**Detailed Steps:**

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t2.small (minimum)
   - Storage: 20GB
   - Security Group: Allow ports 22, 80, 443, 5000

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python
   sudo apt install python3.9 python3-pip -y
   
   # Install Nginx
   sudo apt install nginx -y
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd meeting-router
   
   # Install dependencies
   pip3 install -r requirements.txt
   
   # Create config
   cp config.example.json config.json
   nano config.json
   ```

4. **Setup systemd Service**
   ```bash
   sudo nano /etc/systemd/system/meeting-router.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Meeting Router Dashboard
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/meeting-router
   Environment="PATH=/home/ubuntu/.local/bin"
   ExecStart=/usr/bin/python3 run_dashboard.py --host 0.0.0.0 --port 5000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable meeting-router
   sudo systemctl start meeting-router
   ```

5. **Configure Nginx Reverse Proxy**
   ```bash
   sudo nano /etc/nginx/sites-available/meeting-router
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```
   
   Enable:
   ```bash
   sudo ln -s /etc/nginx/sites-available/meeting-router /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Setup SSL (Optional but Recommended)**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

#### Heroku Deployment

1. **Create Procfile**
   ```bash
   echo "web: python run_dashboard.py --host 0.0.0.0 --port \$PORT" > Procfile
   ```

2. **Create runtime.txt**
   ```bash
   echo "python-3.9.18" > runtime.txt
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create meeting-router-app
   git push heroku main
   heroku open
   ```

4. **Configure Environment Variables**
   ```bash
   heroku config:set MEETING_ROUTER_TASK_BACKEND=Markdown
   heroku config:set MEETING_ROUTER_LOG_LEVEL=INFO
   ```

---

### Option 3: Docker Deployment

**Best for:** Containerized environments, easy deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application
   COPY . .
   
   # Create directories
   RUN mkdir -p transcripts summaries
   
   # Expose port
   EXPOSE 5000
   
   # Run application
   CMD ["python", "run_dashboard.py", "--host", "0.0.0.0", "--port", "5000"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     meeting-router:
       build: .
       ports:
         - "5000:5000"
       volumes:
         - ./transcripts:/app/transcripts
         - ./summaries:/app/summaries
         - ./tasks.md:/app/tasks.md
         - ./config.json:/app/config.json
       environment:
         - MEETING_ROUTER_LOG_LEVEL=INFO
       restart: unless-stopped
   ```

3. **Build and Run**
   ```bash
   # Build image
   docker build -t meeting-router .
   
   # Run with docker-compose
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop
   docker-compose down
   ```

4. **Access**
   - Open browser: `http://localhost:5000`

---

## 🔧 Configuration for Production

### Environment Variables

```bash
# Application Settings
export MEETING_ROUTER_WATCH_DIR="/app/transcripts"
export MEETING_ROUTER_SENTIMENT_THRESHOLD="0.3"
export MEETING_ROUTER_TASK_BACKEND="Markdown"
export MEETING_ROUTER_LOG_LEVEL="INFO"

# JIRA (if using)
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_API_TOKEN="your_token"
export JIRA_PROJECT_KEY="TEAM"

# Slack (if using)
export SLACK_BOT_TOKEN="xoxb-your-token"
export SLACK_CHANNEL_ID="C1234567890"
```

### Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Firewall**: Only expose necessary ports
3. **SSL/TLS**: Use HTTPS in production
4. **File Permissions**: Restrict access to config files
5. **Updates**: Keep dependencies updated

---

## 📊 Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end
    
    subgraph "Application Layer"
        Dashboard[Flask Dashboard<br/>Port 5000]
        Watcher[File Watcher<br/>Monitors Transcripts]
    end
    
    subgraph "Processing Layer"
        Parser[Transcript Parser]
        NLP[NLP Processor<br/>Action Extraction]
        Sentiment[Sentiment Analysis]
    end
    
    subgraph "Integration Layer"
        TaskBackend[Task Backend<br/>JIRA/Trello/Markdown]
        Notifications[Notifications<br/>Slack/Teams]
    end
    
    subgraph "Storage Layer"
        Transcripts[(Transcripts<br/>Directory)]
        Summaries[(Summaries<br/>Directory)]
        Tasks[(Tasks<br/>File/API)]
    end
    
    Browser --> Dashboard
    Dashboard --> Summaries
    Dashboard --> Tasks
    
    Watcher --> Transcripts
    Transcripts --> Parser
    Parser --> NLP
    Parser --> Sentiment
    NLP --> TaskBackend
    Sentiment --> TaskBackend
    TaskBackend --> Tasks
    TaskBackend --> Notifications
    NLP --> Summaries
```

---

## 🔍 Monitoring & Maintenance

### Health Checks

```bash
# Check if service is running
systemctl status meeting-router

# Check logs
tail -f meeting_router.log

# Check disk space
df -h

# Check memory usage
free -m
```

### Backup Strategy

```bash
# Backup summaries and tasks
tar -czf backup-$(date +%Y%m%d).tar.gz summaries/ tasks.md config.json

# Automated backup (add to crontab)
0 2 * * * /path/to/backup-script.sh
```

### Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart meeting-router
```

---

## 🚨 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 5000 in use | Use `--port 8080` or kill process on 5000 |
| Module not found | Run `pip install -r requirements.txt` |
| Permission denied | Check file permissions, run with sudo if needed |
| Can't access from network | Use `--host 0.0.0.0` |
| High memory usage | Restart service, check for memory leaks |

### Debug Mode

```bash
# Run with debug logging
python run_dashboard.py --debug --log-level DEBUG
```

---

## 📈 Scaling Considerations

### For High Traffic

1. **Use Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 meeting_router.dashboard:app
   ```

2. **Add Load Balancer**
   - Use Nginx or HAProxy
   - Distribute across multiple instances

3. **Database Backend**
   - Replace file-based storage with PostgreSQL/MongoDB
   - Store summaries and tasks in database

4. **Caching**
   - Add Redis for caching summaries
   - Reduce file I/O operations

---

## ✅ Post-Deployment Checklist

- [ ] Application accessible via browser
- [ ] Logs are being written correctly
- [ ] File watcher is monitoring transcripts directory
- [ ] Test transcript processing works
- [ ] Dashboard displays summaries correctly
- [ ] Task creation works (Markdown/JIRA/Trello)
- [ ] Notifications are sent (if configured)
- [ ] SSL certificate is valid (production)
- [ ] Backups are configured
- [ ] Monitoring is in place
- [ ] Documentation is updated

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start dashboard | `python run_dashboard.py` |
| Start with watch mode | `python -m meeting_router.main --config config.json` |
| Process single file | `python -m meeting_router.main --process-file <file>` |
| Run tests | `pytest` |
| Check logs | `tail -f meeting_router.log` |
| Restart service | `sudo systemctl restart meeting-router` |

---

## 📞 Support

For issues or questions:
- Check logs: `meeting_router.log`
- Review configuration: `config.json`
- Test with demo: `python demo.py`
- Run diagnostics: `python -m meeting_router.main --help`

