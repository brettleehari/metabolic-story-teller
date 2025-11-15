# GlucoLens Backend - MVP1

FastAPI backend with TimescaleDB and ML-powered pattern discovery for glucose monitoring.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your values (especially DB_PASSWORD and SECRET_KEY)
nano .env
```

### 2. Start Services

```bash
# From project root
cd /path/to/glucolens

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

Services will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **TimescaleDB**: localhost:5432
- **Redis**: localhost:6379

### 3. Generate Sample Data

```bash
# Enter the API container
docker-compose exec api bash

# Generate 90 days of synthetic data
python scripts/generate_sample_data.py --days 90

# Exit container
exit
```

### 4. Run Analysis

Trigger pattern discovery and correlation analysis:

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/insights/trigger-analysis
```

Or manually trigger Celery tasks:

```bash
docker-compose exec celery_worker bash
celery -A app.tasks call app.tasks.run_full_analysis --args='["00000000-0000-0000-0000-000000000001"]'
```

---

## 📊 API Endpoints

### Data Ingestion

**Glucose**
```bash
# Single reading
POST /api/v1/glucose/readings
{
  "timestamp": "2025-01-15T08:00:00Z",
  "value": 95.0,
  "source": "dexcom_g7"
}

# Bulk upload (CGM export)
POST /api/v1/glucose/bulk
{
  "readings": [
    {"timestamp": "2025-01-15T08:00:00Z", "value": 95.0},
    {"timestamp": "2025-01-15T08:05:00Z", "value": 98.0}
  ]
}

# Get readings
GET /api/v1/glucose/readings?start=2025-01-15T00:00:00Z&end=2025-01-16T00:00:00Z
```

**Sleep**
```bash
POST /api/v1/sleep
{
  "date": "2025-01-15",
  "sleep_start": "2025-01-15T23:00:00Z",
  "sleep_end": "2025-01-16T07:00:00Z",
  "duration_minutes": 480,
  "quality_score": 8.5,
  "source": "apple_watch"
}
```

**Activities**
```bash
POST /api/v1/activities
{
  "timestamp": "2025-01-15T18:00:00Z",
  "activity_type": "running",
  "duration_minutes": 45,
  "intensity": "moderate",
  "calories_burned": 350
}
```

**Meals**
```bash
POST /api/v1/meals
{
  "timestamp": "2025-01-15T12:00:00Z",
  "meal_type": "lunch",
  "carbs_grams": 60.0,
  "protein_grams": 30.0,
  "fat_grams": 20.0,
  "calories": 500
}
```

### Insights

```bash
# Get correlations
GET /api/v1/insights/correlations

# Get discovered patterns
GET /api/v1/insights/patterns

# Get dashboard summary (7-day overview)
GET /api/v1/insights/dashboard?period_days=7

# Trigger analysis
POST /api/v1/insights/trigger-analysis
```

---

## 🧪 Testing API

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Or use curl:

```bash
# Health check
curl http://localhost:8000/health

# Upload glucose reading
curl -X POST http://localhost:8000/api/v1/glucose/readings \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-01-15T08:00:00Z",
    "value": 95.0,
    "source": "manual"
  }'

# Get correlations
curl http://localhost:8000/api/v1/insights/correlations
```

---

## 🔬 ML Analysis Pipeline

### 1. Daily Aggregation
Runs automatically at 3 AM daily (configured in Celery Beat).

Computes:
- Average, min, max glucose
- Time in range (TIR %)
- Sleep duration & quality
- Total exercise minutes
- Carb/calorie intake

### 2. Correlation Analysis
Runs at 4 AM daily using statistical methods (Pearson correlation).

Discovers relationships like:
- Sleep duration → Average glucose
- Exercise → Glucose variability
- Carb intake → Time in range

**Planned upgrade**: PCMCI causal discovery for lag relationships (e.g., "sleep yesterday → glucose today").

### 3. Pattern Discovery
Runs weekly (Sunday midnight) using association rule mining.

Finds patterns like:
- `IF high_sleep AND exercise THEN good_glucose` (confidence: 85%)
- Recurring glucose patterns (STUMPY matrix profile - coming soon)

---

## 🛠️ Development

### Local Development (Without Docker)

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL + Redis (via Docker)
docker-compose up -d timescaledb redis

# Run migrations
psql $DATABASE_URL < migrations/init.sql

# Start API
uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A app.tasks worker --loglevel=info

# Start Celery beat (separate terminal)
celery -A app.tasks beat --loglevel=info
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings
│   ├── tasks.py             # Celery background tasks
│   ├── models/              # SQLAlchemy models
│   │   ├── base.py
│   │   ├── glucose.py
│   │   ├── sleep.py
│   │   ├── activity.py
│   │   ├── meal.py
│   │   ├── aggregate.py
│   │   ├── correlation.py
│   │   └── pattern.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── glucose.py
│   │   ├── sleep.py
│   │   ├── activity.py
│   │   ├── meal.py
│   │   └── insights.py
│   └── routes/              # API endpoints
│       ├── glucose.py
│       ├── sleep.py
│       ├── activities.py
│       ├── meals.py
│       └── insights.py
├── migrations/
│   └── init.sql             # Database schema
├── scripts/
│   └── generate_sample_data.py
├── tests/
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Rebuild after code changes
docker-compose up -d --build

# Access database
docker-compose exec timescaledb psql -U glucolens -d glucolens

# Execute command in API container
docker-compose exec api python scripts/generate_sample_data.py
```

---

## 📈 Next Steps (MVP2)

- [ ] User authentication (JWT)
- [ ] PCMCI causal discovery implementation
- [ ] STUMPY recurring pattern detection
- [ ] MOMENT embeddings for day clustering
- [ ] Real-time alerts (WebSocket)
- [ ] Export reports (PDF)
- [ ] Apple HealthKit integration
- [ ] Unit tests (80% coverage)

---

## 🔐 Security Notes

**MVP1 uses a mock user ID for simplicity.** For production:

1. Implement JWT authentication
2. Use environment variables for secrets
3. Enable HTTPS
4. Add rate limiting
5. Audit logging for PHI access (HIPAA compliance)

---

## 🆘 Troubleshooting

**Database connection error?**
```bash
# Check if TimescaleDB is running
docker-compose ps timescaledb

# Check logs
docker-compose logs timescaledb
```

**Celery tasks not running?**
```bash
# Check Celery worker logs
docker-compose logs celery_worker

# Verify Redis connection
docker-compose exec redis redis-cli ping
```

**Import errors?**
```bash
# Rebuild containers
docker-compose down
docker-compose up -d --build
```

---

## 📄 License

MIT License - See LICENSE file for details.

---

**Built with ❤️ for better glucose management**
