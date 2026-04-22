# Deployment Guide

This guide covers deploying the Country Information AI Agent to various hosting platforms.

## 🚀 Deployment Options

### Option 1: Render (Recommended for Quick Deployment)

**Steps:**

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Render will detect `render.yaml` automatically
6. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key
7. Click "Create Web Service"

**Configuration (render.yaml is included):**
- Free tier available
- Auto-deploys on git push
- Health checks configured
- HTTPS included

**Access your app:**
```
https://your-app-name.onrender.com
```

---

### Option 2: Railway

**Steps:**

1. Push your code to GitHub
2. Go to [Railway](https://railway.app/)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will detect configuration automatically
6. Add environment variables:
   - `OPENAI_API_KEY`: Your API key
   - `MODEL_NAME`: gpt-4o-mini (optional)
7. Deploy!

**Features:**
- $5 free credit monthly
- Automatic HTTPS
- Easy rollbacks
- Good logging

**Access your app:**
```
https://your-app.railway.app
```

---

### Option 3: Heroku

**Steps:**

1. Install Heroku CLI: `brew install heroku` (Mac) or download from heroku.com
2. Login: `heroku login`
3. Create app:
   ```bash
   heroku create your-app-name
   ```
4. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your-key-here
   heroku config:set MODEL_NAME=gpt-4o-mini
   ```
5. Deploy:
   ```bash
   git push heroku main
   ```

**Access your app:**
```
https://your-app-name.herokuapp.com
```

---

### Option 4: AWS (EC2 + Application Load Balancer)

**For production deployment:**

1. **Launch EC2 instance** (t3.small or larger)
2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   git clone your-repo
   cd Country-Information-AI-Agent
   pip3 install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY=your-key
   export MODEL_NAME=gpt-4o-mini
   export PORT=8000
   ```

4. **Run with systemd** (production):
   Create `/etc/systemd/system/country-agent.service`:
   ```ini
   [Unit]
   Description=Country Information AI Agent
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/Country-Information-AI-Agent
   Environment="OPENAI_API_KEY=your-key"
   Environment="MODEL_NAME=gpt-4o-mini"
   ExecStart=/usr/bin/python3 app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable country-agent
   sudo systemctl start country-agent
   ```

5. **Configure ALB** for load balancing and HTTPS

---

### Option 5: Docker + Cloud Run (GCP)

**Dockerfile** (create this):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

**Deploy to Cloud Run:**
```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/country-agent

# Deploy
gcloud run deploy country-agent \
  --image gcr.io/PROJECT_ID/country-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key
```

---

## 🔐 Environment Variables Setup

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_NAME` | LLM model | `gpt-4o-mini` |
| `PORT` | Server port | `8000` |
| `HOST` | Server host | `0.0.0.0` |

---

## 📊 Monitoring and Logging

### Health Check Endpoint

```bash
curl https://your-app.com/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Country Information AI Agent",
  "version": "1.0.0"
}
```

### Logs

**Render/Railway:** View in dashboard
**Heroku:** `heroku logs --tail`
**AWS:** CloudWatch Logs
**Docker:** `docker logs container-id`

---

## 🔧 Production Recommendations

### Add Rate Limiting

Install slowapi:
```bash
pip install slowapi
```

Add to `app.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/ask")
@limiter.limit("10/minute")
async def ask_question(request: Request, question: QuestionRequest):
    # ... existing code
```

### Add Caching

Install redis:
```bash
pip install redis
```

Cache country data:
```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_country(country_name):
    cached = cache.get(f"country:{country_name}")
    if cached:
        return json.loads(cached)
    return None

def cache_country(country_name, data):
    cache.setex(f"country:{country_name}", 3600, json.dumps(data))
```

### Add Authentication

Simple API key auth:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/ask")
async def ask_question(
    request: QuestionRequest,
    api_key: str = Depends(get_api_key)
):
    # ... existing code
```

---

## 🧪 Testing Deployment

### Test Health Endpoint
```bash
curl https://your-app.com/health
```

### Test API
```bash
curl -X POST https://your-app.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the population of Germany?"}'
```

### Load Testing
```bash
# Install hey
go install github.com/rakyll/hey@latest

# Run load test
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the population of Germany?"}' \
  https://your-app.com/ask
```

---

## 🐛 Troubleshooting

### "Failed to initialize agent"
- Check API key is set correctly
- Verify API key has sufficient credits
- Check network connectivity

### "Timeout" errors
- Increase timeout in deployment config
- Consider upgrading hosting plan
- Check REST Countries API status

### High response times
- Use `gpt-4o-mini` instead of `gpt-4`
- Add caching for common queries
- Consider using Claude 3.5 Haiku (faster)

---

## 📈 Scaling Recommendations

**Stage 1: Single Instance (0-1000 users)**
- Deploy on Render/Railway free tier
- No caching needed
- Monitor logs

**Stage 2: Multiple Instances (1K-10K users)**
- Add Redis caching
- Deploy 2-3 instances with load balancer
- Add rate limiting
- Monitor with Datadog/New Relic

**Stage 3: Production Scale (10K+ users)**
- Kubernetes deployment
- Redis cluster for caching
- API Gateway with auth
- Auto-scaling based on CPU/memory
- CDN for static assets
- Database for analytics

---

## 💰 Cost Estimates

### Hosting
- **Render Free Tier**: $0/month (750 hours)
- **Railway**: $5/month credit (then ~$10-20)
- **Heroku**: $7/month (Eco dyno)
- **AWS**: $15-50/month (t3.small + ALB)

### API Costs (per 1000 questions)
- **GPT-4o-mini**: ~$0.15 (input) + ~$0.60 (output) = ~$0.75
- **GPT-4o**: ~$2.50 (input) + ~$10 (output) = ~$12.50
- **Claude 3.5 Sonnet**: ~$3 (input) + ~$15 (output) = ~$18

**Recommendation**: Use gpt-4o-mini for production (10x cheaper than GPT-4)

---

## 🎯 Quick Deploy Commands

### Deploy to Render (via CLI)
```bash
# Install Render CLI
npm install -g render-cli

# Deploy
render deploy
```

### Deploy to Railway (via CLI)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy to Heroku
```bash
heroku create
heroku config:set OPENAI_API_KEY=your-key
git push heroku main
heroku open
```

---

Need help? Open an issue or contact support!
