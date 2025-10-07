# Cloudflare MCP Server Capabilities

## ✅ What Cloudflare Offers for MCP

### 🎯 Native MCP Support

- **McpAgent class** in Agents SDK - built-in MCP server capabilities
- **Streamable HTTP transport** - latest MCP standard supported
- **SSE transport** - backward compatibility with existing clients
- **OAuth 2.1 provider** - built-in authentication/authorization
- **Durable Objects** - stateful MCP servers with SQL storage

### 🚀 Deployment Options

#### 1. TypeScript/JavaScript MCP Servers

- ✅ **Full production support**
- ✅ **One-click deployment** templates
- ✅ **Complete package ecosystem**
- ✅ **OAuth provider included**
- ✅ **Auto-scaling and hibernation**

#### 2. Python MCP Servers

- ⚠️ **BETA - Limited production support**
- ✅ **FastAPI supported** (local dev only)
- ❌ **No external packages in production**
- ❌ **Standard library only**
- ⚠️ **Development experience rough**

## 🔧 Built-in Features

### Authentication & Authorization

```typescript
// Automatic OAuth handling
class MyMcpServer extends McpAgent {
  // User details automatically provided
  async myTool(input, user) {
    // user.id, user.email available
  }
}
```

### State Management

- **Durable Objects** with SQLite storage
- **Automatic hibernation** during idle periods
- **Global state persistence**

### Transport Support

- **Streamable HTTP** (latest MCP spec)
- **Server-Sent Events** (SSE) for compatibility
- **WebSocket** with hibernation support

## 🛠️ Development Experience

### Local Development

```bash
npm create cloudflare@latest my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-authless
npm start  # http://localhost:8788/sse
```

### Testing

- **MCP Inspector** integration
- **AI Playground** as remote MCP client
- **Claude Desktop** via mcp-remote proxy

### Deployment

```bash
npx wrangler@latest deploy
# Instant global deployment
```

## 🌍 Global Infrastructure

- **285+ edge locations**
- **Automatic global distribution**
- **Zero cold starts**
- **Built-in DDoS protection**

## 📋 Supported MCP Features

✅ **Tools** - Function calls from AI agents  
✅ **Resources** - Data/content exposure  
✅ **Prompts** - Template management  
✅ **OAuth** - Authentication flows  
✅ **Scoped permissions** - Fine-grained access control  
✅ **Multi-client support** - Multiple simultaneous connections

## 🔄 Client Compatibility

### Direct Remote Support

- **Claude** (via AI Playground)
- **Windsurf**
- **Any MCP SDK** with remote transport

### Via Proxy (mcp-remote)

- **Claude Desktop**
- **Cursor**
- **Cline**
- **Other stdio-based clients**

## 💰 Pricing for MCP Servers

- **Free tier**: 100K requests/day, 10ms CPU time
- **Paid**: $5/month + usage (very cost-effective)
- **No bandwidth charges**
- **Global deployment included**

## 🚨 Current Gaps

- **Python production limitations** (packages not supported)
- **Learning curve** for McpAgent class
- **Beta status** for some features
- **Documentation still evolving**

## 🎯 Best Use Cases

1. **TypeScript/JavaScript MCP servers** - Excellent choice
2. **Global distribution needs** - Perfect fit
3. **OAuth authentication required** - Built-in support
4. **Cost-sensitive projects** - Very competitive pricing
5. **Rapid prototyping** - One-click deployment
