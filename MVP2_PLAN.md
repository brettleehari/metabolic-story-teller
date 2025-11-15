# GlucoLens MVP2 - Implementation Plan

**Upgrade from MVP1 to MVP2 with Authentication, Advanced ML, Real-time Features, and Frontend**

---

## 🎯 MVP2 Goals

1. **User Authentication** - Multi-user support with JWT
2. **Advanced ML Models** - PCMCI causal discovery + STUMPY pattern detection
3. **Real-time Alerts** - WebSocket-based notifications
4. **Frontend Dashboard** - React/Next.js web application
5. **Apple HealthKit** - Seamless iOS integration
6. **Production Ready** - Security, monitoring, deployment

---

## 📋 Implementation Phases

### Phase 1: Authentication & Multi-User Support (Week 1)

#### Backend Changes
- [x] JWT authentication middleware
- [x] User registration endpoint
- [x] Login endpoint with token generation
- [x] Token refresh mechanism
- [x] Password hashing (bcrypt)
- [x] Protect all existing endpoints
- [x] Remove MOCK_USER_ID from routes

#### Database Changes
- [x] User table already exists
- [x] Add refresh_tokens table
- [x] Add user_sessions table for tracking

#### API Changes
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
PUT    /api/v1/auth/profile
```

---

### Phase 2: Advanced ML Models (Week 2)

#### PCMCI Causal Discovery
- [x] Replace Pearson correlation with PCMCI
- [x] Implement time-lag analysis (1-7 days)
- [x] Statistical significance testing
- [x] Causal graph generation
- [x] Update Celery tasks

#### STUMPY Pattern Detection
- [x] Matrix profile computation
- [x] Motif discovery (recurring patterns)
- [x] Anomaly detection
- [x] Pattern visualization data
- [x] Integration with existing pattern table

#### Enhanced Insights
```
GET    /api/v1/insights/causal-graph
GET    /api/v1/insights/recurring-patterns
GET    /api/v1/insights/anomalies
GET    /api/v1/insights/predictions
```

---

### Phase 3: Real-time Alerts (Week 2-3)

#### WebSocket Server
- [x] FastAPI WebSocket endpoint
- [x] Connection management
- [x] User authentication for WebSocket
- [x] Message broadcasting

#### Alert System
- [x] Alert configuration model
- [x] Alert triggers (high/low glucose, patterns)
- [x] Alert delivery (WebSocket + email)
- [x] Alert history
- [x] User preferences

#### Database
```sql
CREATE TABLE alert_configs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    alert_type VARCHAR(50),  -- 'high_glucose', 'low_glucose', 'pattern_detected'
    threshold_value NUMERIC,
    enabled BOOLEAN DEFAULT true,
    delivery_methods JSONB  -- ['websocket', 'email', 'push']
);

CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    alert_type VARCHAR(50),
    message TEXT,
    data JSONB,
    delivered BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### API Endpoints
```
WS     /ws/alerts
GET    /api/v1/alerts/config
POST   /api/v1/alerts/config
GET    /api/v1/alerts/history
PUT    /api/v1/alerts/mark-read
```

---

### Phase 4: Frontend Dashboard (Week 3-4)

#### Technology Stack
- **Framework**: Next.js 14 (App Router)
- **UI Library**: shadcn/ui + Tailwind CSS
- **Charts**: Recharts / Chart.js
- **State**: React Query + Zustand
- **Auth**: NextAuth.js

#### Pages & Features

**1. Authentication**
- `/login` - Login page
- `/register` - Registration page
- `/forgot-password` - Password recovery

**2. Dashboard**
- `/dashboard` - Overview with key metrics
  - Average glucose (7/30/90 days)
  - Time in range chart
  - Recent readings graph
  - Quick stats cards

**3. Data Entry**
- `/data/glucose` - Glucose entry & bulk upload
- `/data/sleep` - Sleep logging
- `/data/meals` - Meal tracking
- `/data/activities` - Activity logging

**4. Insights**
- `/insights/correlations` - Correlation heatmap
- `/insights/patterns` - Discovered patterns
- `/insights/causal-graph` - Interactive causal graph
- `/insights/predictions` - Glucose predictions

**5. Settings**
- `/settings/profile` - User profile
- `/settings/alerts` - Alert configuration
- `/settings/integrations` - Apple HealthKit, etc.

#### Components
```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/
│   │   │   ├── dashboard/
│   │   │   ├── data/
│   │   │   ├── insights/
│   │   │   └── settings/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── charts/
│   │   │   ├── GlucoseLineChart.tsx
│   │   │   ├── TimeInRangeChart.tsx
│   │   │   └── CorrelationHeatmap.tsx
│   │   ├── forms/
│   │   │   ├── GlucoseEntryForm.tsx
│   │   │   └── MealEntryForm.tsx
│   │   └── ui/  (shadcn components)
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── auth.ts
│   │   └── websocket.ts
│   └── hooks/
│       ├── useGlucoseData.ts
│       ├── useDashboard.ts
│       └── useRealTimeAlerts.ts
```

---

### Phase 5: Apple HealthKit Integration (Week 4)

