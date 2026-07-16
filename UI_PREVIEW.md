# 🎨 UI Preview - NGO Proposal Drafting Bot

## Visual Layout Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────────────────┐  ┌─────────────────────────────────────────────┐ │
│  │                      │  │                                             │ │
│  │   SIDEBAR            │  │  PAGE CONTENT                               │ │
│  │  (Green Gradient)    │  │  (Light Background)                         │ │
│  │                      │  │                                             │ │
│  │  📋 NGO Bot          │  │  ┌─────────────────────────────────────┐   │ │
│  │  Proposal Assistant  │  │  │ Gradient Header (Color varies)      │   │ │
│  │                      │  │  │ 💬 Chat / Q&A                       │   │ │
│  │  ┌────────────────┐  │  │  │ ✍️ Draft Proposal                   │   │ │
│  │  │ 📊 Knowledge   │  │  │  │ 📁 Upload Documents                │   │ │
│  │  │ Documents: 5   │  │  │  │ 📋 Knowledge Base                  │   │ │
│  │  │ Chunks: 42     │  │  │  │ 🔧 Admin Panel                     │   │ │
│  │  └────────────────┘  │  │  └─────────────────────────────────────┘   │ │
│  │                      │  │                                             │ │
│  │  🧭 Navigation       │  │  ┌─────────────────────────────────────┐   │ │
│  │  • Chat / Q&A        │  │  │ Status Indicator (Green/Orange)     │   │ │
│  │  • Draft Proposal    │  │  │ 🧠 Memory ON/OFF                    │   │ │
│  │  • Upload Documents  │  │  └─────────────────────────────────────┘   │ │
│  │  • Knowledge Base    │  │                                             │ │
│  │  • Admin Panel       │  │  ┌─────────────────────────────────────┐   │ │
│  │                      │  │  │ Chat Messages (White Cards)         │   │ │
│  │  ⚙️ Settings         │  │  │ ┌─────────────────────────────────┐ │   │ │
│  │  🧠 Memory: ON       │  │  │ │ User: Blue gradient avatar      │ │   │ │
│  │                      │  │  │ │ "What is an NGO proposal?"      │ │   │ │
│  │  Week 3 Deliverable │  │  │ └─────────────────────────────────┘ │   │ │
│  │  FastAPI • LangChain│  │  │ ┌─────────────────────────────────┐ │   │ │
│  │  ChromaDB • Streamlit│ │  │ │ Assistant: Green gradient avatar│ │   │ │
│  │                      │  │  │ │ "An NGO proposal is..."         │ │   │ │
│  │                      │  │  │ │ 📎 Sources | 🔖 Citations      │ │   │ │
│  │                      │  │  │ └─────────────────────────────────┘ │   │ │
│  │                      │  │  └─────────────────────────────────────┘   │ │
│  │                      │  │                                             │ │
│  │                      │  │  ┌─────────────────────────────────────┐   │ │
│  │                      │  │  │ Input Area (Styled)                 │   │ │
│  │                      │  │  │ [Ask about NGO proposals...]        │   │ │
│  │                      │  │  │ [🚀 Send] [🗑️ Clear] [🧠 Memory]  │   │ │
│  │                      │  │  └─────────────────────────────────────┘   │ │
│  │                      │  │                                             │ │
│  └──────────────────────┘  └─────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Page Headers (Gradient Backgrounds)

### 💬 Chat / Q&A
```
╔═══════════════════════════════════════════════════════════════╗
║  💬 Chat with NGO Knowledge Base                              ║
║  Ask questions about NGO proposals, grant writing, and...     ║
║  (Green Gradient: #2E7D32 → #1B5E20)                          ║
╚═══════════════════════════════════════════════════════════════╝
```

### ✍️ Draft Proposal
```
╔═══════════════════════════════════════════════════════════════╗
║  ✍️ NGO Proposal Draft Generator                              ║
║  Fill in your project details and generate a professional...  ║
║  (Blue Gradient: #1976D2 → #1565C0)                           ║
╚═══════════════════════════════════════════════════════════════╝
```

### 📁 Upload Documents
```
╔═══════════════════════════════════════════════════════════════╗
║  📁 Upload Documents to Knowledge Base                        ║
║  Upload NGO documents, grant templates, or reference...       ║
║  (Orange Gradient: #FF6F00 → #F57C00)                         ║
╚═══════════════════════════════════════════════════════════════╝
```

### 📋 Knowledge Base
```
╔═══════════════════════════════════════════════════════════════╗
║  📋 Knowledge Base Status                                     ║
║  View and manage your indexed documents                       ║
║  (Purple Gradient: #7B1FA2 → #6A1B9A)                         ║
╚═══════════════════════════════════════════════════════════════╝
```

### 🔧 Admin Panel
```
╔═══════════════════════════════════════════════════════════════╗
║  🔧 Admin Panel                                               ║
║  Access control, session management, chat history...          ║
║  (Red Gradient: #C62828 → #B71C1C)                            ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Status Indicators

### ✅ Success (Green)
```
┌─────────────────────────────────────────────────────────────┐
│ ✅ Logged in as Admin                                       │
│ (Green background with left border)                         │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Memory Status (Green/Orange)
```
┌─────────────────────────────────────────────────────────────┐
│ 🧠 Conversation Memory ON                                   │
│ I remember your previous questions in this session.         │
│ (Green gradient background)                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🧠 Conversation Memory OFF                                  │
│ Each question is answered independently.                    │
│ (Orange gradient background)                                │
└─────────────────────────────────────────────────────────────┘
```

