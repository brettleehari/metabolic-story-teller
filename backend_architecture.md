# GlucoLens Backend Architecture - MVP1

## 🎯 Overview

GlucoLens backend is a time-series data processing and ML-powered insights engine for glucose monitoring and health pattern discovery.

## 🏗️ Tech Stack

### Core
- **API Framework**: FastAPI 0.104+ (async, high-performance, auto-docs)
- **Language**: Python 3.11+
- **Database**: TimescaleDB (PostgreSQL extension for time-series)
- **Cache**: Redis 7.0+
- **Task Queue**: Celery 5.3+ with Redis broker
- **ML Libraries**:
  - tigramite (PCMCI causal discovery)
  - stumpy (matrix profile pattern discovery)
  - mlxtend (association rules)
  - momentfm (HuggingFace time-series embeddings)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **API Gateway**: Nginx (reverse proxy)
- **Monitoring**: Prometheus + Grafana (future)

---

## 📊 Database Schema

### TimescaleDB Hypertables (Auto-partitioned by time)

#### `glucose_readings`
```sql
CREATE TABLE glucose_readings (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    value NUMERIC(5,1) NOT NULL, -- mg/dL (40.0 - 400.0)
    source VARCHAR(50), -- 'cgm', 'manual', 'apple_health'
    device_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('glucose_readings', 'timestamp');

-- Indexes
CREATE INDEX idx_glucose_user_time ON glucose_readings (user_id, timestamp DESC);
```

#### `sleep_data`
```sql
CREATE TABLE sleep_data (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    sleep_start TIMESTAMPTZ NOT NULL,
    sleep_end TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER, -- total sleep
    deep_sleep_minutes INTEGER,
    rem_sleep_minutes INTEGER,
    light_sleep_minutes INTEGER,
    awake_minutes INTEGER,
    quality_score NUMERIC(3,1), -- 0-10 scale
    source VARCHAR(50), -- 'apple_health', 'fitbit', 'oura', 'manual'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('sleep_data', 'sleep_start');
CREATE INDEX idx_sleep_user_date ON sleep_data (user_id, date DESC);
```

#### `activities`
```sql
CREATE TABLE activities (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    activity_type VARCHAR(50), -- 'walking', 'running', 'cycling', 'strength'
    duration_minutes INTEGER,
    intensity VARCHAR(20), -- 'light', 'moderate', 'vigorous'
    calories_burned INTEGER,
    heart_rate_avg INTEGER,
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('activities', 'timestamp');
CREATE INDEX idx_activities_user_time ON activities (user_id, timestamp DESC);
```

#### `meals`
```sql
CREATE TABLE meals (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    meal_type VARCHAR(20), -- 'breakfast', 'lunch', 'dinner', 'snack'
    carbs_grams NUMERIC(6,1),
    protein_grams NUMERIC(6,1),
    fat_grams NUMERIC(6,1),
    calories INTEGER,
    glycemic_load NUMERIC(4,1),
    description TEXT,
    photo_url VARCHAR(500),
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('meals', 'timestamp');
CREATE INDEX idx_meals_user_time ON meals (user_id, timestamp DESC);
```

### Regular PostgreSQL Tables

#### `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    date_of_birth DATE,
    diabetes_type VARCHAR(20), -- 'type1', 'type2', 'prediabetes', 'gestational'
    target_glucose_min NUMERIC(5,1) DEFAULT 70.0,
    target_glucose_max NUMERIC(5,1) DEFAULT 180.0,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### `daily_aggregates`
```sql
CREATE TABLE daily_aggregates (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    avg_glucose NUMERIC(5,1),
    min_glucose NUMERIC(5,1),
    max_glucose NUMERIC(5,1),
    std_glucose NUMERIC(5,2),
    time_in_range_percent NUMERIC(5,2),
    time_above_range_percent NUMERIC(5,2),
    time_below_range_percent NUMERIC(5,2),
    total_sleep_minutes INTEGER,
    sleep_quality_score NUMERIC(3,1),
    total_exercise_minutes INTEGER,
    total_carbs_grams NUMERIC(7,1),
    total_calories INTEGER,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

CREATE INDEX idx_daily_agg_user_date ON daily_aggregates (user_id, date DESC);
```

#### `correlations`
```sql
CREATE TABLE correlations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    factor_x VARCHAR(100), -- 'sleep_duration', 'exercise_minutes', 'carbs_intake'
    factor_y VARCHAR(100), -- 'avg_glucose', 'glucose_variability'
    correlation_coefficient NUMERIC(4,3), -- -1.00 to 1.00
    p_value NUMERIC(10,8),
    lag_days INTEGER DEFAULT 0, -- e.g., sleep yesterday -> glucose today
    sample_size INTEGER,
    confidence_level VARCHAR(10), -- 'high', 'medium', 'low'
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, factor_x, factor_y, lag_days)
);
```

