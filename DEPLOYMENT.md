# GlucoLens Deployment Guide

Complete guide for deploying GlucoLens to production.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Option 1: Docker Compose (Recommended for MVP)](#option-1-docker-compose-single-server)
3. [Deployment Option 2: Kubernetes](#option-2-kubernetes)
4. [Deployment Option 3: Serverless](#option-3-serverless)
5. [Post-Deployment Tasks](#post-deployment-tasks)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Backup & Disaster Recovery](#backup--disaster-recovery)
8. [Scaling Considerations](#scaling-considerations)

---

## Pre-Deployment Checklist

### Critical Fixes Required (2-3 weeks)

#### 1. Fix Authentication Inconsistencies (1 day)
**Issue:** Sleep, meals, activities routes use `MOCK_USER_ID` instead of JWT auth

**Files to Fix:**
- `backend/app/routes/sleep.py`
- `backend/app/routes/meals.py`
- `backend/app/routes/activities.py`
- `backend/app/routes/insights.py`

**Changes:**
```python
# Replace MOCK_USER_ID with:
@router.post("/")
async def create_item(
    item: ItemCreate,
    current_user: User = Depends(get_current_user),  # Add this
    db: AsyncSession = Depends(get_db)
):
    new_item = Item(
        user_id=current_user.id,  # Use authenticated user
        **item.model_dump()
    )
    # ...
```

#### 2. Add Missing GET Endpoints (1 day)
**Files to Update:**
- `backend/app/routes/sleep.py` - Add `GET /sleep`
- `backend/app/routes/meals.py` - Add `GET /meals`
- `backend/app/routes/activities.py` - Add `GET /activities`

**Example:**
```python
@router.get("/", response_model=list[SleepDataResponse])
async def get_sleep_data(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(SleepData).where(SleepData.user_id == current_user.id)
    if start_date:
        query = query.where(SleepData.date >= start_date)
    if end_date:
        query = query.where(SleepData.date <= end_date)
    result = await db.execute(query)
    return result.scalars().all()
```

#### 3. Setup Alembic Migrations (2 days)

**Install Alembic:**
```bash
# Add to backend/requirements.txt
alembic==1.13.1
```

**Initialize:**
```bash
cd backend
docker-compose exec api alembic init alembic
```

**Configure `alembic.ini`:**
```ini
# Use async driver
sqlalchemy.url = postgresql+asyncpg://glucolens:${DB_PASSWORD}@timescaledb:5432/glucolens
```

**Configure `alembic/env.py`:**
```python
from app.models.base import Base
from app.config import settings

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

**Create Initial Migration:**
```bash
docker-compose exec api alembic revision --autogenerate -m "Initial schema"
docker-compose exec api alembic upgrade head
```

#### 4. Add Basic Tests (3-5 days)

**Create Test Structure:**
```bash
backend/tests/
├── conftest.py           # Fixtures
├── test_auth.py          # Authentication tests
├── test_glucose.py       # Glucose endpoints
├── test_insights.py      # Insights endpoints
└── test_ml.py            # ML pipeline tests
```

**Example Test (`backend/tests/test_auth.py`):**
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login():
    # Setup: Register user first
    # Test: Login with credentials
    # Assert: Token returned
    pass
```

**Run Tests:**
```bash
docker-compose exec api pytest -v
```

#### 5. Add Error Monitoring (1 day)

**Install Sentry:**
```bash
# Add to backend/requirements.txt
sentry-sdk[fastapi]==1.40.0
```

**Configure in `backend/app/main.py`:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from app.config import settings

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT
    )
```

**Add to `.env`:**
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production
```

#### 6. Add Rate Limiting (1 day)

**Install Slowapi:**
```bash
# Add to backend/requirements.txt
slowapi==0.1.9
```

**Configure:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, ...):
    pass
```

---

## Option 1: Docker Compose (Single Server)

**Recommended for:** MVP, beta testing, up to 100 active users
**Cost:** $30-50/month
**Complexity:** Low

### 1. Server Provisioning

**Choose a Provider:**
- **DigitalOcean** - Simple, developer-friendly ($24/mo for 4GB droplet)
- **AWS EC2** - More features, steeper learning curve (t3.medium ~$30/mo)
- **Hetzner** - Best price/performance (~€15/mo for 4GB)

**Minimum Specs:**
- 4GB RAM (8GB recommended)
- 2 CPU cores
- 80GB SSD
- Ubuntu 22.04 LTS

### 2. Server Setup

**SSH into server:**
```bash
ssh root@your-server-ip
```

**Update system:**
```bash
apt update && apt upgrade -y
```

**Install Docker:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```

**Configure firewall:**
```bash
# Install UFW
apt install ufw

# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable
```

**Install fail2ban (brute-force protection):**
```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Deploy Application

**Clone repository:**
```bash
cd /opt
git clone https://github.com/your-username/metabolic-story-teller.git
cd metabolic-story-teller
```

**Create production environment file:**
```bash
cp backend/.env.example backend/.env
nano backend/.env
```

**Production `.env` configuration:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://glucolens:CHANGE_THIS_PASSWORD@timescaledb:5432/glucolens
DB_PASSWORD=CHANGE_THIS_PASSWORD

# Redis
REDIS_URL=redis://redis:6379/0

# Security - GENERATE NEW KEYS!
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Add your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
ENVIRONMENT=production

# Email (for future magic link auth)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
```

**Create production docker-compose:**
```bash
nano docker-compose.prod.yml
```

```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    restart: always
    environment:
      POSTGRES_DB: glucolens
      POSTGRES_USER: glucolens
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - timescale_data:/var/lib/postgresql/data
      - ./backend/migrations:/migrations
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U glucolens"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    env_file:
      - backend/.env
    depends_on:
      timescaledb:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/app:/app/app
    expose:
      - "8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    env_file:
      - backend/.env
    depends_on:
      - redis
      - timescaledb
    command: celery -A app.tasks worker --loglevel=info --concurrency=2

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    env_file:
      - backend/.env
    depends_on:
      - redis
      - timescaledb
    command: celery -A app.tasks beat --loglevel=info

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - api

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  timescale_data:
  redis_data:
```

**Create Nginx configuration:**
```bash
nano nginx.conf
```

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream api {
        server api:8000;
    }

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        # SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API docs
        location /docs {
            proxy_pass http://api;
        }
    }
}
```

**Build frontend for production:**
```bash
npm install
npm run build
# Creates dist/ folder with production build
```

**Get SSL certificate:**
```bash
# Initial certificate
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com \
  --email your@email.com --agree-tos --no-eff-email
```

**Start services:**
```bash
docker compose -f docker-compose.prod.yml up -d
```

**Initialize database:**
```bash
# Run migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Optional: Create admin user
docker compose -f docker-compose.prod.yml exec api python scripts/create_admin.py
```

### 4. Verify Deployment

**Check services:**
```bash
docker compose -f docker-compose.prod.yml ps
```

**Check logs:**
```bash
docker compose -f docker-compose.prod.yml logs -f api
```

**Test endpoints:**
```bash
# Health check
curl https://yourdomain.com/api/v1/health

# API docs
open https://yourdomain.com/docs
```

---

## Option 2: Kubernetes

**Recommended for:** 100+ users, high availability requirements
**Cost:** $150-300/month
**Complexity:** High

### Overview

```
Kubernetes Cluster (AWS EKS / GCP GKE / Azure AKS)
├── Ingress Controller (Nginx / Traefik)
├── Frontend (3 replicas + CDN)
├── Backend API (3 replicas, auto-scaling 3-10)
├── Celery Workers (3 replicas, auto-scaling 3-20)
├── Celery Beat (1 replica)
├── Managed TimescaleDB (RDS / Cloud SQL)
├── Managed Redis (ElastiCache / MemoryStore)
├── Monitoring (Prometheus + Grafana)
└── Logging (ELK Stack / Cloud Logging)
```

### Setup Steps (High-Level)

1. **Create Kubernetes Cluster**
   ```bash
   # AWS EKS
   eksctl create cluster --name glucolens --region us-east-1 --nodes 3

   # GCP GKE
   gcloud container clusters create glucolens --num-nodes=3
   ```

2. **Setup Managed Database**
   - AWS RDS with TimescaleDB extension
   - Configure VPC peering for cluster access
   - Enable automated backups

3. **Create Kubernetes Manifests**
   ```yaml
   # deployment-api.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: glucolens-api
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: glucolens-api
     template:
       metadata:
         labels:
           app: glucolens-api
       spec:
         containers:
         - name: api
           image: your-registry/glucolens-api:latest
           ports:
           - containerPort: 8000
           env:
           - name: DATABASE_URL
             valueFrom:
               secretKeyRef:
                 name: glucolens-secrets
                 key: database-url
           resources:
             requests:
               memory: "512Mi"
               cpu: "250m"
             limits:
               memory: "1Gi"
               cpu: "500m"
   ```

4. **Deploy with Helm**
   - Package app as Helm chart
   - Configure values for production
   - Deploy: `helm install glucolens ./glucolens-chart`

**Full K8s setup is complex and beyond this guide. Consider hiring DevOps expertise.**

---

## Option 3: Serverless

**Recommended for:** Cost optimization, variable traffic
**Cost:** $10-50/month (pay per use)
**Complexity:** Medium-High

### Architecture

```
AWS Serverless Stack
├── CloudFront (Frontend CDN)
├── S3 (Static frontend hosting)
├── API Gateway (REST API)
├── Lambda Functions (FastAPI via Mangum)
├── Aurora Serverless v2 (PostgreSQL + TimescaleDB)
├── ElastiCache Serverless (Redis)
├── EventBridge (Celery replacement)
├── SQS (Task queue)
└── CloudWatch (Monitoring + Logs)
```

### Setup with AWS SAM

**Convert FastAPI to Lambda:**
```python
# backend/app/lambda_handler.py
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

**SAM Template:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  GlucoLensAPI:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: backend/
      Handler: app.lambda_handler.handler
      Runtime: python3.11
      Timeout: 30
      MemorySize: 1024
      Environment:
        Variables:
          DATABASE_URL: !Ref DatabaseURL
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
```

**Deploy:**
```bash
sam build
sam deploy --guided
```

---

## Post-Deployment Tasks

### 1. Setup Automated Backups

**Database Backups (Daily):**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="glucolens_backup_$DATE.sql.gz"

docker compose -f docker-compose.prod.yml exec -T timescaledb \
  pg_dump -U glucolens glucolens | gzip > /backups/$BACKUP_FILE

# Upload to S3
aws s3 cp /backups/$BACKUP_FILE s3://your-bucket/backups/

# Keep only last 30 days
find /backups -type f -mtime +30 -delete
```

**Schedule with cron:**
```bash
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/metabolic-story-teller/backup.sh
```

### 2. Setup Monitoring

**Install Prometheus + Grafana (Docker Compose):**
```yaml
# Add to docker-compose.prod.yml

prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  volumes:
    - grafana_data:/var/lib/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=secure_password
```

**Configure alerts:**
- Disk usage > 80%
- API response time > 2s
- Database connections exhausted
- Celery queue length > 100

### 3. Setup Log Aggregation

**Option A: ELK Stack**
- Elasticsearch for storage
- Logstash for processing
- Kibana for visualization

**Option B: Loki + Grafana**
- Lightweight alternative
- Better for small deployments

**Option C: Cloud Solutions**
- AWS CloudWatch
- GCP Cloud Logging
- Datadog

### 4. Security Hardening

**SSL Configuration:**
- A+ rating on SSL Labs
- TLS 1.2+ only
- HSTS header
- OCSP stapling

**Application Security:**
```python
# Add security headers middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])

# Add CORS restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Database Security:**
- Restrict network access
- Use strong passwords
- Enable SSL connections
- Regular security updates

---

## Monitoring & Maintenance

### Key Metrics to Monitor

**Application Metrics:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active users

**Infrastructure Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network bandwidth

**Database Metrics:**
- Connection pool usage
- Query performance
- Table sizes
- Replication lag (if applicable)

**Celery Metrics:**
- Task queue length
- Task processing time
- Failed tasks
- Worker utilization

### Maintenance Tasks

**Daily:**
- Check error logs
- Monitor disk usage
- Review automated backups

**Weekly:**
- Security updates
- Performance review
- Backup restoration test

**Monthly:**
- Database optimization (VACUUM, ANALYZE)
- SSL certificate check
- Cost optimization review
- Security audit

---

## Backup & Disaster Recovery

### Backup Strategy

**What to Backup:**
1. Database (PostgreSQL)
2. Redis data (if persistent)
3. Environment files (.env)
4. SSL certificates
5. Application code (Git is primary, but keep snapshots)

**Backup Retention:**
- Daily backups: Keep 7 days
- Weekly backups: Keep 4 weeks
- Monthly backups: Keep 12 months

### Disaster Recovery Procedure

**Scenario 1: Database Corruption**
```bash
# 1. Stop application
docker compose -f docker-compose.prod.yml stop api celery_worker celery_beat

# 2. Restore from backup
gunzip < glucolens_backup_YYYYMMDD.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T timescaledb \
  psql -U glucolens -d glucolens

# 3. Verify data
docker compose -f docker-compose.prod.yml exec timescaledb \
  psql -U glucolens -d glucolens -c "SELECT COUNT(*) FROM users;"

# 4. Restart application
docker compose -f docker-compose.prod.yml start api celery_worker celery_beat
```

**Scenario 2: Complete Server Failure**
1. Provision new server
2. Install Docker
3. Clone repository
4. Restore .env files
5. Restore database from S3 backup
6. Start services
7. Update DNS if needed

**RTO (Recovery Time Objective):** 1-2 hours
**RPO (Recovery Point Objective):** 24 hours (daily backups)

---

## Scaling Considerations

### Vertical Scaling (Scale Up)
**When:** Single server at 70%+ CPU/memory

**Steps:**
1. Resize server (4GB → 8GB → 16GB)
2. Update docker-compose resource limits
3. Restart services

**Limits:** Single server caps at ~500-1000 concurrent users

### Horizontal Scaling (Scale Out)
**When:** Vertical scaling insufficient

**Architecture:**
```
Load Balancer
  ├── API Server 1 (+ Celery Worker)
  ├── API Server 2 (+ Celery Worker)
  └── API Server 3 (+ Celery Worker)
       │
       ├── Shared Database (Primary + Read Replicas)
       └── Shared Redis Cluster
```

**Steps:**
1. Setup load balancer (Nginx, HAProxy, or cloud LB)
2. Deploy identical servers
3. Configure shared database
4. Use Redis for session storage
5. Ensure Celery workers share Redis broker

### Database Scaling

**Read Replicas:**
- Route read-only queries to replicas
- Keep writes on primary

**Connection Pooling:**
- Use PgBouncer
- Limit connections per worker

**Sharding (Advanced):**
- Shard by user_id
- Requires application changes

---

## Cost Estimates

### Option 1: Docker Compose (Single Server)

**DigitalOcean Droplet (4GB):** $24/mo
**Managed Database (optional):** $15/mo
**Backups (S3):** $2/mo
**Domain + SSL:** $12/year ($1/mo)
**Monitoring (UptimeRobot free tier):** $0

**Total:** ~$42/month

### Option 2: Kubernetes (AWS EKS)

**EKS Cluster:** $73/mo
**3x t3.medium nodes:** $90/mo
**RDS db.t3.medium:** $70/mo
**ElastiCache:** $50/mo
**Load Balancer:** $20/mo
**Data transfer:** $30/mo

**Total:** ~$333/month

### Option 3: Serverless (AWS)

**Lambda (1M requests/mo):** $20
**API Gateway:** $3.50
**Aurora Serverless v2:** $60
**ElastiCache Serverless:** $30
**CloudFront:** $10
**S3:** $2

**Total:** ~$125/month (at 1M requests)

---

## Troubleshooting

### Common Issues

**Issue: Database connection refused**
```bash
# Check database health
docker compose -f docker-compose.prod.yml exec timescaledb pg_isready

# Check connection from API container
docker compose -f docker-compose.prod.yml exec api \
  python -c "from app.config import async_session_maker; import asyncio; asyncio.run(async_session_maker().__anext__())"
```

**Issue: Celery tasks not processing**
```bash
# Check worker status
docker compose -f docker-compose.prod.yml exec celery_worker \
  celery -A app.tasks inspect active

# Check Redis connection
docker compose -f docker-compose.prod.yml exec redis redis-cli ping

# Restart worker
docker compose -f docker-compose.prod.yml restart celery_worker
```

**Issue: High memory usage**
```bash
# Check container stats
docker stats

# Check for memory leaks in API
docker compose -f docker-compose.prod.yml exec api \
  python -c "import gc; gc.collect(); print('Collected')"

# Restart if needed
docker compose -f docker-compose.prod.yml restart api
```

---

## Next Steps

1. **Fix critical gaps** (2-3 weeks)
2. **Deploy to staging** (test environment)
3. **User acceptance testing**
4. **Deploy to production** (Option 1 recommended)
5. **Monitor for 1 week**
6. **Iterate and improve**

**Good luck with your deployment!** 🚀

For questions or issues, refer to the main README or open a GitHub issue.
