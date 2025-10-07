# User-Based Permissions & Access Control for MCP Servers

## Overview

With OAuth authentication, your MCP server can implement sophisticated **role-based access control** at multiple levels:

1. **Tool-level**: Show different tools to different users
2. **Parameter-level**: Same tool, different behavior based on user role
3. **Data-level**: Same tool, different data access based on permissions

## What User Info We Get From OAuth

### GitHub OAuth provides:

- `username` - GitHub username (e.g., "peterdonaghey")
- `email` - User's email address
- `organizations` - GitHub orgs they belong to
- `teams` - Teams within those orgs (with additional API call)

### Google OAuth provides:

- `email` - User's email address
- `name` - Full name
- `domain` - Email domain (for workspace users)
- `groups` - Google Workspace groups (if configured)

## Access Control Strategies

### 1. Tool-Level Access Control

Show different tools to different users:

```python
@mcp.tool()
def list_tools(request_context):
    user = request_context.user  # From OAuth token
    tools = []

    # Basic tools for everyone
    tools.extend(['assemble_dataset_context', 'execute_basic_query'])

    # Premium tools for specific users/orgs
    if user.email.endswith('@point-topic.com') or 'premium-users' in user.github_orgs:
        tools.extend(['execute_advanced_query', 'get_detailed_forecasts'])

    # Admin tools for admins only
    if user.email in ADMIN_EMAILS or 'admin' in user.github_teams:
        tools.extend(['execute_raw_query', 'manage_datasets'])

    return tools
```

### 2. Parameter-Level Access Control

Same tool, different behavior based on user role:

```python
@mcp.tool()
def execute_query(sql_query: str, request_context):
    user = request_context.user

    # Determine user's data access level
    if user.email.endswith('@point-topic.com'):
        access_level = 'full'
    elif 'premium-subscribers' in user.github_orgs:
        access_level = 'premium'
    else:
        access_level = 'basic'

    # Modify query based on access level
    if access_level == 'basic':
        # Only aggregated data, no postcode-level detail
        if 'postcode' in sql_query.lower():
            return "Error: Postcode-level data requires premium access"

    elif access_level == 'premium':
        # Allow detailed data but add row limits
        sql_query += " LIMIT 10000"

    # Full access gets unrestricted queries

    return execute_with_user_context(sql_query, user)
```

### 3. Data-Level Access Control

Same tool, different data based on permissions:

```python
@mcp.tool()
def assemble_dataset_context(dataset_names: List[str], request_context):
    user = request_context.user

    # Define dataset access matrix
    dataset_permissions = {
        'upc': ['basic', 'premium', 'full'],
        'upc_take_up': ['premium', 'full'],  # Premium subscribers only
        'upc_forecast': ['full'],  # Point Topic employees only
        'ontology': ['basic', 'premium', 'full']
    }

    user_level = get_user_access_level(user)

    # Filter datasets based on permissions
    allowed_datasets = [
        ds for ds in dataset_names
        if user_level in dataset_permissions.get(ds, [])
    ]

    if not allowed_datasets:
        return f"Error: User {user.email} has no access to requested datasets"

    return assemble_context(allowed_datasets, user_context=user)
```

## Real-World Example for UK Broadband Data

```python
def get_user_access_level(user) -> str:
    """Determine user's access level based on OAuth info"""

    # Point Topic employees get full access
    if user.email.endswith('@point-topic.com'):
        return 'full'

    # GitHub org members get premium access
    if 'uk-broadband-subscribers' in user.github_orgs:
        return 'premium'

    # Specific email domains get premium access
    if any(user.email.endswith(domain) for domain in PREMIUM_DOMAINS):
        return 'premium'

    # Everyone else gets basic access
    return 'basic'

# Usage in tools
@mcp.tool()
def execute_query(sql_query: str, request_context):
    user = request_context.user
    access_level = get_user_access_level(user)

    query_restrictions = {
        'basic': {
            'allowed_tables': ['upc_output'],  # Only summary data
            'row_limit': 1000,
            'forbidden_columns': ['detailed_premises_data']
        },
        'premium': {
            'allowed_tables': ['upc_output', 'fact_operator'],
            'row_limit': 50000,
            'forbidden_columns': []
        },
        'full': {
            'allowed_tables': '*',  # All tables
            'row_limit': None,  # No limits
            'forbidden_columns': []
        }
    }

    # Apply restrictions before executing
    validated_query = apply_restrictions(sql_query, query_restrictions[access_level])

    # Log with user context
    log_query(validated_query, user.email, access_level)

    return sf.execute_safe_query(validated_query)
```

## Access Control Configuration

Configure via environment variables or config files:

```bash
# .env
ADMIN_EMAILS=peter@point-topic.com,admin@company.com
PREMIUM_DOMAINS=point-topic.com,licensed-company.com
PREMIUM_GITHUB_ORGS=uk-broadband-subscribers,data-partners

# GitHub team-based access
GITHUB_ADMIN_TEAM=point-topic/admin
GITHUB_PREMIUM_TEAM=point-topic/premium-users
```

## Business Use Cases for UK Broadband Data

### Freemium Model

- **Basic users**: Aggregated data only, 1000 row limit
- **Premium users**: Postcode-level data, 50k row limit
- **Enterprise users**: Full database access, no limits

### Client Licensing

- **Point Topic employees**: All datasets + admin tools
- **Licensed clients**: Specific datasets based on contract
- **Public users**: Summary data only

### Team-Based Access

- **GitHub org "broadband-analysts"**: Premium data access
- **GitHub team "point-topic/admin"**: Server management tools
- **Domain "@regulator.gov.uk"**: Special regulatory dataset access

## Implementation in FastMCP

```python
# Enhanced server with user context
@mcp.tool()
def execute_query(sql_query: str, **kwargs):
    # FastMCP automatically injects user context
    user_token = kwargs.get('_mcp_user_token')
    user_info = extract_user_info(user_token)

    # Apply user-based logic
    access_level = get_user_access_level(user_info)
    return execute_with_permissions(sql_query, access_level, user_info)

def extract_user_info(token):
    """Extract user info from OAuth token"""
    # For GitHub OAuth
    return {
        'username': token.claims.get('login'),
        'email': token.claims.get('email'),
        'github_orgs': get_user_orgs(token.access_token),
        'github_teams': get_user_teams(token.access_token)
    }
```

## Audit & Logging

```python
def log_query(query: str, user_email: str, access_level: str):
    """Log all queries with user context for compliance"""
    log_entry = {
        'timestamp': datetime.utcnow(),
        'user': user_email,
        'access_level': access_level,
        'query': query,
        'query_hash': hashlib.sha256(query.encode()).hexdigest()
    }

    # Log to file/database for audit trail
    audit_logger.info(json.dumps(log_entry))
```

This system gives you:

- **Complete access control** over who sees what data
- **Flexible business models** (freemium, enterprise licensing)
- **Compliance-ready** audit trails
- **GitHub/Google integration** for easy user management
- **Scalable permissions** as your user base grows

Perfect for protecting valuable UK broadband data while providing controlled access to different user tiers!

