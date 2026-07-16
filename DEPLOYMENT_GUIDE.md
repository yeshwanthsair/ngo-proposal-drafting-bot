# Deployment Guide - NGO Proposal Drafting Bot

**Complete guide to deploy your project to production**

---

## 🎯 **Deployment Options**

| Platform | Difficulty | Cost | Best For |
|----------|-----------|------|----------|
| **Docker** | Easy | Free | Local/Any server |
| **Heroku** | Easy | Free-$7/month | Quick deployment |
| **AWS** | Medium | Free-$50/month | Scalable |
| **Google Cloud** | Medium | Free-$50/month | Scalable |
| **Azure** | Medium | Free-$50/month | Enterprise |
| **Linux Server** | Hard | $5-20/month | Full control |

---

## 🐳 **Option 1: Docker Deployment (Recommended)**

### **Step 1: Create Dockerfile for Backend**

Create file: `Dockerfile.backend`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY .env.example ./.env

# Expose port
EXPOSE 8000

# Run backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Step 2: Create Dockerfile for Frontend**

Create file: `Dockerfile.frontend`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY frontend/ ./frontend/
COPY .streamlit/ ./.streamlit/

# Expose port
EXPOSE 8501

# Run frontend
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **Step 3: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
      - CHROMA_PERSIST_DIR=/app/chroma_db
      - ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./logs:/app/logs
    depends_on:
      - ollama
    networks:
      - ngo-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://backend:8000/api/v1
    depends_on:
      - backend
    networks:
      - ngo-network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ./ollama_data:/root/.ollama
    networks:
      - ngo-network

networks:
  ngo-network:
    driver: bridge
```

### **Step 4: Build and Run with Docker**

```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop containers
docker-compose down
```

---

## ☁️ **Option 2: Heroku Deployment**

### **Step 1: Create Procfile**

Create file: `Procfile`

```
web: gunicorn backend.main:app
worker: streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0
```

### **Step 2: Create runtime.txt**

Create file: `runtime.txt`

```
python-3.10.12
```

### **Step 3: Install Heroku CLI**

```bash
# Windows
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### **Step 4: Deploy to Heroku**

```bash
# Login to Heroku
heroku login

# Create app
heroku create ngo-proposal-bot

# Set environment variables
heroku config:set LLM_PROVIDER=groq
heroku config:set GROQ_API_KEY=your_key_here
heroku config:set ADMIN_PASSWORD=your_password

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Open app
heroku open
```

---

## 🚀 **Option 3: AWS Deployment**

### **Step 1: Create AWS Account**

1. Go to https://aws.amazon.com
2. Create free account
3. Set up IAM user

### **Step 2: Deploy Backend to AWS EC2**

```bash
# 1. Launch EC2 instance (Ubuntu 20.04)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# 4. Clone repository
git clone https://github.com/your-username/NGO_Proposal_Drafting_Bot.git
cd NGO_Proposal_Drafting_Bot

# 5. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 6. Install requirements
pip install -r requirements.txt

# 7. Run backend with Gunicorn
gunicorn backend.main:app --workers 4 --bind 0.0.0.0:8000
```

### **Step 3: Deploy Frontend to AWS Amplify**

```bash
# 1. Install Amplify CLI
npm install -g @aws-amplify/cli

# 2. Initialize Amplify
amplify init

# 3. Add hosting
amplify add hosting

# 4. Deploy
amplify publish
```

---

## 🌐 **Option 4: Google Cloud Deployment**

### **Step 1: Create Google Cloud Project**

1. Go to https://console.cloud.google.com
2. Create new project
3. Enable Cloud Run API

### **Step 2: Deploy with Cloud Run**

```bash
# 1. Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# 2. Authenticate
gcloud auth login

# 3. Set project
gcloud config set project YOUR_PROJECT_ID

# 4. Deploy backend
gcloud run deploy ngo-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# 5. Deploy frontend
gcloud run deploy ngo-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🖥️ **Option 5: Linux Server Deployment**

### **Step 1: Rent a Server**

- DigitalOcean: $5/month
- Linode: $5/month
- Vultr: $2.50/month

### **Step 2: Setup Server**

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3-pip python3-venv nginx supervisor git

# Clone repository
git clone https://github.com/your-username/NGO_Proposal_Drafting_Bot.git
cd NGO_Proposal_Drafting_Bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip install gunicorn
```

