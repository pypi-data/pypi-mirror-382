# API Key Authentication Implementation - Agent Handoff

## 🎯 **OBJECTIVE**

Replace the current OAuth authentication system with a simple, robust API key authentication system for the MCP server. This will allow colleagues to connect from anywhere without OAuth complexity.

## 📍 **CURRENT STATE**

### ✅ **What Works**

- **Local server** (`server_local.py`) - Works perfectly with Claude Desktop via stdio
- **User permission system** (`config/users.yaml`) - Excellent email-based access control with 3 levels (basic, premium, full)
- **MCP tools** (`src/tools/mcp_tools.py`) - All working with user restrictions
- **Core functionality** - Dataset context assembly, query execution, permission checking

### 🚨 **What Needs Fixing**

- **Remote server** (`server_remote.py`) - Currently uses OAuth but user wants API key auth instead
- **OAuth is too complex** for the current use case (colleagues need simple access)
- **MCP ecosystem is too new** - OAuth client support is inconsistent across MCP clients
- **Need public deployment** - Server must work from anywhere, not just localhost

## 🔧 **IMPLEMENTATION REQUIREMENTS**

### **API Key Authentication Flow**

1. **User generates API keys** manually for each colleague
2. **API keys stored** in `config/users.yaml` alongside user permissions
3. **Colleagues configure MCP clients** with server URL + API key in Authorization header
4. **Server validates API key** and maps to user email for permission enforcement
5. **Existing user restriction system** continues to work unchanged

### **Configuration Example**

```yaml
# config/users.yaml (ADD api_key field)
users:
  peter.donaghey@point-topic.com:
    access_level: full
    name: "Peter Donaghey"
    api_key: "pt_live_sk_1a2b3c4d5e6f7g8h9i0j" # NEW FIELD

  colleague@company.com:
    access_level: premium
    name: "Colleague Name"
    api_key: "pt_live_sk_9i8h7g6f5e4d3c2b1a0j" # NEW FIELD
```

### **Client Configuration Example**

```json
// Colleague's MCP client config (e.g., ~/.cursor/mcp.json)
{
  "mcpServers": {
    "point-topic": {
      "type": "streamable-http",
      "url": "https://your-deployed-server.com/mcp",
      "headers": {
        "Authorization": "Bearer pt_live_sk_1a2b3c4d5e6f7g8h9i0j"
      }
    }
  }
}
```

## 📂 **KEY FILES TO MODIFY**

### **1. server_remote.py** (MAIN CHANGES)

- **REMOVE**: All OAuth imports and GitHubTokenVerifier
- **REMOVE**: AuthSettings and OAuth configuration
- **ADD**: Simple API key token verifier
- **KEEP**: FastMCP structure and tool registration

### **2. config/users.yaml** (ADD FIELD)

- Add `api_key` field to each user
- Keep existing permission structure unchanged

### **3. src/auth/user_manager.py** (ADD METHOD)

- Add method: `get_user_by_api_key(api_key: str) -> UserInfo`
- Keep all existing methods unchanged

### **4. NEW FILE: src/auth/api_key_verifier.py**

- Implement `ApiKeyTokenVerifier(TokenVerifier)` class
- Validate API key format and lookup user
- Return AccessToken with user context

## 🔍 **REFERENCE FILES**

### **Existing Working Code**

- `src/auth/user_manager.py` - User permission system (DO NOT BREAK THIS)
- `src/tools/mcp_tools.py` - MCP tools with user context (minor updates needed)
- `server_local.py` - Perfect reference for non-auth server structure

### **Documentation References**

- `.dev/official_mcp_sdk_readme.md` - Official MCP SDK patterns (lines 821-889 for auth)
- `.dev/mcp_inspector_docs.md` - MCP Inspector usage and testing
- `config/users.yaml` - Existing user permission structure

### **Current OAuth Implementation (TO REPLACE)**

- `server_remote.py` - Current OAuth server (replace auth, keep structure)
- `src/auth/github_token_verifier.py` - OAuth verifier (use as template for API key verifier)

## 🧪 **TESTING STRATEGY**

### **1. Local Testing**

```bash
# Start API key server
python server_remote.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector
# Configure: transport=streamable-http, url=http://localhost:8000/mcp
# Add Authorization header: Bearer <api-key>
```

### **2. Authentication Testing**

- Test unauthenticated requests (should be rejected)
- Test with valid API key (should work with user permissions)
- Test with invalid API key (should be rejected)
- Test user permission enforcement (basic vs premium vs full access)

### **3. Success Criteria**

- ✅ Server starts without OAuth dependencies
- ✅ API key validation works
- ✅ User permissions enforced correctly
- ✅ Tools apply dataset restrictions and row limits
- ✅ MCP Inspector can connect and authenticate
- ✅ Ready for public deployment

## 🚀 **DEPLOYMENT READINESS**

Once API key auth works locally:

1. **Deploy to cloud** (Railway, Vercel, AWS)
2. **Share server URL** with colleagues
3. **Generate API keys** for each colleague
4. **Colleagues add server** to their MCP client configs

## ⚠️ **CRITICAL REQUIREMENTS**

1. **DO NOT BREAK** the existing user permission system in `config/users.yaml`
2. **DO NOT BREAK** the local server (`server_local.py`)
3. **KEEP** all existing MCP tools functionality
4. **ENSURE** API key format is secure (suggest: `pt_live_sk_` prefix + 32 random chars)
5. **VALIDATE** API keys properly (timing-safe comparison)
6. **PRESERVE** existing user email-based permission mapping

## 📋 **IMPLEMENTATION ORDER**

1. **Create ApiKeyTokenVerifier** class (copy pattern from GitHubTokenVerifier)
2. **Update user_manager.py** to support API key lookup
3. **Modify server_remote.py** to use API key auth instead of OAuth
4. **Update config/users.yaml** with example API keys
5. **Test locally** with MCP Inspector
6. **Verify** user permissions still work correctly
7. **Document** API key generation process

## 🎯 **END GOAL**

A simple, robust MCP server that:

- Accepts API key authentication via Authorization header
- Applies existing user permissions from `config/users.yaml`
- Can be deployed publicly and accessed by colleagues from anywhere
- Maintains all existing functionality while removing OAuth complexity

**The user wants this to be bulletproof and simple - no OAuth, no complexity, just API keys that work reliably.**
