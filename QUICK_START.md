# Quick Start Guide - NGO Proposal Drafting Bot

**Get the application running in 5 minutes!**

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Backend (Terminal 1)
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

### 3. Start Frontend (Terminal 2)
```bash
streamlit run frontend/app.py
```

### 4. Open in Browser
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

### 5. Start Using!
- Go to "💬 Chat / Q&A" and ask a question
- Or go to "✍️ Draft Proposal" to generate a proposal

---

## 📋 What You Can Do

### Chat with AI
- Ask questions about NGO proposals
- Get context-aware responses
- Memory remembers previous questions

### Generate Proposals
- Fill in project details
- Generate any section or full proposal
- Download as TXT or Markdown

### Upload Documents
- Upload your NGO documents
- System learns from them
- Get answers grounded in your docs

### Admin Panel
- Login with password: `admin123`
- View chat history
- Manage sessions
- Clear knowledge base

---

## 🔧 Configuration

### .env File
```bash
ADMIN_PASSWORD=admin123
LLM_PROVIDER=ollama
OLLAMA_MODEL=tinyllama
OLLAMA_BASE_URL=http://localhost:11434
```

### Use Groq Instead of Ollama
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
```

---

## 🧪 Run Tests

### Quick Test (No LLM)
```bash
pytest tests/test_week3.py::TestSessionManager -v
```

### All Tests (Requires Ollama)
```bash
pytest tests/ -v
```

---

## 📊 Features at a Glance

| Feature | Page | Status |
|---------|------|--------|
| Chat with Memory | 💬 Chat / Q&A | ✅ |
| Generate Proposals | ✍️ Draft Proposal | ✅ |
| Upload Documents | 📁 Upload Documents | ✅ |
| View Knowledge Base | 📋 Knowledge Base | ✅ |
| Admin Controls | 🔧 Admin Panel | ✅ |

---

## 🎨 UI Colors

- **Sidebar**: Grey with white text
- **Buttons**: Red with white text
- **Background**: Light grey
- **Text**: Dark grey

---

## 🆘 Troubleshooting

### Backend won't start?
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Frontend can't connect?
```bash
# Check .env file
API_BASE_URL=http://localhost:8000/api/v1
```

### LLM not responding?
```bash
# Start Ollama
ollama serve

# Or use Groq (set GROQ_API_KEY in .env)
```

---

## 📚 Documentation

- **README.md** - Full project documentation
- **VERIFICATION_GUIDE.md** - How to verify everything works
- **PROJECT_STATUS.md** - Complete status report
- **WEEK3_FINAL_SUMMARY.md** - Detailed Week 3 summary

---

## 🎯 Next Steps

1. ✅ Start the application (see above)
2. ✅ Upload sample documents
3. ✅ Ask questions in chat
4. ✅ Generate a proposal
5. ✅ Login to admin panel
6. ✅ View chat history

---

## 💡 Tips

- **Memory**: Toggle "🧠 Conversation Memory" for context-aware responses
- **Proposals**: Start with "Executive Summary" to see how it works
- **Admin**: Default password is `admin123` (change in .env)
- **Documents**: Load sample docs first to test the system

---

## 🚀 You're Ready!

The application is fully functional and ready to use. Start with the Chat page and explore all features!

**Questions?** Check the documentation files or review the code comments.

---

*NGO Proposal Drafting Bot | PRJ-032*
