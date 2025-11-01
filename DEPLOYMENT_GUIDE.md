# Project Samarth - Event-Driven Architecture - Deployment Guide

## 🚀 Quick Deployment Overview

This guide covers deploying the Event-Driven Architecture backend API to production platforms.

**What you'll deploy:**
- FastAPI async backend with event-driven pipeline
- Port: 8002 (configurable)
- Python 3.12 runtime with asyncio
- Pub/Sub event bus architecture

---

## Option 1: Deploy to Render.com (Recommended - Free Tier)

### Step 1: Prepare Your Code

1. **Push to GitHub:**
```bash
cd /Users/paritoshdwivedi/Downloads/Projects/project-samarth-events
git init
git add .
git commit -m "Initial commit: Event-Driven Architecture"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/project-samarth-events.git
git push -u origin main
```

2. **Create `runtime.txt` in backend folder:**
```bash
echo "python-3.12.0" > backend/runtime.txt
```

### Step 2: Deploy on Render

1. Go to https://render.com and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `project-samarth-events`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Environment Variables:**
   - Click "Advanced" → "Add Environment Variable"
   - Key: `DATAGOV_API_KEY`
   - Value: `579b464db66ec23bdd000001610dbcacf605486f7925fe91c9f5d0ee`

6. Click **"Create Web Service"**

7. Wait 3-5 minutes for deployment

8. **Your API will be live at:** `https://project-samarth-events.onrender.com`

### Step 3: Test Deployment

```bash
# Health check
curl https://project-samarth-events.onrender.com/health

# Test query (watch event flow in logs!)
curl -X POST https://project-samarth-events.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Compare rainfall in Kerala and Punjab over 3 years"}'
```

---

## Option 2: Deploy to Railway.app (Free Tier)

### Step 1: Setup Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"Start a New Project"** → **"Deploy from GitHub repo"**
4. Select `project-samarth-events`

### Step 2: Configure

1. Railway auto-detects Python
2. **Add Environment Variables:**
   - Go to Variables tab
   - Add: `DATAGOV_API_KEY=579b464db66ec23bdd000001610dbcacf605486f7925fe91c9f5d0ee`

3. **Set Root Directory:**
   - Settings → Root Directory → `backend`

4. **Custom Start Command (if needed):**
   - Settings → Start Command
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Deploy

1. Click **"Deploy"**
2. Railway will build and deploy automatically
3. **Get your URL:** Settings → Domains → Generate Domain
4. Your API: `https://project-samarth-events.up.railway.app`

---

## Option 3: Deploy to Vercel (Serverless)

**⚠️ Note:** Event-driven architecture works best on persistent servers (Render/Railway) rather than serverless, but Vercel is possible:

### Step 1: Create `vercel.json`

```bash
cd backend
cat > vercel.json << 'VERCEL'
{
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
VERCEL
```

### Step 2: Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd backend
vercel --prod

# Add environment variable
vercel env add DATAGOV_API_KEY
# Enter: 579b464db66ec23bdd000001610dbcacf605486f7925fe91c9f5d0ee
```

---

## Option 4: Local with ngrok (Quick Demo)

Perfect for Loom video with full event logs visible:

```bash
# Terminal 1: Run backend
cd backend
source .venv/bin/activate
export DATAGOV_API_KEY=579b464db66ec23bdd000001610dbcacf605486f7925fe91c9f5d0ee
uvicorn app.main:app --host 0.0.0.0 --port 8002

# Terminal 2: Expose with ngrok
brew install ngrok  # or download from ngrok.com
ngrok http 8002
```

**Copy the HTTPS URL** (e.g., `https://xyz789.ngrok-free.app`)

**Advantage:** See full event flow in Terminal 1 logs!

---

## Testing Your Deployment

### Health Check
```bash
curl https://YOUR_DEPLOYED_URL/health
# Expected: {"status":"ok"}
```

### Test Event Pipeline

**1. Compare Rainfall & Crops:**
```bash
curl -X POST https://YOUR_DEPLOYED_URL/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Compare rainfall in Kerala and Punjab over 3 years"
  }'
```

**2. District Extremes:**
```bash
curl -X POST https://YOUR_DEPLOYED_URL/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which district in Punjab had the highest wheat production in 2020?"
  }'
```

**3. Production Trend:**
```bash
curl -X POST https://YOUR_DEPLOYED_URL/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show rice production trend in Tamil Nadu over 5 years"
  }'
```

**4. Policy Arguments:**
```bash
curl -X POST https://YOUR_DEPLOYED_URL/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Why should Karnataka shift from cotton to sugarcane?"
  }'
```

---

## Monitoring Event Flow in Logs

### On Render:
1. Go to your service dashboard
2. Click "Logs" tab
3. Run a query
4. **Watch event flow:**
   ```
   Publishing event: query.received
   ParseStage processing event
   Publishing event: query.parsed
   DataLoadStage processing event
   Publishing event: data.loaded
   AnalysisStage processing event
   Publishing event: analysis.complete
   FormatStage processing event
   Publishing event: response.ready
   Query completed successfully
   ```

### On Railway:
1. Click on your service
2. Go to "Deployments" → "View Logs"
3. Live event stream visible

**This is the magic of event-driven architecture - full observability!**

---

## Troubleshooting

### Build Fails

**Error: `pandas` compilation fails**
- **Cause:** Using Python 3.14 (incompatible)
- **Fix:** Ensure `runtime.txt` has `python-3.12.0`