#### `patterns`
```sql
CREATE TABLE patterns (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    pattern_type VARCHAR(50), -- 'recurring', 'anomaly', 'association_rule'
    description TEXT,
    confidence NUMERIC(5,4), -- 0-1 for association rules
    support NUMERIC(5,4),
    occurrences INTEGER,
    example_dates DATE[],
    metadata JSONB, -- flexible storage for pattern details
    discovered_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
```

### Data Ingestion
```
POST   /api/v1/glucose/readings          # Single reading
POST   /api/v1/glucose/bulk               # Bulk CGM upload
POST   /api/v1/sleep                      # Sleep session
POST   /api/v1/activities                 # Activity log
POST   /api/v1/meals                      # Meal entry
```

### Apple HealthKit Integration
```
POST   /api/v1/integrations/apple-health  # Bulk sync from iOS
```

### Data Retrieval
```
GET    /api/v1/glucose/readings?start=<ts>&end=<ts>
GET    /api/v1/glucose/daily-summary?date=<date>
GET    /api/v1/dashboard/summary          # Last 7/30 days overview
```

### Insights & Patterns
```
GET    /api/v1/insights/correlations      # Top correlations
GET    /api/v1/insights/patterns          # Discovered patterns
GET    /api/v1/insights/recommendations   # Actionable insights
POST   /api/v1/insights/trigger-analysis  # Manual trigger
```

### Admin/Background Tasks
```
POST   /api/v1/tasks/aggregate-daily      # Trigger aggregation
POST   /api/v1/tasks/discover-patterns    # Trigger ML analysis
GET    /api/v1/tasks/status/<task_id>     # Check task status
```

---

## ⚙️ Background Tasks (Celery)

### Scheduled Tasks
```python
# Daily at 3 AM
@celery.task
def aggregate_daily_data():
    """
    - Calculate daily stats for all users
    - Populate daily_aggregates table
    """

# Daily at 4 AM
@celery.task
def compute_correlations():
    """
    - Run PCMCI causal analysis
    - Update correlations table
    """

# Weekly on Sunday
@celery.task
def discover_patterns():
    """
    - STUMPY for recurring patterns
    - Association rules mining
    - MOMENT embeddings clustering
    """
```

### On-Demand Tasks
```python
@celery.task
def analyze_user_data(user_id, lookback_days=90):
    """User-triggered deep analysis"""

@celery.task
def generate_recommendations(user_id):
    """Personalized action items"""
```

---

## 🔬 ML Pipeline

### 1. PCMCI Causal Discovery
```python
from tigramite import PCMCI
from tigramite.independence_tests import ParCorr

# Input: daily_aggregates DataFrame
# Output: "sleep_duration (lag=1) → avg_glucose" with p-value

def run_pcmci_analysis(user_id):
    data = fetch_daily_aggregates(user_id)
    features = ['sleep_duration', 'exercise_minutes', 'carbs_grams', 'avg_glucose']

    pcmci = PCMCI(data, independence_test=ParCorr())
    results = pcmci.run_pcmci(tau_max=3)  # Check up to 3 days lag

    save_correlations(results, user_id)
```

### 2. STUMPY Pattern Discovery
```python
import stumpy

# Find recurring glucose patterns
def find_recurring_patterns(user_id):
    glucose_series = fetch_glucose_timeseries(user_id)

    # Matrix profile: find repeated subsequences
    mp = stumpy.stump(glucose_series, m=288)  # 24hr windows (5min readings)

    motifs = stumpy.motifs(glucose_series, mp)
    save_patterns(motifs, user_id, pattern_type='recurring')
```

### 3. Association Rules
```python
from mlxtend.frequent_patterns import apriori, association_rules

# Find IF-THEN rules
def mine_association_rules(user_id):
    # Transform daily data into binary features
    df = fetch_daily_aggregates(user_id)
    df['good_glucose'] = (df['time_in_range_percent'] > 80)
    df['high_sleep'] = (df['total_sleep_minutes'] > 420)
    df['exercise'] = (df['total_exercise_minutes'] > 30)

    # Apriori algorithm
    frequent_itemsets = apriori(df, min_support=0.3)
    rules = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.7)

    # Example: {high_sleep, exercise} => {good_glucose} (confidence: 0.85)
    save_association_rules(rules, user_id)
```

### 4. MOMENT Embeddings (Future)
```python
from momentfm import MOMENTPipeline

# Cluster similar days
def cluster_similar_days(user_id):
    daily_patterns = fetch_daily_timeseries(user_id)

    model = MOMENTPipeline.from_pretrained()
    embeddings = model.encode(daily_patterns)

    # K-means clustering
    clusters = kmeans(embeddings, n_clusters=5)
    # Label: "Your best days share this pattern..."
```

---

## 🐳 Docker Compose Setup

```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: glucolens
      POSTGRES_USER: glucolens
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - timescale_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://glucolens:${DB_PASSWORD}@timescaledb:5432/glucolens
      REDIS_URL: redis://redis:6379
    depends_on:
      - timescaledb
      - redis

  celery_worker:
    build: ./backend
    command: celery -A app.tasks worker --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgresql://glucolens:${DB_PASSWORD}@timescaledb:5432/glucolens
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis
      - timescaledb

  celery_beat:
    build: ./backend
    command: celery -A app.tasks beat --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgresql://glucolens:${DB_PASSWORD}@timescaledb:5432/glucolens
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis

volumes:
  timescale_data:
  redis_data:
```

