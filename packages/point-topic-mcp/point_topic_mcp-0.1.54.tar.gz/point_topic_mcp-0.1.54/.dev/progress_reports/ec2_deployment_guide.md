# Point Topic MCP Server - EC2 Deployment Guide

## 🎯 Deployment Options

### Option 1: Simple Script (Recommended for Quick Start)
```bash
# Make executable and run
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

**What it does**:
- ✅ Creates t3.micro instance (~$7.50/month, FREE tier eligible)
- ✅ Sets up security groups (SSH + MCP port 8001)
- ✅ Installs Python, uv, git automatically
- ✅ Clones your repo and sets up systemd service
- ✅ Auto-starts MCP server on boot

### Option 2: AWS CDK (Infrastructure as Code)
```bash
cd infrastructure
pip install -r requirements.txt
cdk bootstrap  # One-time AWS account setup
cdk deploy
```

**Advantages**:
- ✅ Infrastructure as code (version controlled)
- ✅ Easy updates and teardown
- ✅ Professional deployment approach
- ✅ Easy to replicate across environments

### Option 3: Manual Launch (Learning/Testing)
```bash
# 1. Launch t3.micro instance via AWS Console
# 2. SSH in and run setup commands manually
# 3. Good for understanding the process
```

## 💰 Cost Breakdown

| Component | Cost/Month | Notes |
|-----------|------------|-------|
| **t3.micro** | $0 - $7.50 | FREE first year with free tier |
| **EBS Storage** | ~$1 | 8GB default volume |
| **Data Transfer** | ~$0 | 1GB free per month |
| **Total** | **~$1-8/month** | Incredibly cheap! |

## 🚀 After Deployment

### 1. Update Credentials
```bash
ssh -i point-topic-mcp-key.pem ec2-user@YOUR_IP
cd point-topic-mcp
nano .env  # Add real Snowflake credentials
sudo systemctl restart mcp-server
```

### 2. Update Users & API Keys
```bash
nano config/users.yaml  # Add colleague API keys
sudo systemctl restart mcp-server
```

### 3. Test Connection
```bash
# Test from UPC query agent
curl http://YOUR_IP:8001/sse
```

### 4. Monitor Service
```bash
# Check status
sudo systemctl status mcp-server

# View logs
sudo journalctl -u mcp-server -f

# Restart if needed
sudo systemctl restart mcp-server
```

## 🔧 Production Considerations

### Security Hardening
- ✅ Security group restricts access to necessary ports only
- ⚠️ Consider restricting SSH to your IP ranges
- ⚠️ Use AWS Systems Manager Session Manager instead of SSH

### Backup & Updates
```bash
# Create AMI snapshot periodically
aws ec2 create-image --instance-id i-1234567890abcdef0 --name "mcp-server-backup-$(date +%Y%m%d)"

# Update code
cd point-topic-mcp
git pull origin main
sudo systemctl restart mcp-server
```

### Monitoring
- CloudWatch logs automatically collected
- Set up CloudWatch alarms for instance health
- Monitor MCP endpoint availability

## 🎯 Connect UPC Query Agent

Update your UPC query agent configuration:

```python
# In your UPC query agent
MCP_SERVER_URL = "http://YOUR_EC2_IP:8001/sse"
API_KEY = "pt_live_sk_your_api_key_here"

# Test connection
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(f"{MCP_SERVER_URL}/tools", headers=headers)
```

## 🔗 Next Steps

1. **Deploy immediately** with simple script
2. **Test MCP integration** with UPC query agent  
3. **Monitor performance** and costs
4. **Plan OAuth migration** when enterprise system ready
5. **Scale up** if needed (bigger instances, load balancer, etc.)

Your MCP server will be live and accessible within 5-10 minutes! 🚀

