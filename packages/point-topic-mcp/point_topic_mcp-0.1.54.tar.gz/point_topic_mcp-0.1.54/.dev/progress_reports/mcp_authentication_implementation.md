# MCP Authentication & Remote Access Implementation Report

## Executive Summary

After analyzing the [MCP Course #15 video on Google Sign In](https://www.youtube.com/watch?v=zDfz_Gsj_QA) and the [official MCP Python SDK authentication docs](https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#authentication), I've identified multiple approaches for adding authentication to your Point Topic MCP server and making it remotely accessible.

## Key Insights from Video Analysis

### FastMCP OAuth Proxy Pattern

The video demonstrates using **FastMCP 2.0+** with Google OAuth as an authorization server:

- **OAuth Proxy Architecture**: The MCP server acts as both resource server AND OAuth proxy
- **Google Integration**: Uses Google Cloud Console credentials (client ID/secret)
- **PKCE Support**: Implements Proof Key for Code Exchange for security
- **Dynamic Client Registration**: Handles varying client redirect URIs
- **Streamable HTTP**: Uses HTTP transport instead of stdio for remote access

### Why OAuth Proxy is Brilliant

- **Security**: Client credentials stay on server, not exposed to all MCP clients
- **Compatibility**: Bridges gap between OAuth providers (Google) and MCP client requirements
- **Maintainability**: Library handles complex OAuth flows so you don't have to

## Current Point Topic MCP Server Analysis

### What We Have

```
Point Topic MCP Server
├── FastMCP-based server (local stdio only)
├── Snowflake database connector with proper auth
├── Three tools:
│   ├── assemble_dataset_context() - Gets DB schemas/examples
│   ├── execute_query() - Runs safe SQL queries
│   └── (commented out tools for distinct values)
├── Dataset context assembly system
│   ├── upc - Infrastructure availability data
│   ├── upc_take_up - Subscriber estimates
│   └── upc_forecast - Predictive forecasting
│   └── ontology - Broadband entity ontology
└── Environment-based configuration
```

### Current Limitations

- **Local Only**: Uses stdio transport (Claude Desktop only)
- **No Authentication**: Open access to anyone with MCP client
- **Single User**: No user identification or access control

## Authentication Implementation Options

### Option 1: FastMCP OAuth Proxy (Recommended)

#### GitHub OAuth Implementation (Preferred)

```python
from fastmcp import FastMCP
from fastmcp.auth import GitHubOAuthProvider

# GitHub OAuth provider setup
github_oauth = GitHubOAuthProvider(
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    base_url=os.getenv('MCP_BASE_URL', 'http://localhost:8005'),
    redirect_path='/oauth/callback',
    required_scopes=['user:email', 'read:user'],
    allowed_client_redirects=['http://localhost:*', 'http://127.0.0.1:*']
)

# Create authenticated MCP server
mcp = FastMCP(
    name="Point Topic MCP",
    instructions="Protected UK broadband data analysis server",
    oauth=github_oauth
)
```

#### Google OAuth Implementation (Alternative)

```python
from fastmcp import FastMCP
from fastmcp.auth import GoogleOAuthProvider

# Google OAuth provider setup
google_oauth = GoogleOAuthProvider(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    base_url=os.getenv('MCP_BASE_URL', 'http://localhost:8005'),
    redirect_path='/oauth/callback',
    required_scopes=['openid', 'profile', 'email'],
    allowed_client_redirects=['http://localhost:*', 'http://127.0.0.1:*']
)
```

#### Multi-Provider Support

```python
# Dynamic provider selection based on environment
provider = os.getenv('OAUTH_PROVIDER', 'github')
if provider == 'github':
    oauth_provider = github_oauth
elif provider == 'google':
    oauth_provider = google_oauth
elif provider == 'multi':
    # Support both providers with fallback logic
    oauth_provider = MultiOAuthProvider([github_oauth, google_oauth])
```

### Option 2: Official MCP SDK OAuth (Alternative)

Using the official Python SDK's `OAuthClientProvider`:

```python
from mcp.client.auth import OAuthClientProvider
from mcp.client.streamable_http import streamablehttp_client

# For clients connecting to authenticated servers
oauth_auth = OAuthClientProvider(
    server_url="http://your-server:8005",
    client_metadata=OAuthClientMetadata(...),
    storage=TokenStorage(),
    redirect_handler=handle_redirect,
    callback_handler=handle_callback,
)
```

## OAuth Provider Setup Options

### Option A: GitHub OAuth (Recommended for Developers)

1. **GitHub Developer Settings**:

   - Go to GitHub > Settings > Developer settings > OAuth Apps
   - Create new OAuth App with:
     - Homepage URL: `http://localhost:8005`
     - Authorization callback URL: `http://localhost:8005/oauth/callback`
   - Copy Client ID and generate Client Secret

2. **Environment Variables**:

   ```bash
   OAUTH_PROVIDER=github
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   OAUTH_SCOPES=user:email read:user
   ```

3. **Benefits**:
   - Familiar to developers
   - No Google Cloud Console complexity
   - Can restrict by GitHub org/team membership
   - Built-in user identification via GitHub username

### Option B: Google OAuth (From Video Tutorial)

1. **Google Cloud Console**:

   - Create OAuth 2.0 Client ID
   - Set authorized redirect URIs: `http://localhost:8005/oauth/callback`
   - Set authorized JavaScript origins: `http://localhost:8005`, `http://127.0.0.1:8005`
   - Download client credentials (ID + secret)

2. **OAuth Consent Screen**:

   - Configure app name and details
   - Add required scopes: `openid`, `profile`, `email`
   - Set to external (for testing) or internal (for org only)

3. **Environment Variables**:
   ```bash
   OAUTH_PROVIDER=google
   GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret
   OAUTH_SCOPES=openid profile email
   ```

### Option C: Multi-Provider Support

Support both providers simultaneously:

```bash
OAUTH_PROVIDER=multi
# Include both GitHub and Google credentials
```

## Remote Access Implementation

### HTTP Transport Setup

Convert from stdio to streamable HTTP:

```python
# Instead of stdio (local only)
if __name__ == "__main__":
    mcp.run()

# Use HTTP transport (remote capable)
if __name__ == "__main__":
    mcp.run(
        transport="streamable_http",
        host=os.getenv('MCP_SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('MCP_SERVER_PORT', 8005)),
        mcp_path="/mcp"
    )
```

### Deployment Considerations

- **HTTPS**: For production, use reverse proxy (nginx) with SSL certificates
- **Firewall**: Open port 8005 (or configured port) for incoming connections
- **Environment**: Secure storage of OAuth credentials and Snowflake credentials
- **Logging**: Implement proper request/auth logging for security monitoring

## Security Architecture

```
User → MCP Client → HTTP → Your MCP Server (OAuth Proxy) → Google OAuth → Snowflake
                            ↓
                    Protected Tools:
                    - assemble_dataset_context()
                    - execute_query()
```

### Security Benefits

- **User Identity**: Tools can access authenticated user info from OAuth token
- **Access Control**: Can restrict tools based on user email/domain
- **Audit Trail**: Log all queries with user identification
- **Token Management**: OAuth refresh tokens for session persistence

## Implementation Plan

### Phase 1: Local OAuth Setup

1. ✅ Create `.env.template` with required variables
2. 🔄 Convert server to FastMCP with OAuth
3. 🔄 Add HTTP transport
4. 🔄 Test local authentication flow

### Phase 2: Remote Deployment

1. Configure reverse proxy with HTTPS
2. Deploy to cloud server (or expose local with ngrok for testing)
3. Update OAuth redirect URIs in Google Console
4. Test remote access

### Phase 3: Enhanced Security

1. Add user-based access control to tools
2. Implement query logging with user identification
3. Add rate limiting and monitoring
4. Document security procedures

## User Experience Flow

1. **Client Discovery**: MCP client hits `/mcp` endpoint
2. **Authentication Challenge**: Server returns 401 with OAuth metadata
3. **OAuth Flow**: Client redirects user to Google sign-in
4. **Token Exchange**: Server exchanges auth code for access token
5. **Tool Access**: Client can now call protected tools with bearer token
6. **User Context**: Tools can access user info from validated token

## Dependencies Required

Add to `pyproject.toml`:

```toml
dependencies = [
    "httpx>=0.28.1",
    "mcp[cli]>=1.14.0",
    "snowflake-connector-python[pandas]>=3.17.3",
    "python-dotenv>=1.0.0",  # For environment variables
    "fastmcp>=2.0.0",  # For OAuth proxy (if using FastMCP approach)
]
```

## Next Steps

1. **Choose Implementation**: FastMCP OAuth proxy (recommended) vs official SDK approach
2. **Google Cloud Setup**: Create OAuth credentials
3. **Environment Configuration**: Copy `.env.template` to `.env` and configure
4. **Code Implementation**: Convert server to authenticated HTTP transport
5. **Testing**: Local authentication flow first, then remote deployment

## OAuth Provider Comparison

| Feature                | GitHub OAuth          | Google OAuth    |
| ---------------------- | --------------------- | --------------- |
| **Setup Complexity**   | ⭐⭐⭐⭐⭐ Simple     | ⭐⭐⭐ Moderate |
| **Developer Friendly** | ⭐⭐⭐⭐⭐ Native fit | ⭐⭐⭐ Good     |
| **User Base**          | Developers/Tech       | General users   |
| **Access Control**     | Org/Team membership   | Domain/Groups   |
| **User Identity**      | GitHub username       | Email/Name      |
| **Rate Limits**        | Generous              | Generous        |

**Recommendation**: Start with **GitHub OAuth** - it's simpler to set up and perfect for a developer-focused MCP server. Can always add Google later.

## Questions for Peter

1. **OAuth Provider Preference**: GitHub (recommended), Google, or both?
2. **Access Control**: Should we restrict by GitHub org membership or keep it open?
3. **Deployment Target**: Cloud server, local with ngrok, or other?
4. **Monitoring**: Need specific logging/monitoring requirements?

---

_This implementation will transform your local-only MCP server into a secure, remotely accessible service while maintaining all existing UK broadband data analysis capabilities._
