# GlucoLens

**AI-Powered Glucose Monitoring & Pattern Discovery Platform**

GlucoLens is a comprehensive health monitoring system that combines continuous glucose monitoring (CGM) data with lifestyle factors (sleep, exercise, meals) to discover personalized patterns and correlations using machine learning.

---

## 🎯 Implementation Status

### ✅ Fully Implemented (MVP2 Phase)

**Backend - Core API:**
- ✅ **JWT Authentication** - Registration, login, token refresh, profile management
- ✅ **Glucose Data API** - Create, bulk upload, query with date filters
- ✅ **Health Metrics** - HbA1c, medications, insulin, blood pressure, body metrics
- ✅ **TimescaleDB Integration** - Time-series optimized storage
- ✅ **Advanced ML Analytics:**
  - ✅ PCMCI causal discovery (Tigramite) with time-lag analysis
  - ✅ STUMPY pattern detection (matrix profile, motifs, anomalies)
  - ✅ Association rule mining (Apriori algorithm)
  - ✅ Correlation analysis with statistical significance
- ✅ **Celery Background Tasks:**
  - ✅ Daily data aggregation (scheduled 3 AM)
  - ✅ ML analysis pipeline (correlation, patterns, PCMCI, STUMPY)
  - ✅ Scheduled pattern discovery (weekly)
- ✅ **Docker Compose** - Full service orchestration
- ✅ **Synthetic Data Generator** - Realistic test data creation

**Frontend:**
- ✅ **React 18 + TypeScript + Vite** - Modern build setup
- ✅ **Shadcn UI** - Complete component library (40+ components)
- ✅ **Dashboard** - Insights visualization with charts
- ✅ **Upload Wizard** - Multi-step data upload flow
- ✅ **Authentication UI** - Login/register forms
- ✅ **Sample Visualizations** - Demo charts and impact visuals

### ⚠️ Partially Implemented

**Authentication Inconsistency:**
- ⚠️ Glucose, health metrics, advanced insights - Use proper JWT auth
- ⚠️ Sleep, meals, activities, basic insights - Still use MOCK_USER_ID (needs fixing)

**Data Retrieval:**
- ⚠️ Glucose - Full CRUD implemented
- ⚠️ Sleep, meals, activities - Only CREATE, missing GET endpoints

**Frontend Integration:**
- ⚠️ Magic link authentication - Frontend expects it, backend has email/password only
- ⚠️ Token refresh - Backend ready, frontend missing auto-refresh logic
- ⚠️ Health metrics UI - Backend ready, frontend pages missing

### ❌ Not Implemented (Gaps)

**Critical Gaps:**
- ❌ **Testing** - No pytest tests, no frontend tests, no CI/CD
- ❌ **Database Migrations** - Alembic not configured (manual SQL only)
- ❌ **Production Config** - No rate limiting, CSRF protection, monitoring
- ❌ **Error Tracking** - No Sentry/error monitoring integration

**Missing Features:**
- ❌ **Real-time Alerts** - WebSocket endpoints not implemented
- ❌ **Apple HealthKit** - No integration or OAuth flow
- ❌ **MOMENT Model** - Not integrated (commented out in requirements)
- ❌ **Data Export** - No CSV/JSON export functionality
- ❌ **Magic Link Auth** - Email service integration missing
- ❌ **Predictive Features** - Glucose forecasting, meal impact prediction

**Frontend Gaps:**
- ❌ Settings/profile management pages
- ❌ Health metrics input forms
- ❌ Historical data visualization pages
- ❌ Pattern/anomaly detail views
- ❌ Error boundaries and comprehensive error handling

**Production Readiness:**
- ❌ SSL/TLS configuration
- ❌ Secrets management (Vault, AWS Secrets Manager)
- ❌ Application monitoring (APM, metrics)
- ❌ Logging aggregation
- ❌ Backup/restore procedures
- ❌ HIPAA compliance documentation

---

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │  (Coming soon - React/Next.js)
│  Dashboard  │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────┐
│           FastAPI Backend                   │
│  ┌──────────────────────────────────────┐  │
│  │  Data Ingestion (Glucose, Sleep,     │  │
│  │  Activities, Meals)                  │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  Insights API (Correlations,         │  │
│  │  Patterns, Dashboard)                │  │
│  └──────────────────────────────────────┘  │
└──────┬──────────────────────────────────────┘
       │