---

## 📱 Apple HealthKit Integration

### iOS Swift Code (Client-side)
```swift
import HealthKit

func syncToGlucoLens() {
    let healthStore = HKHealthStore()

    // Glucose
    let glucoseType = HKQuantityType.quantityType(forIdentifier: .bloodGlucose)!
    let predicate = HKQuery.predicateForSamples(withStart: lastSyncDate, end: Date())

    let query = HKSampleQuery(sampleType: glucoseType, predicate: predicate) { query, samples, error in
        let readings = samples?.map { sample -> [String: Any] in
            let glucose = sample as! HKQuantitySample
            return [
                "timestamp": glucose.startDate.iso8601,
                "value": glucose.quantity.doubleValue(for: .milligramsPerDeciliter),
                "source": "apple_health"
            ]
        }

        // POST to /api/v1/integrations/apple-health
        sendToBackend(readings)
    }

    healthStore.execute(query)
}
```

### Backend Endpoint
```python
@router.post("/integrations/apple-health")
async def sync_apple_health(data: AppleHealthSyncData, user: User = Depends(current_user)):
    """
    Accepts bulk data from iOS HealthKit:
    - glucose_readings: [...]
    - sleep_sessions: [...]
    - activities: [...]
    """
    async with db.transaction():
        await insert_bulk_glucose(data.glucose_readings)
        await insert_bulk_sleep(data.sleep_sessions)
        await insert_bulk_activities(data.activities)

    # Trigger aggregation
    aggregate_daily_data.delay(user_id=user.id)

    return {"status": "success", "records_synced": len(data.glucose_readings)}
```

---

## 🚀 Deployment Strategy

### MVP1 (Local/Development)
```bash
docker-compose up -d
python -m alembic upgrade head  # Run migrations
uvicorn app.main:app --reload
```

### Production (AWS/GCP)
- **API**: ECS Fargate / Cloud Run
- **Database**: RDS for PostgreSQL + TimescaleDB extension
- **Redis**: ElastiCache / Cloud Memorystore
- **Celery**: ECS tasks / Cloud Run Jobs
- **Load Balancer**: ALB / Cloud Load Balancing

---

## 📈 Scalability Considerations

1. **Time-series partitioning**: Auto-partition by month
2. **Continuous aggregates** (TimescaleDB feature):
   ```sql
   CREATE MATERIALIZED VIEW hourly_glucose_avg
   WITH (timescaledb.continuous) AS
   SELECT time_bucket('1 hour', timestamp) AS hour,
          user_id,
          AVG(value) as avg_glucose
   FROM glucose_readings
   GROUP BY hour, user_id;
   ```
3. **Redis caching**: Cache correlations for 24 hours
4. **Celery autoscaling**: Add workers based on queue length

---

## 🔐 Security

- **JWT tokens** with refresh mechanism
- **Rate limiting**: 100 req/min per user
- **HTTPS only** in production
- **HIPAA compliance** considerations:
  - Encrypted at rest (AWS KMS)
  - Audit logs for PHI access
  - User consent management

---

## 📊 Sample Data Format

### CGM Upload Example
```json
POST /api/v1/glucose/bulk
{
  "readings": [
    {"timestamp": "2025-01-15T08:00:00Z", "value": 95.0, "source": "dexcom_g7"},
    {"timestamp": "2025-01-15T08:05:00Z", "value": 98.0, "source": "dexcom_g7"}
  ]
}
```

### Sleep Data Example
```json
POST /api/v1/sleep
{
  "date": "2025-01-14",
  "sleep_start": "2025-01-14T23:00:00Z",
  "sleep_end": "2025-01-15T07:00:00Z",
  "duration_minutes": 480,
  "deep_sleep_minutes": 120,
  "quality_score": 8.5,
  "source": "apple_watch"
}
```

---

## 🎯 MVP1 Deliverables

✅ Core API endpoints (glucose, sleep, meals, activities)
✅ TimescaleDB schema + migrations
✅ Daily aggregation pipeline
✅ PCMCI correlation analysis
✅ Association rules discovery
✅ Sample data generator (synthetic)
✅ Docker Compose setup
✅ API documentation (FastAPI auto-docs)

**Out of Scope for MVP1:**
- User authentication (add in MVP2)
- MOMENT/TS2Vec embeddings
- Real-time alerts
- Mobile app (frontend only)

---

## 📚 Next Steps

1. Run migrations: `alembic upgrade head`
2. Generate sample data: `python scripts/generate_sample_data.py`
3. Start services: `docker-compose up`
4. Test API: `http://localhost:8000/docs`
5. Trigger analysis: `POST /api/v1/tasks/discover-patterns`

---

**Ready to build! 🚀**
