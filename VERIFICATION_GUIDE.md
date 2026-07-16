# Week 3 Verification Guide
**NGO Proposal Drafting Bot (PRJ-032)**  
**How to Verify All Features Are Working**

---

## ✅ Pre-Verification Checklist

Before running the application, ensure:
- [ ] Python 3.10+ installed
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file configured with required variables
- [ ] Ollama installed (for local LLM) OR Groq API key set
- [ ] Ports 8000 (backend) and 8501 (frontend) are available

---

## 🚀 Step 1: Start the Backend

```bash
# Terminal 1: Start FastAPI backend
python -m uvicorn backend.main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Verify**:
- Open http://localhost:8000/docs in browser
- Should see Swagger API documentation
- All endpoints should be listed

---

## 🎨 Step 2: Start the Frontend

```bash
# Terminal 2: Start Streamlit frontend
streamlit run frontend/app.py
```

**Expected Output**:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

**Verify**:
- Frontend opens at http://localhost:8501
- Sidebar shows "NGO Bot" header
- Navigation menu shows 5 pages
- Knowledge base stats show 0 documents initially

---

## 🤖 Step 3: Start LLM Service (Optional but Recommended)

```bash
# Terminal 3: Start Ollama (for local LLM)
ollama serve
```

**Expected Output**:
```
Listening on 127.0.0.1:11434
```

**Alternative**: Use Groq (cloud LLM)
```bash
# Set in .env file
GROQ_API_KEY=your_key_here
LLM_PROVIDER=groq
```

---

## 🧪 Step 4: Run Tests

### Quick Test (No LLM Required)
```bash
# Test session manager and datetime utils
pytest tests/test_week3.py::TestSessionManager tests/test_week3.py::TestDatetimeUtils -v
```

**Expected Output**:
```
tests/test_week3.py::TestSessionManager::test_create_session PASSED
tests/test_week3.py::TestSessionManager::test_create_admin_session PASSED
...
14 passed in 0.10s
```

### Full Test Suite (Requires Ollama)
```bash
# Run all tests
pytest tests/ -v
```

---

## 📋 Step 5: Verify Each Feature

### Feature 1: Chat / Q&A Page

**Steps**:
1. Go to "💬 Chat / Q&A" page
2. See welcome message from assistant
3. Toggle "🧠 Conversation Memory" ON
4. Type a question: "What is an NGO proposal?"
5. See response with timestamp

**Expected**:
- ✅ Response appears within 30 seconds
- ✅ Timestamp shows current time
- ✅ Memory toggle works
- ✅ Can edit and regenerate messages

**Verify Memory**:
1. Ask: "What is an executive summary?"
2. Ask: "How long should it be?"
3. Second response should reference first question

---

### Feature 2: Upload Documents

**Steps**:
1. Go to "📁 Upload Documents" page
2. Click "📥 Load Sample NGO Documents"
3. Wait for upload to complete

**Expected**:
- ✅ Sample documents load successfully
- ✅ Knowledge base stats update
- ✅ Documents appear in "📋 Knowledge Base" page

**Verify**:
1. Go to "📋 Knowledge Base" page
2. Should see documents listed
3. Click on document to preview
4. Should see document content

---

### Feature 3: Proposal Generation

**Steps**:
1. Go to "✍️ Draft Proposal" page
2. Fill in form:
   - Organization: "Hope Foundation"
   - Project Title: "Rural Education Program"
   - Problem: "Limited access to quality education in rural areas"
   - Beneficiaries: "500 children aged 6-16"
3. Select section: "Executive Summary"
4. Click "🚀 Generate Proposal"

**Expected**:
- ✅ Proposal generates within 30-60 seconds
- ✅ Content appears in markdown format
- ✅ Download buttons work
- ✅ Can generate different sections

**Verify Checklist**:
1. Scroll down to "✅ Proposal Submission Checklist"
2. Enter organization and project name
3. Click "📋 Generate Checklist"
4. Should see comprehensive checklist
5. Can download as markdown

---

### Feature 4: Admin Panel

**Steps**:
1. Go to "🔧 Admin Panel" page
2. Enter password: `admin123` (or your ADMIN_PASSWORD)
3. Click "🔑 Login as Admin"

**Expected**:
- ✅ Login successful message
- ✅ Admin panel unlocks
- ✅ Can see session management
- ✅ Can see chat history

**Verify Session Management**:
1. Should see session statistics
2. Can view all active sessions
3. Can see message counts

**Verify Chat History**:
1. Should see chat history logs
2. Can search by keyword
3. Can filter by session
4. Can export history

---

## 🔍 Step 6: API Verification

### Test Root Endpoint
```bash
curl http://localhost:8000/
```

**Expected Response**:
```json
{
  "project": "NGO Proposal Drafting Bot",
  "version": "3.0.0",
  "week": "Week 3",
  "status": "running"
}
```

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "message": "NGO Proposal Drafting Bot API is running (Week 3)"
}
```

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is an NGO proposal?",
    "session_id": "test_session",
    "use_memory": true
  }'
