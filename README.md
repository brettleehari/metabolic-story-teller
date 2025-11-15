# GlucoLens

**AI-Powered Glucose Monitoring & Pattern Discovery Platform**

GlucoLens is a comprehensive health monitoring system that combines continuous glucose monitoring (CGM) data with lifestyle factors (sleep, exercise, meals) to discover personalized patterns and correlations using machine learning.

---

## 🎯 Features

### MVP1 (Current)
- ✅ **Time-series data ingestion** (glucose, sleep, activities, meals)
- ✅ **TimescaleDB** for efficient time-series storage
- ✅ **Daily aggregation** pipeline (automated via Celery)
- ✅ **Correlation analysis** (sleep, exercise, diet → glucose)
- ✅ **Pattern discovery** using association rule mining
- ✅ **RESTful API** with FastAPI
- ✅ **Background task processing** with Celery
- ✅ **Synthetic data generator** for testing
- ✅ **Docker Compose** deployment

### Coming in MVP2
- 🔜 User authentication & multi-user support
- 🔜 PCMCI causal discovery (with time lags)
- 🔜 STUMPY recurring pattern detection
- 🔜 MOMENT (HuggingFace) embeddings
- 🔜 Real-time alerts & notifications
- 🔜 Apple HealthKit integration
- 🔜 Frontend dashboard (React/Next.js)

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

### Current (MVP1)
1. **Pearson Correlation** - Statistical relationships between factors
2. **Association Rules** (Apriori algorithm) - IF-THEN pattern discovery

### Planned (MVP2)
3. **PCMCI** - Causal discovery with time-lag analysis
4. **STUMPY** - Matrix profile for recurring patterns
5. **MOMENT** - HuggingFace time-series embeddings
6. **TS2Vec** - Contrastive learning for day clustering

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

### Phase 1: MVP1 (Current) ✅
- Core data ingestion
- Time-series storage
- Basic pattern discovery
- Docker deployment

### Phase 2: MVP2 (Next)
- [ ] User authentication
- [ ] Advanced ML models (PCMCI, STUMPY)
- [ ] Frontend dashboard
- [ ] Real-time alerts
- [ ] Apple HealthKit sync

### Phase 3: Production
- [ ] Multi-platform mobile apps
- [ ] Cloud deployment (AWS/GCP)
- [ ] HIPAA compliance
- [ ] Advanced visualizations
- [ ] Community features

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