┌──────▼───────────────────┐  ┌───────────────┐
│   TimescaleDB            │  │  Redis        │
│  (Time-series storage)   │  │  (Cache/Queue)│
└──────────────────────────┘  └───────┬───────┘
                                      │
                             ┌────────▼────────┐
                             │ Celery Workers  │
                             │ ┌─────────────┐ │
                             │ │ Aggregation │ │
                             │ │ Correlation │ │
                             │ │ Patterns    │ │
                             │ └─────────────┘ │
                             └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone & Setup

```bash
git clone <repo-url>
cd glucolens

# Copy environment template
cp backend/.env.example backend/.env

# Edit .env and set DB_PASSWORD and SECRET_KEY
nano backend/.env
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

**Services:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432
- Redis: localhost:6379

### 3. Generate Sample Data

```bash
# Generate 90 days of realistic synthetic data
docker-compose exec api python scripts/generate_sample_data.py --days 90
```

### 4. Run Analysis

```bash
# Trigger pattern discovery
curl -X POST http://localhost:8000/api/v1/insights/trigger-analysis

# View results
curl http://localhost:8000/api/v1/insights/correlations
curl http://localhost:8000/api/v1/insights/patterns
curl http://localhost:8000/api/v1/insights/dashboard
```

---

## 🚢 Deployment & Development Strategy

### Current State: Development-Ready
The application is currently **development-ready** with Docker Compose, but **not production-ready**. See gaps above.

### Quick Fixes Needed Before Production
1. **Fix Authentication** - Add `get_current_user` to sleep/meals/activities routes (1 day)
2. **Add GET Endpoints** - Sleep, meals, activities data retrieval (1 day)
3. **Setup Alembic** - Database migration management (2 days)
4. **Add Basic Tests** - Critical path coverage (3-5 days)
5. **Error Monitoring** - Sentry integration (1 day)
6. **Rate Limiting** - FastAPI middleware (1 day)

**Estimated Time to Production-Ready: 2-3 weeks** (with above fixes + deployment setup)

### Recommended Development Workflow

#### 1. **Feature Branch Strategy**
```bash
main (production-ready code)
  ├── develop (integration branch)
  │   ├── feature/fix-auth-gaps
  │   ├── feature/add-get-endpoints
  │   ├── feature/setup-alembic
  │   └── feature/add-tests
```

**Workflow:**
- Create feature branch from `develop`
- Make changes, test locally
- Create PR to `develop`
- After testing, merge `develop` → `main` for deployment

#### 2. **Local Development Setup**
```bash
# 1. Clone and setup
git clone <repo>
cd metabolic-story-teller
cp backend/.env.example backend/.env
# Edit .env with your secrets

# 2. Start development environment
docker-compose up -d          # Start backend services
npm install                   # Install frontend dependencies
npm run dev                   # Start frontend (localhost:8080)

# 3. Generate test data
docker-compose exec api python scripts/generate_sample_data.py --days 90

# 4. Make changes
# - Edit backend: backend/app/
# - Edit frontend: src/
# - Changes auto-reload in both

# 5. Test manually
# - Backend: http://localhost:8000/docs
# - Frontend: http://localhost:8080

# 6. Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

#### 3. **Testing Before Commit**
```bash
# Backend linting (when configured)
docker-compose exec api black app/
docker-compose exec api flake8 app/

# Frontend linting
npm run lint

# Type checking
npx tsc --noEmit

# Run tests (when implemented)
docker-compose exec api pytest
npm run test
```

#### 4. **Database Changes**
**Current (Manual SQL):**
```bash
# Edit backend/migrations/your_changes.sql
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /migrations/your_changes.sql
```

**Recommended (Alembic - TODO):**
```bash
# After Alembic setup
docker-compose exec api alembic revision --autogenerate -m "add new column"
docker-compose exec api alembic upgrade head
```

### Deployment Architecture Recommendations

#### Option 1: Docker Compose (Small Scale - Up to 100 users)
**Pros:** Simple, cost-effective, good for MVP
**Cons:** Single server, limited scalability

```
DigitalOcean/AWS EC2 Instance ($20-40/mo)
  ├── Docker Compose
  │   ├── Nginx (SSL termination)
  │   ├── Frontend (static files)
  │   ├── Backend (FastAPI)
  │   ├── TimescaleDB
  │   ├── Redis
  │   ├── Celery Worker
  │   └── Celery Beat
  └── Backups (automated daily)
```

