# MCP Chat Client - Project Handoff Report

## 🎯 Mission: Build a Chat-Based MCP Client

We're creating a **conversational MCP client** that integrates with our Point Topic MCP server, based on the existing UPC Query Agent codebase.

## 🧙‍♂️ Context: The Great MCP Client Betrayal

**What we discovered:** All major MCP clients (Cursor, Claude Desktop) have **broken remote MCP support**. They can see servers in settings but agents can't actually use the tools.

**Our solution:** Build our own client using **Pydantic AI** (which has excellent MCP support) instead of relying on these broken implementations.

## 📂 Source Project: UPC Query Agent

**Location:** `/Users/peterdonaghey/Projects/upc_query_agent`

**Current Architecture:**

- **Backend:** FastAPI with Pydantic AI agents
- **Frontend:** React + TypeScript + Vite + TailwindCSS
- **Database:** Snowflake connection for user management & history
- **Workflow:** One-shot query processing (ask → process → result)
- **Agents:** Multiple specialized agents (UPC Query, CSV Analysis, Query Classifier)

## 🎯 New Project Goals

### Major Changes:

1. **Conversational Flow** - Replace one-shot workflow with continuous chat
2. **Simplified Backend** - Single Pydantic AI agent + MCP server integration
3. **MCP Integration** - Backend connects to Point Topic MCP server
4. **Basic Chat UI** - Simple chat interface for users

### Keep Unchanged:

- ✅ User authentication & management
- ✅ Snowflake database connection
- ✅ Message history for analytics
- ✅ FastAPI + React + TypeScript + TailwindCSS stack

### Remove/Simplify:

- ❌ Complex multi-agent workflows
- ❌ One-shot query processing
- ❌ Complex prompts (handled by MCP server)
- ❌ CSV Analysis agent
- ❌ Query Classifier

## 🏗️ Implementation Plan

### Step 1: Project Setup

```bash
# Copy existing project
cp -r /Users/peterdonaghey/Projects/upc_query_agent /Users/peterdonaghey/Projects/point-topic-chat-client

# Rename and clean up
cd /Users/peterdonaghey/Projects/point-topic-chat-client
# Remove complex agents, keep basic structure
```

### Step 2: Backend Changes

**New Dependencies:**

```python
# Add to requirements.txt
pydantic-ai[mcp]  # For MCP client functionality
```

**Core Backend Changes:**

1. **Replace agents/** with simple **chat_agent.py**
2. **Add MCP integration** - Connect to Point Topic MCP server:

   ```python
   from pydantic_ai import Agent
   from pydantic_ai.mcp import MCPServerStreamableHTTP

   # Point Topic MCP server integration
   point_topic_server = MCPServerStreamableHTTP(
       url="http://localhost:8000/mcp",
       headers={"Authorization": "Bearer pt_live_sk_7f8e9d0c1b2a3456789abcdef0123456"}
   )

   chat_agent = Agent(
       model="claude-3-5-sonnet",
       toolsets=[point_topic_server]
   )
   ```

3. **Update API routes** - Replace `/query` with `/chat` endpoints for conversation flow

### Step 3: Frontend Changes

**Current Frontend:** `/frontend/src/`

- Uses React Query for API calls
- Has authentication flow
- One-shot query interface

**New Frontend Requirements:**

- **Chat interface** - Message bubbles, input field
- **Conversation history** - Show full chat thread
- **Streaming responses** - Real-time agent responses
- **Tool usage indicators** - Show when MCP tools are being used

**Keep existing:**

- Authentication system
- User management
- React + TypeScript + TailwindCSS setup

### Step 4: Database Schema

**Keep existing user tables**

**Update message history table:**

```sql
-- Modify existing query_log table for chat messages
ALTER TABLE query_log ADD COLUMN conversation_id VARCHAR(255);
ALTER TABLE query_log ADD COLUMN message_type VARCHAR(50); -- 'user' or 'assistant'
ALTER TABLE query_log ADD COLUMN parent_message_id VARCHAR(255);
```

## 🎯 Core Features (Keep It Basic!)

### Backend Features:

1. **Chat API** - RESTful endpoints for conversation
2. **MCP Integration** - Connect to Point Topic MCP server
3. **User Auth** - Existing system
4. **Message History** - Store conversation threads

### Frontend Features:

1. **Chat Interface** - Simple message bubbles
2. **Real-time Updates** - Show agent thinking/responding
3. **Tool Usage Display** - Show when UK broadband data tools are used
4. **Conversation Management** - Start new chats, view history

## 🧪 Testing Strategy

1. **Local Testing:**

   - Point Topic MCP server running on `localhost:8000`
   - Chat client connects and can use tools
   - Authentication works
   - Messages saved to database

2. **MCP Tools Testing:**
   - `assemble_dataset_context` - Should work via chat
   - `execute_query` - Should work via chat
   - `check_user_permissions` - Should work via chat

## 🚀 Success Criteria

**Agent can successfully:**

1. Start a conversation with the chat client
2. Ask questions about UK broadband data
3. Agent uses Point Topic MCP tools to answer
4. Conversation flows naturally (follow-up questions work)
5. Message history is preserved

## 📁 File Structure (After Cleanup)

```
point-topic-chat-client/
├── api/
│   ├── api_server.py              # Keep, minimal changes
│   ├── auth_handler.py            # Keep unchanged
│   ├── routes/
│   │   ├── auth.py                # Keep unchanged
│   │   ├── user.py                # Keep unchanged
│   │   ├── history.py             # Modify for chat history
│   │   ├── chat.py                # NEW - replace query.py
│   │   └── static.py              # Keep unchanged
│   └── services/                  # Keep unchanged
├── core/
│   └── snowflake_connector.py     # Keep unchanged
├── agents/                        # REMOVE - replace with:
├── chat/
│   ├── chat_agent.py              # NEW - Simple Pydantic AI + MCP
│   └── mcp_integration.py         # NEW - MCP server connections
├── frontend/                      # Keep structure, update components
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/              # NEW - Chat interface
│   │   │   └── ...                # Keep existing auth components
│   │   └── pages/
│   │       ├── ChatPage.tsx       # NEW - Main chat interface
│   │       └── ...                # Keep existing pages
└── requirements.txt               # Add pydantic-ai[mcp]
```

## 🔮 Next Steps for Implementation

1. **Copy and rename project**
2. **Strip out complex agents**
3. **Add MCP integration with Point Topic server**
4. **Build simple chat interface**
5. **Test conversation flow**
6. **Deploy and celebrate!** 🎉

---

_The future is conversational MCP! While others struggle with broken clients, we'll have the only working solution._ 🧙‍♂️✨
