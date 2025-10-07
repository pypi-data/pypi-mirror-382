# MCP Transport Authentication Requirements - CRITICAL CLARIFICATION

## 🚨 Transport Authentication Matrix

| Transport           | Authentication         | Status            | Notes                      |
| ------------------- | ---------------------- | ----------------- | -------------------------- |
| **Streamable HTTP** | **OAuth 2.1 REQUIRED** | New Standard      | API keys NOT supported     |
| **SSE**             | OAuth 2.1 OR API Keys  | Legacy/Compatible | More flexible auth options |
| **stdio**           | Environment vars       | Local only        | No network auth needed     |

## 🔥 Key Findings

### Streamable HTTP Transport (NEW - Protocol 2025-03-26)

- **MANDATES OAuth 2.1 authentication**
- Must implement RFC8414 (Authorization Server Metadata)
- Must support RFC7591 (Dynamic Client Registration)
- Protected Resource Metadata (RFC9728) required
- **API keys are NOT supported**

### SSE Transport (LEGACY - Protocol 2024-11-05)

- **Flexible authentication options**
- Can use OAuth 2.1 OR simpler methods (API keys, Bearer tokens)
- Still widely supported for compatibility
- No requirement for complex OAuth flows

## 💡 What This Means

### Current Setup Analysis

- ✅ `server_remote_sse.py` - **Works with API keys** (SSE transport)
- ❌ `server_remote.py` - **Requires OAuth** (HTTP transport)

### For Production MCP Deployment

- **Option 1**: Use SSE transport + API keys (current working setup)
- **Option 2**: Implement OAuth 2.1 for HTTP transport (future-proof)
- **Option 3**: Hybrid - support both transports

## 🔧 OAuth 2.1 Implementation Requirements

### Required Endpoints

```
/.well-known/oauth-authorization-server  # Auth server metadata
/.well-known/oauth-protected-resource    # Resource metadata
/oauth/authorize                         # Authorization endpoint
/oauth/token                            # Token endpoint
/oauth/register                         # Dynamic client registration
```

### AWS Cognito Integration

- ✅ **Supports OAuth 2.1 flows**
- ✅ **Authorization Code + PKCE**
- ✅ **Client Credentials flow**
- ⚠️ **Manual DCR implementation** needed (API Gateway + Lambda)
- ✅ **Well documented** examples available

## 📋 Recommendation Impact

### Short Term (UPC Query Agent)

- **Use SSE transport** (`server_remote_sse.py`)
- Keep API key authentication
- Works immediately with current setup

### Long Term (Enterprise Production)

- **Implement OAuth 2.1** with AWS Cognito
- Support both SSE (compatibility) and HTTP (future)
- Align with enterprise TypeScript system

## 🔗 Key Resources Saved

- `mcp_oauth_authorization_spec.md` - Official MCP OAuth spec
- `auth0_mcp_oauth_guide.md` - Comprehensive OAuth guide
- `aws_cognito_mcp_oauth_implementation.md` - AWS implementation
- `mcp_oauth2_aws_cognito_example.md` - Working code example
- `aws_bedrock_mcp_cognito.md` - Bedrock MCP integration

## 🎯 Bottom Line

**The transport choice determines authentication complexity:**

- **SSE = Simple API keys work**
- **HTTP = OAuth 2.1 required**

Your current SSE setup is perfect for immediate UPC agent integration!