#### iOS Swift Package
```swift
// HealthKitManager.swift
class HealthKitManager {
    func requestAuthorization()
    func fetchGlucoseReadings(from: Date, to: Date)
    func fetchSleepAnalysis(from: Date, to: Date)
    func fetchWorkouts(from: Date, to: Date)
    func syncToBackend(data: HealthData)
}
```

#### Backend Enhancements
```
POST   /api/v1/integrations/healthkit/sync
GET    /api/v1/integrations/healthkit/status
POST   /api/v1/integrations/healthkit/configure
```

#### Features
- Automatic background sync
- Incremental updates
- Conflict resolution
- Data validation

---

### Phase 6: Production Features (Week 5)

#### Security
- [x] Rate limiting (100 req/min per user)
- [x] HTTPS enforcement
- [x] SQL injection prevention (SQLAlchemy ORM)
- [x] XSS protection
- [x] CSRF tokens
- [x] API key management

#### Monitoring
- [x] Prometheus metrics
- [x] Grafana dashboards
- [x] Health check endpoints
- [x] Error tracking (Sentry)
- [x] Logging (structured JSON)

#### Performance
- [x] Redis caching for insights
- [x] Database query optimization
- [x] CDN for static assets
- [x] Image optimization
- [x] Lazy loading

---

## 🗄️ Database Schema Updates

### New Tables

```sql
-- Refresh tokens for JWT
CREATE TABLE refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alert configurations
CREATE TABLE alert_configs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    threshold_value NUMERIC,
    enabled BOOLEAN DEFAULT true,
    delivery_methods JSONB DEFAULT '["websocket"]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alert history
CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    alert_type VARCHAR(50),
    message TEXT,
    data JSONB,
    delivered BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HealthKit integration status
CREATE TABLE healthkit_sync_status (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_sync_at TIMESTAMPTZ,
    last_glucose_reading TIMESTAMPTZ,
    last_sleep_reading TIMESTAMPTZ,
    sync_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📦 New Dependencies

### Backend
```txt
# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# WebSocket
websockets==12.0

# Advanced ML
tigramite==5.2.4.1  # Already included
stumpy==1.12.0      # Already included

# Monitoring
prometheus-client==0.19.0
sentry-sdk[fastapi]==1.39.1

# Rate limiting
slowapi==0.1.9

# Email (for alerts)
fastapi-mail==1.4.1
```

### Frontend
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "recharts": "^2.10.3",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "latest",
    "next-auth": "^5.0.0",
    "lucide-react": "^0.303.0"
  }
}
```

---

## 🚀 Deployment Strategy

### Development
```bash
# Backend
docker-compose up -d

# Frontend
cd frontend
npm run dev
```

### Staging
- **Backend**: AWS ECS Fargate / GCP Cloud Run
- **Database**: RDS PostgreSQL with TimescaleDB
- **Frontend**: Vercel / Netlify
- **Redis**: ElastiCache / Cloud Memorystore

### Production
- **Load Balancer**: AWS ALB / GCP Load Balancing
- **CDN**: CloudFront / Cloud CDN
- **Monitoring**: CloudWatch / Cloud Monitoring
- **SSL**: ACM / Let's Encrypt
- **Backup**: Automated daily snapshots

---

## 📊 API Changes Summary

### New Endpoints (MVP2)

**Authentication**
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
PUT    /api/v1/auth/profile
```

**Advanced Insights**
```
GET    /api/v1/insights/causal-graph
GET    /api/v1/insights/recurring-patterns
GET    /api/v1/insights/anomalies
GET    /api/v1/insights/predictions
```

**Alerts**
```
WS     /ws/alerts
GET    /api/v1/alerts/config
POST   /api/v1/alerts/config
GET    /api/v1/alerts/history
PUT    /api/v1/alerts/mark-read
```

**Integrations**
```
POST   /api/v1/integrations/healthkit/sync
GET    /api/v1/integrations/healthkit/status
POST   /api/v1/integrations/healthkit/configure
```

### Breaking Changes

All existing endpoints now require authentication:
```
Authorization: Bearer <jwt_token>
```

Migration guide will be provided for MVP1 users.

---

## 🧪 Testing Strategy

### Backend Tests
```bash
pytest tests/
pytest tests/test_auth.py
pytest tests/test_ml_models.py
pytest tests/test_websocket.py
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
npm run test
npm run test:e2e  # Playwright
npm run test:coverage
```

### Integration Tests
- API endpoint tests
- WebSocket connection tests
- ML pipeline tests
- End-to-end user flows

---

## 📈 Success Metrics

- **Performance**: API response time < 200ms (p95)
- **Reliability**: 99.9% uptime
- **ML Accuracy**: Correlation discovery precision > 80%
- **User Engagement**: Daily active users
- **Data Quality**: < 1% data sync errors

---

## 🎯 Timeline

**Week 1**: Authentication + Multi-user
**Week 2**: Advanced ML (PCMCI + STUMPY)
**Week 3**: Real-time Alerts + WebSocket
**Week 4**: Frontend Dashboard
**Week 5**: Apple HealthKit + Production

**Total**: 5 weeks to MVP2 completion

---

**Ready to start implementation!** 🚀

I'll begin with Phase 1: Authentication & Multi-User Support