**Error: Module not found**
- **Cause:** Requirements not installed
- **Fix:** Verify `requirements.txt` in backend folder

### Runtime Errors

**Error: API key not set**
- **Fix:** Add `DATAGOV_API_KEY` environment variable in platform settings

**Error: Timeout on first request**
- **Normal:** Data loading can take 5-10s first time
- **Fix:** Increase timeout if needed (default is 30s)

**Error: Event not published**
- **Fix:** Check logs for pipeline stage errors

### Async Issues

**Error: Event loop errors**
- **Cause:** Platform doesn't support asyncio properly
- **Fix:** Use Render/Railway (both support async FastAPI)

---

## Architecture Highlights for Demo

When showing your deployed API, highlight:

### 1. Event Bus Flow
```
Request → query.received → parsed → loaded → complete → ready → Response
```

**Show in logs:** Each event publishing and being received by next stage

### 2. Pipeline Stages
- **ParseStage:** Converts question to intent
- **DataLoadStage:** Fetches datasets
- **AnalysisStage:** Performs calculations
- **FormatStage:** Creates response

### 3. Event-Driven Benefits
✅ **Decoupled:** Stages communicate only via events
✅ **Observable:** Every event logged
✅ **Async:** Non-blocking execution
✅ **Scalable:** Easy to distribute stages

---

## Platform Comparison

| Platform | Free Tier | Async Support | Event Logs | Best For |
|----------|-----------|---------------|------------|----------|
| **Render** | Yes (750hrs/mo) | Excellent | Excellent | Production |
| **Railway** | Yes ($5 credit) | Excellent | Good | Production |
| **Vercel** | Yes | Limited | Limited | Quick demo |
| **ngrok** | Yes (temp URL) | Full (local) | Full (local) | **Loom demo** |

**Recommendation:** 
- **Render** for permanent deployment
- **ngrok + local** for Loom demo (to show event logs)

---

## Scaling to Distributed System

### Current (Single Process):
```
FastAPI → In-Memory Event Bus → 4 Stages
```

### Future (Microservices):
```
API Service → Redis Pub/Sub → ParseStage Service
                            → DataStage Service
                            → AnalysisStage Service
                            → FormatStage Service
```

**Migration Steps:**
1. Replace `EventBus` with Redis client
2. Deploy each stage as separate service
3. Configure Redis Pub/Sub topics
4. Same code, distributed execution!

**Mention in Loom:** "This architecture is cloud-native ready. The same code can run distributed across Kubernetes pods."

---

## Loom Video Checklist

**Before Recording:**
- [ ] API deployed OR local server + ngrok running
- [ ] Health check passing
- [ ] Test all 4 query types successfully
- [ ] Logs panel open and visible
- [ ] Copy deployment URL

**During Demo:**
- [ ] Show deployed URL
- [ ] Run a query via curl/Postman
- [ ] **Point to logs showing 5 events flowing**
- [ ] Explain each stage (Parse → Data → Analysis → Format)
- [ ] Run another query, show same event flow
- [ ] Highlight async execution (mention concurrent queries possible)

**Script:**
"This is deployed on [Render/Railway] at [URL]. Watch the logs carefully - you'll see the event-driven architecture in action. First, the query.received event is published. ParseStage picks it up, processes the question, and publishes query.parsed. Then DataLoadStage fetches datasets and publishes data.loaded. This continues through the pipeline - 5 events total. Each stage is completely decoupled. In production, these could be separate microservices communicating via Redis or Kafka."

---

## Advanced: Redis Event Bus (Optional)

To scale beyond single server:

### 1. Add Redis dependency:
```bash
pip install redis
```

### 2. Replace EventBus:
```python
# app/event_bus_redis.py
import redis
import json

class RedisEventBus:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)

    def publish(self, topic, data, metadata=None):
        event = {"data": data, "metadata": metadata}
        self.redis.publish(topic, json.dumps(event))

    def subscribe(self, topic, handler):
        pubsub = self.redis.pubsub()
        pubsub.subscribe(topic)
        for message in pubsub.listen():
            if message['type'] == 'message':
                event = json.loads(message['data'])
                handler(event)
```

### 3. Deploy stages separately:
```bash
# Stage 1 service
python -m app.pipeline.parse_stage

# Stage 2 service
python -m app.pipeline.data_load_stage

# etc.
```

**Mention in Loom:** "The architecture supports horizontal scaling. Replace the in-memory bus with Redis, deploy stages as containers, and you have a distributed event-driven system."

---

## Production Checklist

✅ **Deployed:** API accessible via HTTPS
✅ **Environment Variables:** API key configured
✅ **Health Check:** `/health` endpoint responding
✅ **Event Pipeline:** All 4 stages executing
✅ **Logs Visible:** Event flow observable
✅ **Async Working:** Non-blocking execution
✅ **Timeout Handling:** 30s timeout configured
✅ **Error Handling:** pipeline.error event handling

**You're production-ready with enterprise-grade event-driven architecture!** 🚀

---

## Quick Reference

### Environment Variables
```bash
DATAGOV_API_KEY=579b464db66ec23bdd000001610dbcacf605486f7925fe91c9f5d0ee
```

### Event Topics
- `query.received` → ParseStage
- `query.parsed` → DataLoadStage  
- `data.loaded` → AnalysisStage
- `analysis.complete` → FormatStage
- `response.ready` → QueryExecutor
- `pipeline.error` → Error handler

### Key URLs
- **Health:** `/health`
- **Query:** `POST /ask`
- **Refresh:** `POST /refresh`
