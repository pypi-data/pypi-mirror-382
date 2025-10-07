# GitHub OAuth Setup Instructions

## Step 1: Create GitHub OAuth App

1. Go to https://github.com/settings/applications/new
2. Fill in the application details:

   - **Application name**: `Point Topic MCP Server`
   - **Homepage URL**: `http://localhost:8000`
   - **Application description**: `Point Topic MCP Server with OAuth authentication`
   - **Authorization callback URL**: `http://localhost:8000/oauth/callback`

3. Click **Register application**
4. Copy the **Client ID** and **Client Secret**

## Step 2: Environment Configuration

Create a `.env` file in the project root with:

```bash
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here

# Server Configuration
OAUTH_ISSUER_URL=https://github.com/login/oauth
RESOURCE_SERVER_URL=http://localhost:8000
REQUIRED_SCOPES=user:email,read:user
```

## Step 3: Test Configuration

After setup, the OAuth flow will work as follows:

1. **MCP Inspector/Client** connects to `http://localhost:8000/mcp`
2. **Server** responds with OAuth metadata (RFC 9728)
3. **Client** redirects user to GitHub for authentication
4. **GitHub** redirects back with authorization code
5. **Client** exchanges code for access token
6. **Server** validates token with GitHub API and checks user permissions
7. **Authorized tools** become available based on user's email and access level

## Important Notes

- **Local server (`server_local.py`)** remains unchanged and auth-free
- **Remote server (`server_remote.py`)** gets OAuth authentication
- **Existing user system** in `config/users.yaml` is preserved
- **Email-based permissions** continue to work exactly as before

## Required Scopes

- `user:email` - Access to user's email address
- `read:user` - Access to basic user profile information

These scopes allow the server to:

1. Validate the GitHub access token
2. Retrieve the user's email address
3. Match email against existing user permissions in `config/users.yaml`