### **Step 3: Configure Supervisor**

Create file: `/etc/supervisor/conf.d/ngo-bot.conf`

```ini
[program:ngo-backend]
directory=/root/NGO_Proposal_Drafting_Bot
command=/root/NGO_Proposal_Drafting_Bot/venv/bin/gunicorn backend.main:app --workers 4 --bind 0.0.0.0:8000
autostart=true
autorestart=true
stderr_logfile=/var/log/ngo-backend.err.log
stdout_logfile=/var/log/ngo-backend.out.log

[program:ngo-frontend]
directory=/root/NGO_Proposal_Drafting_Bot
command=/root/NGO_Proposal_Drafting_Bot/venv/bin/streamlit run frontend/app.py --server.port=8501
autostart=true
autorestart=true
stderr_logfile=/var/log/ngo-frontend.err.log
stdout_logfile=/var/log/ngo-frontend.out.log
```

### **Step 4: Configure Nginx**

Create file: `/etc/nginx/sites-available/ngo-bot`

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Step 5: Start Services**

```bash
# Start supervisor
supervisorctl reread
supervisorctl update
supervisorctl start all

# Enable nginx
systemctl enable nginx
systemctl start nginx

# Check status
supervisorctl status
```

---

## 📋 **Pre-Deployment Checklist**

- [ ] All tests passing locally
- [ ] `.env` file configured with production values
- [ ] `.env` NOT committed to git
- [ ] `requirements.txt` updated
- [ ] `README.md` updated
- [ ] Documentation complete
- [ ] Error handling tested
- [ ] Database backups configured
- [ ] Logging configured
- [ ] Security headers set

---

## 🔐 **Production Environment Variables**

Create `.env` for production:

```env
# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192

# Database
CHROMA_PERSIST_DIR=/var/lib/ngo-bot/chroma_db

# Admin
ADMIN_PASSWORD=your_secure_password_here

# API
API_BASE_URL=https://your-domain.com/api/v1

# Debug
DEBUG=False
```

---

## 🚀 **Quick Deployment Commands**

### **Docker (Fastest)**
```bash
docker-compose build
docker-compose up -d
# Access at http://localhost:8501
```

### **Heroku**
```bash
heroku create ngo-proposal-bot
git push heroku main
heroku open
```

### **AWS EC2**
```bash
# SSH into instance
ssh -i key.pem ubuntu@ip

# Clone and run
git clone repo-url
cd repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn backend.main:app --bind 0.0.0.0:8000
```

---

## 📊 **Deployment Comparison**

| Feature | Docker | Heroku | AWS | Linux |
|---------|--------|--------|-----|-------|
| **Setup Time** | 30 min | 10 min | 1 hour | 2 hours |
| **Cost** | Free | Free-$7 | Free-$50 | $5-20 |
| **Scalability** | Good | Good | Excellent | Manual |
| **Maintenance** | Low | Very Low | Medium | High |
| **Best For** | Development | Quick Deploy | Production | Full Control |

---

## ✅ **Verification After Deployment**

```bash
# Check backend health
curl https://your-domain.com/health

# Check API docs
https://your-domain.com/docs

# Check frontend
https://your-domain.com

# Check logs
docker-compose logs -f
# or
heroku logs --tail
# or
tail -f /var/log/ngo-backend.out.log
```

---

## 🆘 **Troubleshooting**

### **Port Already in Use**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 PID
```

### **Module Not Found**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### **Database Connection Error**
```bash
# Check ChromaDB directory
ls -la chroma_db/

# Reset database
rm -rf chroma_db/
```

### **LLM Not Responding**
```bash
# Check Ollama/Groq
curl http://localhost:11434/api/tags
# or check GROQ_API_KEY
```

---

## 📞 **Support**

- Docker Issues: https://docs.docker.com
- Heroku Issues: https://devcenter.heroku.com
- AWS Issues: https://docs.aws.amazon.com
- FastAPI: https://fastapi.tiangolo.com
- Streamlit: https://docs.streamlit.io

---

*NGO Proposal Drafting Bot | PRJ-032 | Yeshwanth Sai R*
