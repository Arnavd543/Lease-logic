# Deployment Guide: Streamlit Cloud vs Docker

Quick guide to help you choose the right deployment method for LeaseLogic.

## TL;DR Recommendations

**For You (Personal/Portfolio Project):**
- **Use Streamlit Cloud** - Easiest, free tier available, perfect for demos

**For Production/Enterprise:**
- **Use Docker** - More control, can deploy anywhere, better for scale

## Option 1: Streamlit Cloud (Recommended for You)

### Pros
- Free tier available
- Dead simple deployment (literally 3 clicks)
- Automatic HTTPS
- Built-in secrets management
- Auto-deploys on git push
- No server management
- Perfect for portfolio/demos

### Cons
- Limited to Streamlit hosting
- Less control over infrastructure
- Free tier has resource limits (800MB RAM)
- Can't customize deployment environment much

### Setup (5 minutes)

1. **Push to GitHub**
   ```bash
   cd /Users/arnav/projects/ai-lease/leaselogic
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/leaselogic.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Connect your GitHub repo
   - Select `app.py` as main file
   - Add secrets:
     ```
     OPENAI_API_KEY = "your-key"
     ```
   - Click "Deploy"

3. **Done!** Your app will be live at `https://yourapp.streamlit.app`

### Cost
- **Free tier**: 1 private app, 800MB RAM
- **Community tier**: $0/month (public apps)
- **Team tier**: $250/month (unlimited private apps)

**For your use case: FREE**

## Option 2: Docker (For Production)

### Pros
- Full control over deployment
- Can deploy anywhere (AWS, GCP, Azure, your own server)
- Easy to scale
- Consistent environment
- Good for enterprise/production
- Can customize resources

### Cons
- Need to manage infrastructure
- Costs money (server hosting)
- More complex setup
- Need to handle HTTPS, domain, etc.

### Setup (30 minutes)

1. **Build Docker Image**
   ```bash
   cd /Users/arnav/projects/ai-lease/leaselogic
   docker build -t leaselogic:latest .
   ```

2. **Run Locally**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-key" > .env

   # Run with docker-compose
   docker-compose up -d

   # View logs
   docker-compose logs -f

   # Access at http://localhost:8501
   ```

3. **Deploy to Cloud (Example: AWS EC2)**
   ```bash
   # SSH into EC2 instance
   ssh ubuntu@your-ec2-ip

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Clone repo
   git clone https://github.com/yourusername/leaselogic.git
   cd leaselogic

   # Create .env
   nano .env  # Add OPENAI_API_KEY

   # Run
   docker-compose up -d
   ```

4. **Set up HTTPS** (Optional but recommended)
   - Use nginx as reverse proxy
   - Get SSL cert from Let's Encrypt
   - Configure domain

### Cost Estimates

**AWS EC2 (t3.medium)**:
- Instance: $30/month
- Storage: $5/month
- Total: ~$35/month

**Digital Ocean Droplet**:
- 2GB RAM: $12/month
- 4GB RAM: $24/month

**Google Cloud Run** (Alternative):
- Pay per use
- ~$10-20/month for light usage

## Comparison Table

| Feature | Streamlit Cloud | Docker |
|---------|----------------|--------|
| **Setup Time** | 5 minutes | 30+ minutes |
| **Cost (Your Use)** | FREE | $12-35/month |
| **Maintenance** | Zero | Ongoing |
| **Scalability** | Limited | Unlimited |
| **Control** | Low | High |
| **Best For** | Demos, portfolios | Production, enterprise |
| **HTTPS** | Automatic | Manual setup |
| **Custom Domain** | Limited | Full control |
| **Resource Limits** | 800MB RAM | Configurable |

## My Recommendation for You

**Use Streamlit Cloud** for these reasons:

1. **You're building a portfolio project** - Streamlit Cloud is perfect for this
2. **It's free** - Docker costs $12-35/month minimum
3. **Zero maintenance** - No servers to manage
4. **Perfect for demos** - Share the link with employers/friends
5. **Easy updates** - Just push to GitHub, auto-deploys
6. **HTTPS included** - Secure by default

### When to Use Docker

Switch to Docker later if:
- You need more than 800MB RAM
- You want to monetize (need production infrastructure)
- You need custom domain with full control
- You're deploying in enterprise environment
- You need to integrate with other services

## Quick Start: Streamlit Cloud (Recommended)

```bash
# 1. Create GitHub repo (if not done)
cd /Users/arnav/projects/ai-lease/leaselogic
git init
git add .
git commit -m "LeaseLogic - AI lease analyzer"
git branch -M main

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/leaselogic.git
git push -u origin main

# 2. Deploy
# Go to https://share.streamlit.io
# Click "New app"
# Select your repo
# Add OPENAI_API_KEY in secrets
# Deploy

# Done! Live in ~2 minutes
```

## Quick Start: Docker (If Needed)

```bash
# 1. Local testing
cd /Users/arnav/projects/ai-lease/leaselogic
echo "OPENAI_API_KEY=your-key" > .env
docker-compose up

# Access at http://localhost:8501

# 2. Deploy to server
# Transfer files to server
scp -r . user@server:/app/leaselogic

# SSH into server
ssh user@server
cd /app/leaselogic
docker-compose up -d
```

## Performance Benchmarks

Run these to verify your deployment:

```bash
# Test query speed
./venv/bin/python tests/test_performance.py

# Expected results:
# - Average query time: 15-25s
# - Lease-only: ~10-15s (30% faster)
# - Law-only: ~10-15s (30% faster)
# - Quality: 7-9/10 average
```

## Next Steps After Deployment

1. **Test with Real Lease**
   - Upload your own lease
   - Ask various questions
   - Verify quality

2. **Monitor Costs**
   - Check OpenAI usage dashboard
   - Set up billing alerts
   - Track queries per day

3. **Share**
   - Add to portfolio
   - Share link on LinkedIn
   - Include in resume

4. **Iterate**
   - Gather feedback
   - Add more states
   - Improve quality

## Support

Questions? Check:
- `docs/DEPLOYMENT.md` - Full deployment guide
- `docs/ARCHITECTURE.md` - Technical details
- `README.md` - Project overview

## Summary

**For your AI lease analyzer portfolio project:**

**ANSWER: Use Streamlit Cloud**

- Free
- 5-minute setup
- Perfect for demos
- Easy to share
- No maintenance

Docker is great, but overkill for your current needs. You can always migrate later if needed.
