# Deployment Guide

Complete guide for deploying LeaseLogic to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
- [Docker Deployment](#docker-deployment)
- [Cost Optimization](#cost-optimization)
- [Production Considerations](#production-considerations)
- [Monitoring and Observability](#monitoring-and-observability)

## Prerequisites

### Required

- GitHub account for version control
- OpenAI API key with billing enabled
- Python 3.11+ runtime environment

### Optional

- LangSmith API key for tracing and evaluation
- Docker installation for containerized deployment
- Domain name for custom URL

### Pre-Deployment Checklist

- [ ] All environment variables documented
- [ ] No sensitive data committed to repository
- [ ] requirements.txt up to date
- [ ] Tests passing locally
- [ ] ChromaDB vector stores initialized
- [ ] Configuration files reviewed

## Streamlit Cloud Deployment

### Step 1: Prepare Repository

1. **Verify Project Structure**
   ```bash
   leaselogic/
   ├── app.py                 # Must be in root
   ├── requirements.txt       # All dependencies listed
   ├── config/config.yaml     # Configuration file
   ├── src/                   # Source code
   └── data/vector_stores/    # Pre-built vector stores
   ```

2. **Create `.gitignore`**
   ```
   # Environment
   .env
   venv/
   __pycache__/

   # Data
   temp_lease.pdf
   *.log

   # IDE
   .vscode/
   .idea/
   ```

3. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

### Step 2: Configure Streamlit Cloud

1. **Create Account**
   - Visit https://share.streamlit.io
   - Sign in with GitHub
   - Authorize Streamlit access to repositories

2. **Deploy Application**
   - Click "New app"
   - Select repository: `yourusername/leaselogic`
   - Set branch: `main`
   - Set main file path: `app.py`
   - Set Python version: `3.11`

3. **Configure Secrets**

   Navigate to App Settings > Secrets and add:
   ```toml
   OPENAI_API_KEY = "sk-..."
   LANGCHAIN_API_KEY = "ls__..."  # Optional
   LANGCHAIN_TRACING_V2 = "true"   # Optional
   LANGCHAIN_PROJECT = "LeaseLogic"  # Optional
   ```

4. **Advanced Settings** (Optional)
   - Increase memory limit if needed (default: 800MB)
   - Set custom domain if available
   - Configure timeout settings

### Step 3: Deploy and Test

1. Click "Deploy"
2. Monitor build logs for errors
3. Once deployed, test core functionality:
   - PDF upload
   - Query classification
   - All three query types (lease-only, law-only, both)
   - State selection

### Step 4: Post-Deployment Verification

**Test Checklist:**
- [ ] Application loads without errors
- [ ] PDF upload works
- [ ] Vector store loads correctly
- [ ] Queries return reasonable answers
- [ ] Classification works (check console logs if LangSmith enabled)
- [ ] Performance is acceptable (<30s per query)

## Docker Deployment

### Step 1: Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Create .dockerignore

```
# Version control
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.egg-info
venv/

# Environment
.env

# Documentation
*.md
docs/

# Tests
tests/
```

### Step 3: Build and Run

```bash
# Build image
docker build -t leaselogic:latest .

# Run container
docker run -d \
  --name leaselogic \
  -p 8501:8501 \
  --env-file .env \
  leaselogic:latest

# View logs
docker logs -f leaselogic

# Stop container
docker stop leaselogic

# Remove container
docker rm leaselogic
```

### Step 4: Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  leaselogic:
    build: .
    container_name: leaselogic
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./data/vector_stores:/app/data/vector_stores
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Usage:**
```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## Cost Optimization

### OpenAI API Costs

**Per-Query Breakdown (with intelligent routing):**

| Query Type | Components | Estimated Cost |
|-----------|------------|----------------|
| Comparison ("both") | Classifier + Lease + Law + Grading + Synthesis | $0.08 |
| Lease-only | Classifier + Lease + Grading + Synthesis | $0.05 |
| Law-only | Classifier + Law + Grading + Synthesis | $0.04 |

**Monthly Cost Estimates:**

| Usage Level | Queries/Month | Avg Cost/Query | Monthly Cost |
|-------------|---------------|----------------|--------------|
| Light | 100 | $0.06 | $6 |
| Medium | 500 | $0.06 | $30 |
| Heavy | 2,000 | $0.06 | $120 |

### Optimization Strategies

1. **Intelligent Query Routing** (Already Implemented)
   - Automatically skips unnecessary searches
   - Saves 38-50% on lease-only/law-only queries

2. **Caching Strategy**
   ```python
   # Implement query result caching
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def cached_analysis(query_hash, lease_id):
       # Return cached result if available
       pass
   ```

3. **Batch Processing**
   - Process multiple questions from same lease in single session
   - Reuse loaded vector stores

4. **Model Selection**
   - Use GPT-4o-mini for classification and grading (cheaper)
   - Reserve GPT-4o for synthesis only

5. **Configuration Tuning**
   ```yaml
   rag:
     max_requery_iterations: 2  # Reduce from 3 to 2
     retrieval_k: 3             # Reduce from 5 to 3 if acceptable
   ```

### Cost Monitoring

**Set Up OpenAI Usage Limits:**
1. Visit https://platform.openai.com/account/billing/limits
2. Set monthly budget cap
3. Configure email alerts at 50%, 75%, 90%

**Track Costs with LangSmith:**
- Enable LangSmith tracing
- Monitor cost per query in dashboard
- Identify expensive queries for optimization

## Production Considerations

### Security

**Environment Variables:**
```bash
# Never commit to version control
# Use secret management systems

# Streamlit Cloud: Use Secrets management
# Docker: Use docker secrets or .env files with restricted permissions
chmod 600 .env
```

**File Upload Validation:**
```python
# In app.py, add validation
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf'}

if uploaded_file.size > MAX_FILE_SIZE:
    st.error("File too large. Maximum size: 10MB")
```

**Rate Limiting:**
```python
# Add to app.py for public deployment
import streamlit as st
from datetime import datetime, timedelta

def check_rate_limit(user_id):
    # Implement per-user rate limiting
    # Store in session_state or external DB
    pass
```

### Monitoring

**Application Health:**
```bash
# Docker health check endpoint
curl http://localhost:8501/_stcore/health

# Expected response: 200 OK
```

**LangSmith Integration:**
```python
# .env configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key
LANGCHAIN_PROJECT=LeaseLogic-Production
```

**Key Metrics to Track:**
- Average query response time
- Query classification distribution
- Retrieval quality grades
- API costs per query
- Error rates
- User session duration

### Logging

**Configure Structured Logging:**
```python
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('leaselogic.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(json.dumps({
    'event': 'query_processed',
    'query_scope': scope,
    'quality': grade,
    'duration_ms': duration
}))
```

### Error Handling

**Graceful Degradation:**
```python
try:
    result = run_analysis(...)
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    st.error(
        "We encountered an error processing your request. "
        "Please try again or contact support."
    )
    # Don't expose internal errors to users
```

### Scaling

**Current Architecture Limits:**
- ChromaDB: Good for <1M vectors
- Streamlit: Single-threaded, best for <100 concurrent users
- Stateful: Session data stored in memory

**Scaling Options:**

1. **Horizontal Scaling (Multiple Instances)**
   ```bash
   # Use load balancer
   # Share vector stores via network filesystem
   # Implement session affinity
   ```

2. **Database Migration**
   ```python
   # Replace ChromaDB with Pinecone/Weaviate for scale
   # Benefits:
   # - Multi-region support
   # - Higher throughput
   # - Built-in scaling
   ```

3. **Async Processing**
   ```python
   # For high-latency queries
   # Implement job queue (Celery + Redis)
   # Return job ID, poll for results
   ```

### Backup and Recovery

**Vector Store Backup:**
```bash
# Backup ChromaDB data
tar -czf vectorstore_backup_$(date +%Y%m%d).tar.gz data/vector_stores/

# Automate with cron
0 2 * * * /path/to/backup_script.sh
```

**Configuration Backup:**
```bash
# Version control all config
git add config/config.yaml
git commit -m "Update configuration"
git push
```

## Monitoring and Observability

### LangSmith Setup

1. **Enable Tracing**
   ```bash
   # .env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_PROJECT=LeaseLogic-Prod
   ```

2. **View Traces**
   - Visit https://smith.langchain.com
   - Navigate to your project
   - Monitor query traces in real-time

3. **Set Up Alerts**
   - Configure error rate alerts
   - Set latency thresholds
   - Monitor cost anomalies

### Application Monitoring

**Recommended Tools:**

- **Sentry** - Error tracking
  ```python
  import sentry_sdk
  sentry_sdk.init(dsn="your-dsn")
  ```

- **Prometheus + Grafana** - Metrics and dashboards
  ```python
  from prometheus_client import Counter, Histogram

  query_counter = Counter('queries_total', 'Total queries processed')
  query_duration = Histogram('query_duration_seconds', 'Query duration')
  ```

### Performance Benchmarks

**Baseline Metrics:**
```bash
# Run performance tests
python tests/test_performance.py

# Expected results:
# - Average query time: 15-25s
# - P95 latency: <30s
# - Quality grade: 7-9/10
```

## Troubleshooting

### Common Issues

**1. ChromaDB Not Found**
```bash
# Ensure vector stores are initialized
python src/tools/law_vectorstore.py
```

**2. Memory Errors**
```bash
# Increase Docker memory limit
docker run -m 2g ...

# Or in Streamlit Cloud: Upgrade plan
```

**3. Slow Queries**
```yaml
# Reduce retrieval_k in config.yaml
rag:
  retrieval_k: 3  # Down from 5
```

**4. API Rate Limits**
```python
# Implement exponential backoff
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(min=1, max=60))
def call_openai_api():
    ...
```

## Rollback Procedure

**Streamlit Cloud:**
1. Navigate to app settings
2. Select "Reboot app"
3. Or redeploy previous commit from GitHub

**Docker:**
```bash
# Tag previous working version
docker tag leaselogic:latest leaselogic:backup

# Roll back
docker stop leaselogic
docker rm leaselogic
docker run -d --name leaselogic leaselogic:backup
```

## Support

For deployment issues:
- Check application logs
- Review LangSmith traces
- Consult [GitHub Issues](https://github.com/yourusername/leaselogic/issues)
- Email: support@yourdomain.com