**Setup Steps:**
1. Provision Ubuntu 22.04 server (4GB RAM minimum)
2. Install Docker + Docker Compose
3. Clone repository
4. Configure `.env` with production secrets
5. Setup Nginx reverse proxy with Let's Encrypt SSL
6. Configure automated backups (pg_dump to S3)
7. Setup monitoring (uptime, error logs)

#### Option 2: Kubernetes (Scale - 100+ users)
**Pros:** Auto-scaling, high availability, production-grade
**Cons:** Complex, higher cost

```
AWS EKS / GCP GKE / Azure AKS
  ├── Ingress (Load Balancer + SSL)
  ├── Frontend (Static CDN - CloudFront/CloudFlare)
  ├── Backend (3+ replicas, auto-scaling)
  ├── RDS TimescaleDB (managed database)
  ├── ElastiCache Redis (managed)
  ├── Celery Workers (3+ replicas)
  ├── Celery Beat (1 replica)
  ├── Monitoring (Prometheus + Grafana)
  └── Logging (ELK Stack / CloudWatch)
```

#### Option 3: Serverless (Cost-Optimized)
**Pros:** Pay per use, no server management
**Cons:** Cold starts, vendor lock-in

```
AWS Lambda / Google Cloud Functions
  ├── API Gateway (REST endpoints)
  ├── Lambda Functions (FastAPI via Mangum)
  ├── CloudFront (Frontend CDN)
  ├── RDS Aurora Serverless (TimescaleDB)
  ├── ElastiCache Serverless (Redis)
  ├── EventBridge (scheduled tasks)
  └── SQS/SNS (task queue)
```

### Recommended First Deployment: Option 1 (Docker Compose)

**Cost:** $30-50/month
**Effort:** 1-2 days setup
**Good for:** MVP, beta testing, early users

