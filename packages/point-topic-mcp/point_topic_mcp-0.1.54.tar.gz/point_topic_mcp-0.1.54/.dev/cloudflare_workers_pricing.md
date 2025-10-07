# Cloudflare Workers Pricing Analysis

## 🆓 Free Tier

- **100,000 requests per day**
- **10ms CPU time per invocation**
- No duration charges
- **No bandwidth/egress charges**

## 💰 Paid Plan ($5/month minimum)

- **10 million requests included** + $0.30 per additional million
- **30 million CPU milliseconds included** + $0.02 per additional million CPU-ms
- Max 5 minutes CPU time per invocation (default: 30 seconds)
- **No duration or bandwidth charges**

## 📊 Cost Examples

### Example 1: Moderate Traffic MCP Server

- 15M requests/month, 7ms CPU time per request
- **Monthly Cost: $8.00**
  - Subscription: $5.00
  - Requests: $1.50 (5M excess × $0.30)
  - CPU time: $1.50 (75M excess CPU-ms × $0.02)

### Example 2: High Traffic MCP Server

- 100M requests/month, 7ms CPU time per request
- **Monthly Cost: $45.40**
  - Subscription: $5.00
  - Requests: $27.00 (90M excess × $0.30)
  - CPU time: $13.40 (670M excess CPU-ms × $0.02)

### Example 3: Cron-Based Data Processing

- 720 requests/month, 3 minutes CPU time per request
- **Monthly Cost: $6.99**
  - Subscription: $5.00
  - CPU time: $1.99 (99.6M excess CPU-ms × $0.02)

## 🔑 Key Advantages

- **CPU-time based billing** - no charges for I/O wait time
- **Zero cold start latency** globally (V8 isolates)
- **Global edge deployment** at 285+ locations
- **Free static asset serving**
- **No egress/bandwidth charges**
- **Built-in DDoS protection**

## ⚡ Performance Benefits

- ~0ms cold starts (vs AWS Lambda 100-1000ms)
- Global edge execution
- Built-in auto-scaling
- No infrastructure management

## 🚨 Current Limitations for Python

- **Python Workers in BETA**
- **Packages DO NOT run in production** (only standard library)
- FastAPI works but limited to built-in packages only
- Must use `python_workers` compatibility flag

## 💡 Bottom Line

**Cloudflare Workers pricing is VERY competitive** - typically 40-80% cheaper than AWS Lambda for similar workloads, with better performance and global distribution.