### ⚠️ Warning (Orange)
```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ Restricted Area                                          │
│ Admin access required. Enter your password to continue.     │
│ (Orange background with left border)                        │
└─────────────────────────────────────────────────────────────┘
```

### ℹ️ Info (Blue)
```
┌─────────────────────────────────────────────────────────────┐
│ 💡 Default password: Yeshwanth@2006                         │
│ Change in .env file: ADMIN_PASSWORD=yourpassword            │
│ (Blue background with left border)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Buttons

### Primary Button (Blue Gradient)
```
┌──────────────────────────────┐
│ 🚀 Generate Proposal         │  ← Blue gradient
│ (Hover: Darker + Shadow)     │
└──────────────────────────────┘
```

### Secondary Button (Orange Gradient)
```
┌──────────────────────────────┐
│ 📋 Generate Checklist        │  ← Orange gradient
│ (Hover: Darker + Shadow)     │
└──────────────────────────────┘
```

### Danger Button (Red Gradient)
```
┌──────────────────────────────┐
│ 🗑️ Clear Knowledge Base      │  ← Red gradient
│ (Hover: Darker + Shadow)     │
└──────────────────────────────┘
```

---

## Cards & Metrics

### Metric Card
```
┌─────────────────────────────┐
│ 📄 Documents                │  ← Light gray border
│ 5                           │  ← Green text, large font
│ (White background, shadow)  │
└─────────────────────────────┘
```

### Chat Message Card
```
┌─────────────────────────────────────────────────────────┐
│ 👤 User Message                                         │
│ 🕐 May 09, 2026 at 02:30 PM                            │
│                                                         │
│ What is an NGO proposal?                                │
│                                                         │
│ [📋 Copy] [🔄 Regenerate] [✏️ Edit]                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🤖 Assistant Message                                    │
│ 🕐 May 09, 2026 at 02:31 PM                            │
│                                                         │
│ An NGO proposal is a formal document that outlines...   │
│                                                         │
│ [📎 Sources] [🔖 Citations]                            │
└─────────────────────────────────────────────────────────┘
```

---

## Form Fields

### Input Field (Default)
```
Organization Name *
┌─────────────────────────────────────────────────────────┐
│ e.g., Hope Foundation                                   │
│ (Gray border, rounded corners)                          │
└─────────────────────────────────────────────────────────┘
```

### Input Field (Focus)
```
Organization Name *
┌─────────────────────────────────────────────────────────┐
│ Hope Foundation                                         │
│ (Green border, shadow glow)                             │
└─────────────────────────────────────────────────────────┘
```

---

## Sidebar Stats

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  📊 Knowledge Base                                       │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │ Documents        │  │ Chunks           │            │
│  │ 5                │  │ 42               │            │
│  │ (Semi-transparent)  (Semi-transparent) │            │
│  └──────────────────┘  └──────────────────┘            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Color Swatches

```
Primary Green       Secondary Blue      Accent Orange
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│              │   │              │   │              │
│  #2E7D32     │   │  #1976D2     │   │  #FF6F00     │
│              │   │              │   │              │
└──────────────┘   └──────────────┘   └──────────────┘

Success Green       Warning Orange      Error Red
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│              │   │              │   │              │
│  #4CAF50     │   │  #FFA726     │   │  #EF5350     │
│              │   │              │   │              │
└──────────────┘   └──────────────┘   └──────────────┘

Background Light    Text Dark           Border Gray
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│              │   │              │   │              │
│  #F5F7FA     │   │  #1A1A1A     │   │  #E0E0E0     │
│              │   │              │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## Typography

```
H1 - Page Title
💬 Chat with NGO Knowledge Base
(Green, 2.2rem, Bold)

H2 - Section Header
👥 Session Management
(Blue, 1.5rem, Bold)

H3 - Subsection
📋 Project Details
(Green, 1.2rem, Bold)

Body Text
Ask questions about NGO proposals, grant writing, and program design.
(Dark gray, 1rem, Regular)

Caption
🕐 May 09, 2026 at 02:30 PM
(Light gray, 0.85rem, Regular)
```

---

## Responsive Layout

### Desktop (Wide)
```
┌─────────────────────────────────────────────────────────┐
│ Sidebar (250px) │ Main Content (Remaining)              │
└─────────────────────────────────────────────────────────┘
```

### Tablet (Medium)
```
┌─────────────────────────────────────────────────────────┐
│ Sidebar (200px) │ Main Content (Remaining)              │
└─────────────────────────────────────────────────────────┘
```

### Mobile (Single Column)
```
┌─────────────────────────────────────────────────────────┐
│ Sidebar (Collapsed)                                     │
├─────────────────────────────────────────────────────────┤
│ Main Content (Full Width)                               │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

✅ **Professional Design** - Modern color scheme with gradients  
✅ **Consistent Branding** - Green for NGO theme throughout  
✅ **Clear Hierarchy** - Visual distinction between sections  
✅ **Accessible** - High contrast, readable fonts  
✅ **Responsive** - Works on desktop, tablet, mobile  
✅ **Interactive** - Hover effects, smooth transitions  
✅ **Production-Ready** - Polished and professional appearance  

---

**Result**: A visually attractive, professional NGO Proposal Drafting Bot UI! 🎉