**Production Checklist:**
- [ ] Fix authentication gaps
- [ ] Setup Alembic migrations
- [ ] Add basic tests (critical paths)
- [ ] Configure production .env
- [ ] Setup SSL certificate (Let's Encrypt)
- [ ] Configure Nginx reverse proxy
- [ ] Setup automated backups (daily pg_dump to S3/DigitalOcean Spaces)
- [ ] Configure error monitoring (Sentry)
- [ ] Setup uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure log aggregation
- [ ] Add rate limiting
- [ ] Security hardening (firewall, fail2ban)
- [ ] Document deployment process
- [ ] Create restore/rollback procedures

---

## 📚 Documentation

- [Backend Architecture](backend_architecture.md) - Complete technical design
- [Backend README](backend/README.md) - API documentation & development guide
- [API Docs (Interactive)](http://localhost:8000/docs) - Swagger UI

---

## 🧪 Example API Usage

### Upload Glucose Reading

```bash
curl -X POST http://localhost:8000/api/v1/glucose/readings \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-01-15T08:00:00Z",
    "value": 95.0,
    "source": "dexcom_g7"
  }'
```

### Bulk Upload CGM Data

```bash
curl -X POST http://localhost:8000/api/v1/glucose/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {"timestamp": "2025-01-15T08:00:00Z", "value": 95.0},
      {"timestamp": "2025-01-15T08:05:00Z", "value": 98.0},
      {"timestamp": "2025-01-15T08:10:00Z", "value": 102.0}
    ]
  }'
```

### Get Insights

```bash
# Top correlations
curl http://localhost:8000/api/v1/insights/correlations

# Discovered patterns
curl http://localhost:8000/api/v1/insights/patterns

# Dashboard summary
curl http://localhost:8000/api/v1/insights/dashboard?period_days=7
```

---

## 🔬 ML Models & Techniques

### ✅ Implemented & Active
1. **PCMCI (Tigramite)** - Causal discovery with time-lag analysis
   - ParCorr conditional independence tests
   - Directed acyclic graph (DAG) generation
   - Top causal factors extraction
   - Fallback to correlation on insufficient data

2. **STUMPY (Matrix Profile)** - Recurring pattern detection
   - Motif discovery for repeating glucose patterns
   - Discord detection for anomalies
   - Similar day finder
   - Configurable window sizes

3. **Association Rules (mlxtend)** - IF-THEN pattern mining
   - Apriori algorithm for frequent itemsets
   - Confidence and support thresholds
   - Binary feature transformation
   - Weekly pattern discovery

4. **Pearson Correlation** - Statistical relationships
   - Time-lagged correlations (0-7 days)
   - Statistical significance testing (p-values)
   - Fallback for PCMCI when data insufficient

### ❌ Planned but Not Implemented
5. **MOMENT** - HuggingFace time-series embeddings (commented out)
6. **TS2Vec** - Contrastive learning for day clustering
7. **Predictive Models** - Glucose forecasting, meal impact prediction

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- TimescaleDB (PostgreSQL + time-series)
- Redis (caching & task queue)
- Celery (background jobs)
- SQLAlchemy (ORM)
- Pydantic (validation)

**ML Libraries:**
- tigramite (PCMCI)
- stumpy (matrix profile)
- mlxtend (association rules)
- pandas, numpy, scipy

**Infrastructure:**
- Docker & Docker Compose
- Nginx (future)

---

## 📁 Project Structure

```
glucolens/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── schemas/         # API schemas
│   │   ├── routes/          # API endpoints
│   │   ├── main.py          # FastAPI app
│   │   ├── tasks.py         # Celery tasks
│   │   └── config.py        # Settings
│   ├── migrations/          # Database schema
│   ├── scripts/             # Utilities
│   ├── tests/               # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── backend_architecture.md
└── README.md
```

---

## 🧑‍💻 Development

See [Backend README](backend/README.md) for detailed development instructions.

Quick commands:

```bash
# Start services
docker-compose up -d

# Rebuild after code changes
docker-compose up -d --build

# Run tests
docker-compose exec api pytest

# Access database
docker-compose exec timescaledb psql -U glucolens -d glucolens

# View Celery tasks
docker-compose exec celery_worker celery -A app.tasks inspect active
```

---

## 🗺️ Roadmap

### Phase 1: MVP1 ✅ COMPLETE
- ✅ Core data ingestion (glucose, sleep, activities, meals)
- ✅ TimescaleDB time-series storage
- ✅ Basic pattern discovery (association rules)
- ✅ Docker deployment

### Phase 2: MVP2 ⚠️ 70% COMPLETE
**Completed:**
- ✅ User authentication (JWT with refresh tokens)
- ✅ Advanced ML models (PCMCI, STUMPY)
- ✅ Frontend dashboard (React + Shadcn UI)
- ✅ Health metrics tracking (HbA1c, medications, insulin, BP, body metrics)
- ✅ Celery background task scheduling

**In Progress:**
- ⚠️ Fix authentication inconsistencies (sleep/meals/activities routes)
- ⚠️ Complete data retrieval endpoints (GET for sleep/meals/activities)
- ⚠️ Magic link authentication
- ⚠️ Frontend health metrics pages

**Not Started:**
- ❌ Real-time alerts (WebSocket)
- ❌ Apple HealthKit sync
- ❌ Comprehensive testing suite
- ❌ Database migrations (Alembic)

### Phase 3: Production Readiness (Next Priority)
**Critical for Deployment:**
- [ ] Fix authentication gaps
- [ ] Implement Alembic migrations
- [ ] Add comprehensive testing (pytest, frontend tests)
- [ ] Set up error monitoring (Sentry)
- [ ] Add rate limiting
- [ ] Configure SSL/TLS
- [ ] Secrets management
- [ ] Application monitoring (Prometheus/Grafana)
- [ ] Backup/restore procedures
- [ ] CI/CD pipeline

**Future Enhancements:**
- [ ] Real-time WebSocket alerts
- [ ] Apple HealthKit integration
- [ ] Data export functionality
- [ ] MOMENT model integration
- [ ] Predictive glucose forecasting
- [ ] Multi-platform mobile apps
- [ ] Cloud deployment (AWS/GCP)
- [ ] HIPAA compliance certification

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🙏 Acknowledgments

- **TimescaleDB** for time-series optimization
- **FastAPI** for the amazing framework
- **tigramite**, **stumpy**, and **mlxtend** for ML algorithms
- Diabetes community for inspiration

---

## 📧 Contact

Questions? Open an issue or contact the maintainers.

**Built with ❤️ for better glucose management**