```

**Expected Response**:
```json
{
  "answer": "An NGO proposal is...",
  "sources": [],
  "citations": [],
  "chunks_used": 0,
  "session_id": "test_session",
  "timestamp": "May 9, 2026 at 3:45 PM"
}
```

### Test Admin Login
```bash
curl -X POST http://localhost:8000/api/v1/chat/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "admin123"}'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Admin login successful.",
  "session_id": "admin_session_id_here"
}
```

---

## 📊 Step 7: Verify UI Customization

### Check Colors
- [ ] Sidebar is grey (#4a4a4a) with white text
- [ ] All buttons are red (#FF0000) with white text
- [ ] Buttons turn darker red on hover
- [ ] Main background is light grey
- [ ] Text is dark and readable

### Check Responsive Design
- [ ] Sidebar expands/collapses
- [ ] Multi-column layouts work
- [ ] Mobile view is readable
- [ ] All buttons are clickable

### Check Navigation
- [ ] All 5 pages accessible from sidebar
- [ ] Page transitions are smooth
- [ ] Navigation menu is always visible

---

## 🧠 Step 8: Verify Conversation Memory

**Test Sequence**:
1. Enable "🧠 Conversation Memory"
2. Ask: "What are the main sections of an NGO proposal?"
3. Ask: "Can you give me an example of the first one?"
4. Response should reference "executive summary" from first question

**Expected**:
- ✅ Second response shows understanding of context
- ✅ Memory persists across messages
- ✅ Can clear memory with button

---

## 🔐 Step 9: Verify Admin Features

**Test Admin Login**:
1. Go to Admin Panel
2. Enter wrong password → Should fail
3. Enter correct password → Should succeed
4. Should see "✅ Logged in as Admin"

**Test Session Management**:
1. Should see total sessions count
2. Should see admin/user session breakdown
3. Should see total messages count

**Test Chat History**:
1. Ask questions in Chat page
2. Go to Admin Panel
3. Should see questions in history
4. Can search by keyword
5. Can filter by session
6. Can export history

**Test KB Refresh**:
1. Click "🔄 Refresh Knowledge Base"
2. Should see success message
3. Stats should update

---

## 📈 Step 10: Performance Verification

### Response Times
- [ ] Chat response: < 30 seconds (with LLM)
- [ ] Proposal generation: 30-60 seconds
- [ ] Document upload: < 10 seconds
- [ ] Page navigation: < 1 second

### Memory Usage
- [ ] Backend memory: < 500MB
- [ ] Frontend memory: < 200MB
- [ ] Conversation history: Max 20 messages

### Concurrent Users
- [ ] Multiple sessions work independently
- [ ] Each session has separate memory
- [ ] No cross-session data leakage

---

## 🐛 Step 11: Error Handling Verification

### Test Missing Backend
1. Stop FastAPI backend
2. Try to use frontend
3. Should see error: "Cannot connect to backend"

### Test Invalid Input
1. Try to upload unsupported file type
2. Should see error message
3. Should not crash

### Test Empty Questions
1. Try to ask empty question
2. Should see validation error
3. Should not crash

### Test Admin with Wrong Password
1. Enter wrong password
2. Should see "Invalid password" message
3. Should not grant access

---

## ✅ Final Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 8501
- [ ] API documentation accessible at /docs
- [ ] All 5 frontend pages working
- [ ] Chat page with memory working
- [ ] Proposal generation working
- [ ] Document upload working
- [ ] Knowledge base page working
- [ ] Admin panel with login working
- [ ] Session management working
- [ ] Chat history logging working
- [ ] All tests passing (14+ core tests)
- [ ] UI colors correct (grey sidebar, red buttons)
- [ ] Error messages displaying correctly
- [ ] Response times acceptable

---

## 🎯 Success Criteria

**All of the following should be true**:

✅ Backend API running and responding  
✅ Frontend UI loading without errors  
✅ Chat page accepting questions and returning answers  
✅ Conversation memory working (context-aware responses)  
✅ Proposal generation creating valid content  
✅ Document upload and indexing working  
✅ Admin panel accessible with password  
✅ Session management tracking users  
✅ Chat history logging interactions  
✅ All UI colors applied correctly  
✅ Tests passing (14+ core tests)  
✅ No console errors or warnings  

---

## 🚨 Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process and restart
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Frontend Won't Connect to Backend
```bash
# Check API_BASE_URL in .env
API_BASE_URL=http://localhost:8000/api/v1

# Verify backend is running
curl http://localhost:8000/health
```

### LLM Not Responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Or use Groq instead
# Set GROQ_API_KEY in .env
# Set LLM_PROVIDER=groq
```

### Tests Failing
```bash
# Run with verbose output
pytest tests/test_week3.py -v -s

# Run specific test
pytest tests/test_week3.py::TestSessionManager::test_create_session -v
```

### Memory Issues
```bash
# Clear ChromaDB
rm -rf ./chroma_db

# Clear session state
# Restart frontend: Ctrl+C and rerun
```

---

## 📞 Support

If you encounter issues:

1. Check the error message carefully
2. Review the troubleshooting section above
3. Check that all services are running
4. Verify environment variables in .env
5. Check logs in terminal windows
6. Run tests to identify specific failures

---

## 🎉 Verification Complete!

If all steps pass, your NGO Proposal Drafting Bot is fully functional and ready to use!

**Next Steps**:
- Start using the application
- Upload your own NGO documents
- Generate proposals for your projects
- Share with team members
- Provide feedback for improvements

---

*Generated on May 9, 2026*  
*NGO Proposal Drafting Bot | PRJ-032*
