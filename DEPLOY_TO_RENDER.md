# 🚀 Deploy GlucoLens to Render.com - One-Click Deployment

**Deploy in 3 minutes with Render's free tier!**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/brettleehari/metabolic-story-teller)

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [What Gets Deployed](#what-gets-deployed)
3. [Post-Deployment Setup](#post-deployment-setup)
4. [Environment Variables](#environment-variables)
5. [Database Initialization](#database-initialization)
6. [Monitoring & Logs](#monitoring--logs)
7. [Upgrading Plans](#upgrading-plans)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### Option 1: One-Click Deploy (Recommended)

1. Click the "Deploy to Render" button above
2. Sign in or create a Render account (free)
3. Render reads `render.yaml` and creates all services automatically:
   - ✅ FastAPI backend (web service)
   - ✅ React frontend (static site)
   - ✅ PostgreSQL database
   - ✅ Redis cache
   - ✅ Celery worker (background tasks)
   - ✅ Celery beat (scheduled tasks)
4. Wait 5-10 minutes for deployment
5. Access your app at the provided `.onrender.com` URL

### Option 2: Manual Deploy from Dashboard

1. Fork this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your forked repository
5. Render detects `render.yaml` and creates services

---

## 🏗️ What Gets Deployed

### Services Created

| Service | Type | Plan | Purpose |
|---------|------|------|---------|
| **glucolens-api** | Web | Free | FastAPI backend (Python 3.11) |
| **glucolens-frontend** | Static | Free | React frontend (Vite build) |
| **glucolens-celery-worker** | Worker | Free | Background ML tasks |
| **glucolens-celery-beat** | Worker | Free | Scheduled tasks (daily aggregations) |
| **glucolens-db** | PostgreSQL | Free | Time-series data storage |
| **glucolens-redis** | Redis | Free | Cache & task queue |

### Free Tier Limits

- **Web Services**: 750 hours/month (free)
- **PostgreSQL**: 1GB storage, 97 connection limit
- **Redis**: 25MB storage
- **Bandwidth**: 100GB/month
- **Build Minutes**: 500 minutes/month
- **Services spin down after 15 minutes of inactivity** (spins up in <30s on next request)

**Total Cost**: **$0/month** for evaluation and development

---

## ⚙️ Post-Deployment Setup

### 1. Update CORS Origins (Required)

The backend needs to know which frontend domains to allow:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click on **glucolens-api** service
3. Go to "Environment" tab
4. Find `CORS_ORIGINS` variable
5. Click "Edit" and set to your frontend URL:
   ```
   https://glucolens-frontend.onrender.com
   ```
6. Save changes (service will redeploy)

### 2. Initialize Database Schema

On first deployment, create database tables:

```bash
# Option 1: Via Render Shell
# Go to glucolens-api → Shell tab
python -c "
from app.models.base import Base, engine
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())
print('✅ Database initialized')
"

# Option 2: Via Local Connection
# Copy DATABASE_URL from glucolens-api environment variables
psql $DATABASE_URL -c "
-- Database will be initialized on first API startup
-- Or uncomment create_all in app/main.py line 74
"
```

### 3. Generate Sample Data (Optional)

```bash
# Via Render Shell on glucolens-api
python scripts/generate_sample_data.py --days 90

# This creates:
# - Demo user account
# - 90 days of glucose readings
# - Sleep, meal, activity data
# - Correlations and patterns
```

### 4. Access Your Application

- **Frontend**: `https://glucolens-frontend.onrender.com`
- **Backend API**: `https://glucolens-api.onrender.com`
- **API Docs**: `https://glucolens-api.onrender.com/docs`
- **Health Check**: `https://glucolens-api.onrender.com/health`

**Default Credentials** (if using sample data):
- Email: `demo@glucolens.com`
- Password: `Demo123!`

---

## 🔐 Environment Variables

### Required (Auto-configured)

These are set automatically by `render.yaml`:

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | glucolens-db | PostgreSQL connection string |
| `REDIS_URL` | glucolens-redis | Redis connection string |
| `SECRET_KEY` | Auto-generated | JWT signing key (64 hex chars) |
| `CELERY_BROKER_URL` | glucolens-redis | Celery task queue |
| `CELERY_RESULT_BACKEND` | glucolens-redis | Celery results storage |

### Optional (Set Manually)

Add these via Dashboard → Service → Environment:

| Variable | Example | Required? |
|----------|---------|-----------|
| `CORS_ORIGINS` | `https://glucolens-frontend.onrender.com` | **Yes** |
| `SENTRY_DSN` | `https://xxx@sentry.io/123` | No (monitoring) |
| `LOG_LEVEL` | `INFO` | No (default: INFO) |
| `MAX_WORKERS` | `4` | No (Celery concurrency) |

### ML Configuration (Pre-set)

Already configured in `render.yaml`:

```yaml
MIN_DATA_POINTS_PCMCI: 50
PCMCI_ALPHA_LEVEL: 0.05
PCMCI_MAX_LAG: 7
STUMPY_WINDOW_SIZE: 288
ML_CACHE_TTL: 3600
```

---

## 🗄️ Database Initialization

### Automatic Initialization

The application uses database connection retry logic:
- Waits up to 30 seconds for database to be ready
- Creates connection pool on startup
- Health check validates database connectivity

### Manual Schema Creation

If tables aren't created automatically:

```bash
# Via Render Shell (glucolens-api service)
cd /app
python << EOF
import asyncio
from app.models.base import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully")

asyncio.run(create_tables())
EOF
```

### Running Migrations (Future)

When Alembic migrations are added:

```bash
# Via Render Shell
alembic upgrade head
```

---

## 📊 Monitoring & Logs

### View Logs

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click on service (e.g., **glucolens-api**)
3. Click "Logs" tab
4. Real-time logs appear here

### Health Checks

Each service has health monitoring:

**API Health**:
```bash
curl https://glucolens-api.onrender.com/health
# Returns:
# {
#   "service": "glucolens-backend",
#   "status": "healthy",
#   "database": "connected",
#   "version": "2.0.0"
# }
```

### Metrics

Free tier includes:
- CPU usage graphs
- Memory usage graphs
- Request count
- Response times
- 90-day log retention

---

## 💰 Upgrading Plans

### When to Upgrade

Consider upgrading from free to paid when:
- ❌ Service sleeps after 15 min inactivity (annoying for users)
- ❌ Need more than 1GB database storage
- ❌ Need faster than 512MB RAM instances
- ❌ Need custom domains with SSL
- ❌ Need team collaboration

### Recommended Upgrades

| Scenario | Plan | Cost/Month |
|----------|------|------------|
| **MVP/Demo** | Free tier | $0 |
| **Beta/Testing** | Starter web + Starter DB | $14 ($7 + $7) |
| **Production** | Standard web + Standard DB + Pro Redis | $67 ($25 + $25 + $17) |
| **Scale** | Pro web + Pro DB + multiple workers | $200+ |

### Upgrade Steps

1. Go to service in Dashboard
2. Click "Settings" → "Plan"
3. Select new plan
4. Confirm payment method
5. Service upgrades without downtime

---

## 🐛 Troubleshooting

### Service Won't Start

**Symptom**: Service shows "Deploy failed" or keeps restarting

**Solutions**:
1. Check logs for errors
2. Verify `Dockerfile` builds locally:
   ```bash
   docker build -t glucolens-test ./backend
   docker run -p 8000:8000 glucolens-test
   ```
3. Ensure all required env vars are set
4. Check database connectivity in logs

### Database Connection Errors

**Symptom**: "OperationalError: could not connect to server"

**Solutions**:
1. Verify `DATABASE_URL` is set correctly
2. Check database service is running
3. Wait 30 seconds (retry logic handles delays)
4. Check database IP allowlist (should be empty for Render services)

### Frontend Can't Reach Backend

**Symptom**: API calls fail with CORS errors

**Solutions**:
1. Verify `CORS_ORIGINS` includes frontend URL
2. Check `VITE_API_BASE_URL` points to backend
3. Ensure both services are deployed and running
4. Check network tab in browser DevTools

### Celery Tasks Not Running

**Symptom**: Background tasks don't execute

**Solutions**:
1. Check **glucolens-celery-worker** service is running
2. Verify `CELERY_BROKER_URL` matches Redis URL
3. Check logs for task errors
4. Ensure Redis service is healthy

### Service Sleeps (Free Tier)

**Symptom**: First request after inactivity is slow (~30s)

**Solutions**:
1. **Accept it** (this is normal for free tier)
2. **Upgrade to Starter plan** ($7/month) - never sleeps
3. **Use UptimeRobot** to ping every 14 minutes (keeps service awake)
4. **Add loading indicator** in frontend for cold starts

### Out of Memory

**Symptom**: Service crashes with OOM error

**Solutions**:
1. Reduce `--concurrency` for Celery workers (default: 2)
2. Upgrade to larger instance ($7/month = 1GB RAM)
3. Optimize ML model memory usage
4. Check for memory leaks in logs

---

## 📚 Additional Resources

### Render Documentation
- [Render Blueprints](https://render.com/docs/blueprint-spec)
- [Environment Variables](https://render.com/docs/environment-variables)
- [PostgreSQL](https://render.com/docs/databases)
- [Redis](https://render.com/docs/redis)
- [Static Sites](https://render.com/docs/static-sites)

### GlucoLens Documentation
- [Architecture Diagrams](./ARCHITECTURE_DIAGRAMS.md)
- [Development Workflow](./DEVELOPMENT_WORKFLOW.md)
- [ML Pipeline Guide](./ML_PIPELINE_EXECUTION_GUIDE.md)
- [Deployment Validation Report](./DEPLOYMENT_VALIDATION_REPORT.md)

### Support
- **Render Support**: [https://render.com/docs/support](https://render.com/docs/support)
- **GlucoLens Issues**: [GitHub Issues](https://github.com/brettleehari/metabolic-story-teller/issues)

---

## ✅ Deployment Checklist

After clicking "Deploy to Render":

- [ ] Wait for all services to deploy (5-10 minutes)
- [ ] Set `CORS_ORIGINS` environment variable
- [ ] Verify backend health check returns 200
- [ ] Initialize database schema (if not automatic)
- [ ] (Optional) Generate sample data
- [ ] Test frontend → backend connectivity
- [ ] Test user registration and login
- [ ] Verify Celery tasks are processing
- [ ] Check logs for any warnings
- [ ] Bookmark your app URLs

---

## 🎉 Success!

Your GlucoLens instance is now running on Render!

**Next Steps**:
1. Create your first user account
2. Start logging glucose readings
3. Explore ML-powered insights
4. Customize configuration for your needs
5. Consider upgrading to paid tier for production use

**Questions?** Open an issue on GitHub or check Render's documentation.

---

**Deployment Date**: Auto-updated on deploy
**Last Updated**: 2025-12-19
**Render Blueprint Version**: 1.0.0
