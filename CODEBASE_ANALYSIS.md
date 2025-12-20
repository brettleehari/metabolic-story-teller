# GlucoLens Codebase Comprehensive Analysis

**Date:** January 2025
**Purpose:** Complete walkthrough, gap analysis, and refactoring recommendations
**Status:** In-depth technical audit

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Database Schema](#database-schema)
5. [API Endpoints Analysis](#api-endpoints-analysis)
6. [Critical Gaps & Issues](#critical-gaps--issues)
7. [Refactoring Recommendations](#refactoring-recommendations)
8. [Dummy Data Strategy](#dummy-data-strategy)
9. [Free-Tier Deployment Options](#free-tier-deployment-options)
10. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

### Current State
- **Completion:** ~70% MVP2
- **Backend:** FastAPI + TimescaleDB + Celery + Redis
- **Frontend:** React 18 + TypeScript + Vite + Shadcn UI
- **ML Services:** PCMCI (Tigramite), STUMPY, Association Rules
- **Lines of Code:** ~15,000+ (backend + frontend)

### Key Findings
✅ **Strengths:**
- Solid ML foundation (PCMCI, STUMPY working)
- Modern tech stack
- Good separation of concerns
- Type safety (TypeScript + Pydantic)

❌ **Critical Issues:**
- **Authentication inconsistency** - Some routes use MOCK_USER_ID
- **Missing GET endpoints** - Sleep, meals, activities have no retrieval
- **Frontend/Backend mismatch** - Magic link vs email/password auth
- **No file upload implementation** - Frontend expects it, backend missing
- **Incomplete data visualization** - Dashboard components not connected to real data

---

## Backend Architecture

### Tech Stack
```
FastAPI 0.104.1
├── SQLAlchemy 2.0.23 (async)
├── TimescaleDB (PostgreSQL extension)
├── Celery 5.3.4 (background tasks)
├── Redis 5.0.1 (cache + queue)
├── Tigramite 5.2.3.2 (PCMCI causal discovery)
├── STUMPY 1.12.0 (pattern detection)
└── mlxtend 0.23.0 (association rules)
```

### Directory Structure
```
backend/
├── app/
│   ├── models/          # 15 SQLAlchemy models
│   ├── schemas/         # 13 Pydantic schemas
│   ├── routes/          # 12 API route modules
│   ├── services/        # 2 ML services (PCMCI, STUMPY)
│   ├── utils/           # Auth utilities
│   ├── dependencies.py  # FastAPI dependencies
│   ├── config.py        # Settings (Pydantic BaseSettings)
│   ├── main.py          # FastAPI app
│   ├── tasks.py         # Celery tasks (aggregation)
│   └── tasks_ml.py      # Celery ML tasks
├── scripts/
│   ├── generate_sample_data.py
│   ├── generate_demo_users.py
│   ├── run_ml_pipeline.py
│   ├── deploy_demo.sh
│   └── validate_deployment.sh
└── migrations/          # Manual SQL files (Alembic not configured)
```

### Database Models (15 total)

| Model | Purpose | Key Fields | Auth Status |
|-------|---------|------------|-------------|
| `User` | User accounts | email, password_hash, diabetes_type | ✅ Proper |
| `GlucoseReading` | CGM data | timestamp, value, source | ✅ Proper |
| `SleepData` | Sleep tracking | start_time, end_time, quality | ❌ MOCK_USER_ID |
| `Meal` | Food logging | timestamp, description, macros | ❌ MOCK_USER_ID |
| `Activity` | Exercise logging | type, duration, intensity | ❌ MOCK_USER_ID |
| `HbA1c` | HbA1c tests | test_date, value | ✅ Proper |
| `Medication` | Medication tracking | name, dosage, frequency | ✅ Proper |
| `Insulin` | Insulin doses | timestamp, dose_units, type | ✅ Proper |
| `BloodPressure` | BP readings | systolic, diastolic | ✅ Proper |
| `BodyMetrics` | Weight, BMI | weight_kg, bmi | ✅ Proper |
| `Correlation` | ML insights | factor_type, correlation | ✅ Proper |
| `Pattern` | Association rules | antecedents, confidence | ✅ Proper |
| `DailyAggregate` | Aggregated stats | date, avg_glucose, etc | ✅ Proper |
| `RefreshToken` | JWT refresh | token, expires_at | ✅ Proper |

### API Routes Analysis

#### ✅ Fully Implemented Routes

**Authentication** (`/api/v1/auth`)
- ✅ POST `/register` - Create new user account
- ✅ POST `/login` - Email + password authentication
- ✅ POST `/refresh` - Refresh access token
- ✅ POST `/logout` - Invalidate refresh token
- ✅ GET `/me` - Get current user profile
- ✅ PUT `/profile` - Update user profile
- ✅ POST `/change-password` - Change password

**Glucose** (`/api/v1/glucose`)
- ✅ POST `/readings` - Create single reading (auth)
- ✅ POST `/bulk` - Bulk upload (auth)
- ✅ GET `/readings` - Get readings with filters (auth)

**Health Metrics** (all with auth)
- ✅ POST `/api/v1/hba1c` - Log HbA1c
- ✅ GET `/api/v1/hba1c` - Get HbA1c history
- ✅ POST `/api/v1/medications` - Add medication
- ✅ GET `/api/v1/medications` - List medications
- ✅ PUT `/api/v1/medications/{id}` - Update medication
- ✅ POST `/api/v1/insulin` - Log insulin dose
- ✅ GET `/api/v1/insulin` - Get insulin history
- ✅ POST `/api/v1/blood_pressure` - Log BP
- ✅ GET `/api/v1/blood_pressure` - Get BP history
- ✅ POST `/api/v1/body_metrics` - Log body metrics
- ✅ GET `/api/v1/body_metrics` - Get body metrics

**Insights** (`/api/v1/insights`)
- ✅ GET `/correlations` - Top correlations (MOCK_USER_ID)
- ✅ GET `/patterns` - Discovered patterns (MOCK_USER_ID)
- ✅ GET `/dashboard` - Dashboard summary (MOCK_USER_ID)
- ✅ POST `/trigger-analysis` - Manual trigger

**Advanced Insights** (`/api/v1/advanced_insights`)
- ✅ GET `/pcmci` - PCMCI causal discovery results (auth)
- ✅ POST `/run_pcmci` - Trigger PCMCI analysis (auth)
- ✅ GET `/stumpy_patterns` - STUMPY patterns (auth)
- ✅ POST `/run_stumpy` - Trigger STUMPY analysis (auth)

#### ❌ Partially Implemented Routes (Missing GET)

**Sleep** (`/api/v1/sleep`)
- ✅ POST `` - Create sleep record (MOCK_USER_ID)
- ❌ GET `` - **MISSING** - No way to retrieve sleep data!

**Meals** (`/api/v1/meals`)
- ✅ POST `` - Create meal (MOCK_USER_ID)
- ❌ GET `` - **MISSING** - No way to retrieve meals!

**Activities** (`/api/v1/activities`)
- ✅ POST `` - Create activity (MOCK_USER_ID)
- ❌ GET `` - **MISSING** - No way to retrieve activities!

#### ❌ Missing Routes (Frontend Expects)

**File Uploads** (`/api/v1/uploads`)
- ❌ POST `/uploads` - Upload CSV/JSON files
- ❌ GET `/uploads` - Upload history
- ❌ Backend endpoint doesn't exist at all!

**Analysis Jobs** (`/api/v1/analysis`)
- ❌ POST `/analysis/start` - Start analysis job
- ❌ GET `/analysis/{job_id}/status` - Check job status
- ❌ Not implemented (Celery tasks exist but no REST endpoints)

**Magic Link Auth** (`/api/v1/auth`)
- ❌ POST `/auth/request-magic-link` - Send magic link email
- ❌ POST `/auth/verify-token` - Verify magic link token
- ❌ Frontend expects this, backend has email/password only

---

## Frontend Architecture

### Tech Stack
```
React 18.3.1
├── TypeScript 5.6.2
├── Vite 5.4.2
├── React Router 6.26.2
├── TanStack Query 5.56.2
├── Shadcn UI (40+ components)
├── Tailwind CSS 3.4.1
├── Recharts 2.12.7
└── Lucide React (icons)
```

### Directory Structure
```
src/
├── components/
│   ├── ui/              # 40+ Shadcn UI components
│   ├── AuthForm.tsx     # Login/register (expects magic link)
│   ├── Dashboard.tsx    # Insights dashboard
│   ├── UploadWizard.tsx # File upload wizard
│   ├── MetabolicChart.tsx
│   └── ...
├── pages/
│   ├── Index.tsx        # Landing page
│   ├── DemoIndex.tsx    # Demo profile selection
│   ├── DemoDashboard.tsx # Demo dashboard
│   └── NotFound.tsx
├── services/
│   ├── authService.ts   # Auth API calls
│   ├── uploadService.ts # Upload API calls
│   ├── insightsService.ts # Insights API calls
│   ├── analysisService.ts # Analysis jobs API calls
│   └── demoService.ts   # Demo mode API calls
├── config/
│   ├── api.ts           # API configuration
│   └── demo.ts          # Demo mode configuration
├── hooks/
│   ├── use-toast.ts
│   └── use-mobile.tsx
└── lib/
    └── utils.ts
```

### Components Analysis

#### ✅ Completed Components

1. **AuthForm.tsx** (97 lines)
   - Email input
   - "Send Magic Link" button
   - ⚠️ Issue: Backend doesn't support magic links!
   - Uses `authService.requestMagicLink()` which calls non-existent endpoint

2. **Dashboard.tsx** (203 lines)
   - Mock data visualization
   - Sample charts
   - ⚠️ Issue: Not connected to real API!
   - Hard-coded sample data

3. **UploadWizard.tsx** (215 lines)
   - Multi-step file upload
   - File type selection
   - ⚠️ Issue: Calls non-existent `/uploads` endpoint!

4. **DemoIndex.tsx** (235 lines)
   - ✅ Complete: Profile selection for 3 demo users
   - Beautiful UI with Shadcn components

5. **DemoDashboard.tsx** (305 lines)
   - ✅ Complete: Read-only dashboard for demo users
   - Connects to Lambda demo API

#### ❌ Missing Components

1. **RealDashboard.tsx**
   - Authenticated user dashboard
   - Connect to `/api/v1/insights/dashboard`
   - Real-time glucose chart
   - Sleep, meals, activities timeline

2. **ProfileSettings.tsx**
   - User profile management
   - Target glucose range settings
   - CGM type selection
   - Notification preferences

3. **HealthMetricsForm.tsx**
   - HbA1c logging
   - Medication management
   - Insulin tracking
   - Blood pressure tracking

4. **DataExplorer.tsx**
   - Historical data visualization
   - Date range picker
   - Export to CSV

5. **InsightsDetail.tsx**
   - Detailed correlation view
   - Pattern explanation
   - PCMCI graph visualization

### Service Layer Analysis

#### ✅ `authService.ts`
```typescript
requestMagicLink(email) → POST /auth/request-magic-link ❌ Missing
verifyMagicLink(token) → POST /auth/verify-token ❌ Missing
```

#### ❌ `uploadService.ts`
```typescript
uploadFile(file) → POST /uploads ❌ Missing
getUploadHistory() → GET /uploads ❌ Missing
```

#### ⚠️ `insightsService.ts`
```typescript
getInsights() → GET /insights/{user_id} ⚠️ Uses MOCK_USER_ID
```

#### ❌ `analysisService.ts`
```typescript
startAnalysis() → POST /analysis/start ❌ Missing
getJobStatus(id) → GET /analysis/{id}/status ❌ Missing
```

---

## Critical Gaps & Issues

### 1. Authentication Inconsistency 🔴 CRITICAL

**Problem:** Mixed authentication patterns cause security and UX issues

**Evidence:**
```python
# Some routes use proper JWT auth
@router.post("/readings", dependencies=[Depends(get_current_user)])

# Others use hardcoded MOCK_USER_ID
MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
@router.post("/sleep")
async def create_sleep(sleep: SleepDataCreate, db: AsyncSession = Depends(get_db)):
    db_sleep = SleepData(user_id=MOCK_USER_ID, **sleep.model_dump())
```

**Affected Routes:**
- `/api/v1/sleep` (all endpoints)
- `/api/v1/meals` (all endpoints)
- `/api/v1/activities` (all endpoints)
- `/api/v1/insights` (correlations, patterns, dashboard)

**Impact:**
- All users share the same sleep/meal/activity data!
- Security vulnerability
- Cannot deploy to production

**Solution:**
1. Add `current_user: User = Depends(get_current_user)` to all routes
2. Remove all `MOCK_USER_ID` references
3. Update database queries to filter by `current_user.id`

---

### 2. Missing GET Endpoints 🔴 CRITICAL

**Problem:** Data can be created but never retrieved

**Affected Endpoints:**
- `/api/v1/sleep` - No GET endpoint
- `/api/v1/meals` - No GET endpoint
- `/api/v1/activities` - No GET endpoint

**Evidence:**
```python
# backend/app/routes/sleep.py
@router.post("", response_model=SleepDataResponse, status_code=201)
async def create_sleep_data(...):  # ✅ Exists
    ...

# ❌ Missing GET endpoint!
# @router.get("", response_model=List[SleepDataResponse])
# async def get_sleep_data(...):
#     ...
```

**Impact:**
- Users can log sleep but can't view their history
- Dashboard can't display sleep data
- ML pipeline can access data, but frontend can't

**Solution:**
```python
@router.get("", response_model=List[SleepDataResponse])
async def get_sleep_data(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(SleepData).where(SleepData.user_id == current_user.id)
    if start:
        query = query.where(SleepData.start_time >= start)
    if end:
        query = query.where(SleepData.end_time <= end)
    query = query.order_by(SleepData.start_time.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
```

---

### 3. Frontend/Backend Auth Mismatch 🟠 HIGH

**Problem:** Frontend expects magic link, backend has email/password

**Frontend Code:**
```typescript
// src/components/AuthForm.tsx
const handleSubmit = async () => {
  await authService.requestMagicLink(email);  // ❌ Endpoint doesn't exist
  setIsLoading(false);
};
```

**Backend Reality:**
```python
# backend/app/routes/auth.py
@router.post("/login")  # ✅ Exists (email + password)
async def login(credentials: LoginRequest):
    ...

# ❌ Missing magic link endpoints
# @router.post("/request-magic-link")
# @router.post("/verify-token")
```

**Solutions (choose one):**

**Option A: Keep email/password, update frontend**
```typescript
// Update AuthForm.tsx to use email + password
const handleSubmit = async () => {
  await authService.login(email, password);  // Use existing endpoint
};
```

**Option B: Implement magic links (requires email service)**
```python
# Add SendGrid/AWS SES integration
@router.post("/request-magic-link")
async def request_magic_link(email: str):
    token = generate_magic_link_token(email)
    await send_email(email, f"https://app.com/verify?token={token}")
    return {"message": "Magic link sent"}
```

---

### 4. Missing File Upload Implementation 🟠 HIGH

**Problem:** Frontend has upload wizard, backend has no upload endpoint

**Frontend:**
```typescript
// src/services/uploadService.ts
async uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${this.baseUrl}/api/v1/uploads`, {  // ❌ Doesn't exist!
    method: 'POST',
    body: formData,
  });
}
```

**Backend:** No `/uploads` route exists at all!

**Solution:** Implement file upload with CSV/JSON parsing

```python
# backend/app/routes/uploads.py
from fastapi import UploadFile, File
import pandas as pd

@router.post("/uploads")
async def upload_file(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Parse CSV/JSON
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file.file)
    elif file.filename.endswith('.json'):
        df = pd.read_json(file.file)
    else:
        raise HTTPException(400, "Unsupported file type")

    # Map to appropriate model
    if data_type == 'glucose':
        records = [GlucoseReading(user_id=current_user.id, **row) for row in df.to_dict('records')]
    # ...

    db.add_all(records)
    await db.commit()

    return {"status": "success", "records_created": len(records)}
```

---

### 5. Dashboard Not Connected to Real Data 🟡 MEDIUM

**Problem:** Dashboard component uses hard-coded mock data

**Current Implementation:**
```typescript
// src/components/Dashboard.tsx
const Dashboard = () => {
  // ❌ Hard-coded mock data
  const sampleData = [
    { time: '00:00', glucose: 95, sleep: 'deep' },
    { time: '01:00', glucose: 92, sleep: 'deep' },
    // ...
  ];

  return (
    <LineChart data={sampleData}>  {/* ❌ Not real user data! */}
      <Line dataKey="glucose" stroke="#8884d8" />
    </LineChart>
  );
};
```

**Solution:** Connect to real API endpoints

```typescript
const Dashboard = () => {
  const [glucoseData, setGlucoseData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('/api/v1/glucose/readings', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setGlucoseData(data);
      setLoading(false);
    };
    fetchData();
  }, []);

  if (loading) return <Skeleton />;

  return (
    <LineChart data={glucoseData}>
      <Line dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
};
```

---

### 6. No Database Migrations (Alembic) 🟡 MEDIUM

**Problem:** Manual SQL migrations, no version control

**Current State:**
```bash
backend/migrations/
└── 001_initial_schema.sql  # Manual SQL file
```

**Risks:**
- Schema changes not tracked
- No rollback capability
- Team members can get out of sync
- Production migrations risky

**Solution:** Configure Alembic

```bash
# Install Alembic
pip install alembic

# Initialize
cd backend
alembic init alembic

# Configure alembic/env.py
target_metadata = Base.metadata

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply
alembic upgrade head
```

---

### 7. Missing Tests 🟡 MEDIUM

**Current State:** Zero tests!

```bash
backend/tests/  # ❌ Doesn't exist
src/__tests__/  # ❌ Doesn't exist
```

**Impact:**
- No confidence in refactoring
- Bugs slip into production
- Hard to onboard new developers

**Solution:** Add pytest + React Testing Library

```python
# backend/tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "secure123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert "id" in response.json()
```

```typescript
// src/components/__tests__/AuthForm.test.tsx
import { render, screen } from '@testing-library/react';
import { AuthForm } from '../AuthForm';

test('renders email input', () => {
  render(<AuthForm />);
  expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument();
});
```

---

## Refactoring Recommendations

### High Priority

#### 1. Unify Authentication (2-3 days)

**Files to modify:**
- `backend/app/routes/sleep.py`
- `backend/app/routes/meals.py`
- `backend/app/routes/activities.py`
- `backend/app/routes/insights.py`

**Changes:**
```python
# Before
MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
@router.post("")
async def create_sleep(sleep: SleepDataCreate, db: AsyncSession = Depends(get_db)):
    db_sleep = SleepData(user_id=MOCK_USER_ID, **sleep.model_dump())

# After
@router.post("")
async def create_sleep(
    sleep: SleepDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Add auth
):
    db_sleep = SleepData(user_id=current_user.id, **sleep.model_dump())  # ✅ Use current user
```

#### 2. Add Missing GET Endpoints (1-2 days)

**Files to create:**
Add to existing route files:
- `backend/app/routes/sleep.py` - Add `get_sleep_data()`
- `backend/app/routes/meals.py` - Add `get_meals()`
- `backend/app/routes/activities.py` - Add `get_activities()`

**Template:**
```python
@router.get("", response_model=List[ModelResponse])
async def get_resources(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Model).where(Model.user_id == current_user.id)
    if start:
        query = query.where(Model.timestamp >= start)
    if end:
        query = query.where(Model.timestamp <= end)
    query = query.order_by(Model.timestamp.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
```

#### 3. Fix Frontend Auth (1 day)

**Option A: Update to email/password**
```typescript
// src/components/AuthForm.tsx
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');  // ✅ Add password field

const handleSubmit = async () => {
  await authService.login(email, password);  // ✅ Use existing endpoint
};
```

```typescript
// src/services/authService.ts
async login(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return await response.json();
}
```

#### 4. Implement File Upload Endpoint (2-3 days)

**Create:**
- `backend/app/routes/uploads.py`
- `backend/app/schemas/uploads.py`
- `backend/app/services/parser_service.py`

**Features:**
- CSV/JSON parsing
- Validation
- Async background processing with Celery
- Progress tracking

### Medium Priority

#### 5. Add Alembic Migrations (1 day)

```bash
# Setup
pip install alembic
alembic init alembic

# Configure
# Edit alembic/env.py to use Base.metadata

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply
alembic upgrade head
```

#### 6. Add Comprehensive Logging (1 day)

```python
# backend/app/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger("glucolens")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler("logs/app.log", maxBytes=10485760, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
```

#### 7. Implement Rate Limiting (1 day)

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# In main.py startup
await FastAPILimiter.init(redis)

# On routes
@router.post("/login", dependencies=[Depends(RateLimiter(times=5, minutes=1))])
async def login(...):
    ...
```

### Low Priority (Nice to Have)

#### 8. Add Frontend Error Boundaries (0.5 days)

```typescript
// src/components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong. Please refresh.</div>;
    }
    return this.props.children;
  }
}
```

#### 9. Add Loading Skeletons (1 day)

```typescript
// src/components/DashboardSkeleton.tsx
export const DashboardSkeleton = () => (
  <div className="space-y-4">
    <Skeleton className="h-64 w-full" />
    <Skeleton className="h-32 w-full" />
  </div>
);
```

#### 10. Add API Response Caching (1 day)

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@router.get("/dashboard")
@cache(expire=300)  # Cache for 5 minutes
async def get_dashboard(...):
    ...
```

---

## Dummy Data Strategy

### Comprehensive Dummy Data Requirements

To properly showcase all features, we need realistic synthetic data for:

1. **User Profiles** (3 personas)
2. **Glucose Readings** (CGM data every 5 min)
3. **Sleep Data** (daily records)
4. **Meals** (3-4 per day with macros)
5. **Activities** (2-5 per week)
6. **Health Metrics** (HbA1c, medications, insulin, BP)
7. **ML Insights** (pre-computed correlations, patterns)

### Enhanced Demo User Profiles

Expand the existing 3 demo users to cover all features:

**Alice Thompson - "The Well-Controlled Type 1"**
```python
{
    "id": "11111111-1111-1111-1111-111111111111",
    "email": "alice@demo.glucolens.com",
    "full_name": "Alice Thompson",
    "age": 34,
    "diabetes_type": "type1",
    "diagnosis_date": "2015-03-12",
    "insulin_dependent": True,
    "cgm_type": "dexcom_g7",
    "height_cm": 165,
    "weight_kg": 62,
    "gender": "female",
    "target_glucose_min": 70,
    "target_glucose_max": 180,

    # Data characteristics
    "base_glucose": 100,
    "variability": 15,
    "time_in_range": 85,
    "avg_sleep_hours": 7.5,
    "exercise_frequency": "moderate",  # 3-4x/week
    "meal_regularity": "high",

    # Medications
    "medications": [
        {"name": "Lantus", "type": "basal_insulin", "dosage": "20 units", "frequency": "daily"},
        {"name": "Humalog", "type": "bolus_insulin", "dosage": "varies", "frequency": "with_meals"}
    ],

    # Recent HbA1c
    "hba1c_values": [5.8, 5.9, 5.7, 5.8],  # Last 4 tests
}
```

**Bob Martinez - "The Stressed Professional with Type 2"**
```python
{
    "id": "22222222-2222-2222-2222-222222222222",
    "email": "bob@demo.glucolens.com",
    "full_name": "Bob Martinez",
    "age": 45,
    "diabetes_type": "type2",
    "diagnosis_date": "2020-08-15",
    "insulin_dependent": False,
    "cgm_type": "freestyle_libre_3",
    "height_cm": 178,
    "weight_kg": 92,
    "gender": "male",
    "target_glucose_min": 70,
    "target_glucose_max": 180,

    # Data characteristics
    "base_glucose": 140,
    "variability": 30,
    "time_in_range": 60,
    "avg_sleep_hours": 6.0,
    "exercise_frequency": "low",  # 1-2x/week
    "meal_regularity": "low",  # Irregular eating

    # Medications
    "medications": [
        {"name": "Metformin", "type": "oral", "dosage": "1000mg", "frequency": "twice_daily"},
        {"name": "Jardiance", "type": "oral", "dosage": "10mg", "frequency": "daily"}
    ],

    # Recent HbA1c
    "hba1c_values": [7.2, 7.0, 7.3, 7.1],

    # Additional health metrics
    "blood_pressure_avg": [135, 85],  # Slightly elevated
}
```

**Carol Chen - "The Athletic Type 1"**
```python
{
    "id": "33333333-3333-3333-3333-333333333333",
    "email": "carol@demo.glucolens.com",
    "full_name": "Carol Chen",
    "age": 28,
    "diabetes_type": "type1",
    "diagnosis_date": "2010-05-20",
    "insulin_dependent": True,
    "cgm_type": "dexcom_g7",
    "height_cm": 168,
    "weight_kg": 58,
    "gender": "female",
    "target_glucose_min": 70,
    "target_glucose_max": 180,

    # Data characteristics
    "base_glucose": 115,
    "variability": 20,
    "time_in_range": 75,
    "avg_sleep_hours": 8.0,
    "exercise_frequency": "very_high",  # 5-6x/week
    "meal_regularity": "high",

    # Medications
    "medications": [
        {"name": "Tresiba", "type": "basal_insulin", "dosage": "18 units", "frequency": "daily"},
        {"name": "Fiasp", "type": "bolus_insulin", "dosage": "varies", "frequency": "with_meals"}
    ],

    # Recent HbA1c
    "hba1c_values": [6.3, 6.2, 6.4, 6.1],
}
```

### Data Generation Script Enhancement

Update `backend/scripts/generate_demo_users.py` to include:

#### 1. Health Metrics Generation

```python
async def generate_health_metrics(session: AsyncSession, user_id: UUID, profile: dict):
    """Generate comprehensive health metrics for a user."""

    # HbA1c tests (quarterly for 1 year)
    hba1c_dates = [
        datetime.now(UTC) - timedelta(days=270),
        datetime.now(UTC) - timedelta(days=180),
        datetime.now(UTC) - timedelta(days=90),
        datetime.now(UTC),
    ]

    for i, test_date in enumerate(hba1c_dates):
        hba1c = HbA1c(
            user_id=user_id,
            test_date=test_date.date(),
            value=profile["hba1c_values"][i],
            notes=f"Quarterly test {i+1}"
        )
        session.add(hba1c)

    # Medications
    for med in profile["medications"]:
        medication = Medication(
            user_id=user_id,
            name=med["name"],
            medication_type=med["type"],
            dosage=med["dosage"],
            frequency=med["frequency"],
            start_date=(datetime.now(UTC) - timedelta(days=365)).date(),
            active=True
        )
        session.add(medication)

    # Blood pressure (if applicable)
    if "blood_pressure_avg" in profile:
        for day_offset in range(0, 90, 7):  # Weekly readings
            bp_date = datetime.now(UTC) - timedelta(days=day_offset)
            bp = BloodPressure(
                user_id=user_id,
                timestamp=bp_date,
                systolic=profile["blood_pressure_avg"][0] + random.randint(-10, 10),
                diastolic=profile["blood_pressure_avg"][1] + random.randint(-5, 5),
                heart_rate=random.randint(60, 80)
            )
            session.add(bp)

    # Body metrics (weekly)
    for week in range(12):  # 12 weeks
        metric_date = datetime.now(UTC) - timedelta(weeks=week)
        weight_change = random.uniform(-0.5, 0.5) * week  # Gradual weight change
        metrics = BodyMetrics(
            user_id=user_id,
            timestamp=metric_date,
            weight_kg=profile["weight_kg"] + weight_change,
            height_cm=profile["height_cm"],
            bmi=round((profile["weight_kg"] + weight_change) / ((profile["height_cm"]/100) ** 2), 1)
        )
        session.add(metrics)

    # Insulin doses (if insulin dependent)
    if profile.get("insulin_dependent"):
        await generate_insulin_doses(session, user_id, profile)
```

#### 2. Insulin Dose Generation

```python
async def generate_insulin_doses(session: AsyncSession, user_id: UUID, profile: dict):
    """Generate realistic insulin doses based on meals and glucose."""

    # Get meals for dosing
    meals_query = select(Meal).where(Meal.user_id == user_id).order_by(Meal.timestamp)
    result = await session.execute(meals_query)
    meals = result.scalars().all()

    for meal in meals:
        # Calculate bolus insulin (1 unit per 10g carbs as rough estimate)
        carbs = meal.carbs_grams or 40
        bolus_dose = round(carbs / 10, 1)

        # Add some variation
        bolus_dose += random.uniform(-1, 1)
        bolus_dose = max(1, bolus_dose)  # At least 1 unit

        insulin = Insulin(
            user_id=user_id,
            timestamp=meal.timestamp,
            dose_units=bolus_dose,
            insulin_type="bolus",
            notes=f"Meal bolus for {carbs}g carbs"
        )
        session.add(insulin)

    # Add basal insulin (once daily)
    basal_dose = 20 if profile["age"] < 40 else 24
    for day_offset in range(90):
        dose_time = (datetime.now(UTC) - timedelta(days=day_offset)).replace(hour=22, minute=0)
        basal = Insulin(
            user_id=user_id,
            timestamp=dose_time,
            dose_units=basal_dose + random.uniform(-2, 2),
            insulin_type="basal",
            notes="Nightly basal insulin"
        )
        session.add(basal)
```

#### 3. Enhanced Meal Generation

```python
MEAL_TYPES = {
    "breakfast": {
        "time_range": (7, 9),
        "examples": [
            {"name": "Oatmeal with berries", "carbs": 45, "protein": 8, "fat": 5},
            {"name": "Whole wheat toast with eggs", "carbs": 30, "protein": 18, "fat": 12},
            {"name": "Greek yogurt with granola", "carbs": 35, "protein": 15, "fat": 8},
            {"name": "Smoothie bowl", "carbs": 40, "protein": 10, "fat": 6},
        ]
    },
    "lunch": {
        "time_range": (12, 14),
        "examples": [
            {"name": "Grilled chicken salad", "carbs": 25, "protein": 35, "fat": 15},
            {"name": "Turkey sandwich", "carbs": 40, "protein": 25, "fat": 10},
            {"name": "Quinoa bowl", "carbs": 45, "protein": 20, "fat": 12},
            {"name": "Vegetable stir-fry with rice", "carbs": 55, "protein": 15, "fat": 8},
        ]
    },
    "dinner": {
        "time_range": (18, 20),
        "examples": [
            {"name": "Salmon with vegetables", "carbs": 30, "protein": 40, "fat": 20},
            {"name": "Pasta with marinara", "carbs": 60, "protein": 15, "fat": 10},
            {"name": "Chicken stir-fry", "carbs": 45, "protein": 35, "fat": 12},
            {"name": "Beef tacos", "carbs": 35, "protein": 30, "fat": 18},
        ]
    },
    "snack": {
        "time_range": (15, 17),
        "examples": [
            {"name": "Apple with almonds", "carbs": 20, "protein": 5, "fat": 8},
            {"name": "Protein bar", "carbs": 25, "protein": 15, "fat": 7},
            {"name": "Crackers with cheese", "carbs": 18, "protein": 8, "fat": 10},
        ]
    }
}

async def generate_meals_data(session: AsyncSession, user_id: UUID, profile: dict, days: int = 90):
    """Generate realistic meal data."""

    for day_offset in range(days):
        date = datetime.now(UTC) - timedelta(days=day_offset)

        # Breakfast (always)
        meal_time = date.replace(hour=random.randint(7, 9), minute=random.randint(0, 59))
        breakfast = random.choice(MEAL_TYPES["breakfast"]["examples"])
        session.add(Meal(
            user_id=user_id,
            timestamp=meal_time,
            meal_type="breakfast",
            description=breakfast["name"],
            carbs_grams=breakfast["carbs"] + random.randint(-5, 5),
            protein_grams=breakfast["protein"] + random.randint(-2, 2),
            fat_grams=breakfast["fat"] + random.randint(-2, 2),
            calories=calculate_calories(breakfast)
        ))

        # Lunch (always)
        meal_time = date.replace(hour=random.randint(12, 14), minute=random.randint(0, 59))
        lunch = random.choice(MEAL_TYPES["lunch"]["examples"])
        session.add(Meal(
            user_id=user_id,
            timestamp=meal_time,
            meal_type="lunch",
            description=lunch["name"],
            carbs_grams=lunch["carbs"] + random.randint(-5, 5),
            protein_grams=lunch["protein"] + random.randint(-3, 3),
            fat_grams=lunch["fat"] + random.randint(-2, 2),
            calories=calculate_calories(lunch)
        ))

        # Snack (70% of days for active users, 30% for others)
        if random.random() < (0.7 if profile["exercise_frequency"] in ["high", "very_high"] else 0.3):
            meal_time = date.replace(hour=random.randint(15, 17), minute=random.randint(0, 59))
            snack = random.choice(MEAL_TYPES["snack"]["examples"])
            session.add(Meal(
                user_id=user_id,
                timestamp=meal_time,
                meal_type="snack",
                description=snack["name"],
                carbs_grams=snack["carbs"],
                protein_grams=snack["protein"],
                fat_grams=snack["fat"],
                calories=calculate_calories(snack)
            ))

        # Dinner (always)
        meal_time = date.replace(hour=random.randint(18, 20), minute=random.randint(0, 59))
        dinner = random.choice(MEAL_TYPES["dinner"]["examples"])
        session.add(Meal(
            user_id=user_id,
            timestamp=meal_time,
            meal_type="dinner",
            description=dinner["name"],
            carbs_grams=dinner["carbs"] + random.randint(-5, 5),
            protein_grams=dinner["protein"] + random.randint(-5, 5),
            fat_grams=dinner["fat"] + random.randint(-3, 3),
            calories=calculate_calories(dinner)
        ))

def calculate_calories(meal: dict) -> int:
    """Calculate calories from macros (4 cal/g for carbs+protein, 9 cal/g for fat)."""
    return (meal["carbs"] * 4) + (meal["protein"] * 4) + (meal["fat"] * 9)
```

#### 4. Enhanced Activity Generation

```python
ACTIVITY_TYPES = {
    "very_high": [
        {"type": "running", "duration_range": (30, 60), "intensity": "high"},
        {"type": "cycling", "duration_range": (45, 90), "intensity": "moderate"},
        {"type": "swimming", "duration_range": (30, 45), "intensity": "high"},
        {"type": "weight_training", "duration_range": (45, 60), "intensity": "moderate"},
        {"type": "hiit", "duration_range": (20, 30), "intensity": "high"},
    ],
    "moderate": [
        {"type": "walking", "duration_range": (30, 60), "intensity": "low"},
        {"type": "yoga", "duration_range": (45, 60), "intensity": "low"},
        {"type": "cycling", "duration_range": (30, 45), "intensity": "moderate"},
    ],
    "low": [
        {"type": "walking", "duration_range": (20, 30), "intensity": "low"},
        {"type": "stretching", "duration_range": (15, 20), "intensity": "low"},
    ]
}

async def generate_activities_data(session: AsyncSession, user_id: UUID, profile: dict, days: int = 90):
    """Generate realistic activity data based on exercise frequency."""

    # Map frequency to activities per week
    frequency_map = {
        "very_high": 6,  # 6 days/week
        "high": 5,       # 5 days/week
        "moderate": 3,   # 3 days/week
        "low": 1,        # 1 day/week
    }

    activities_per_week = frequency_map.get(profile["exercise_frequency"], 2)
    activity_pool = ACTIVITY_TYPES.get(profile["exercise_frequency"], ACTIVITY_TYPES["moderate"])

    for week in range(days // 7):
        # Randomly select days of the week for activities
        activity_days = random.sample(range(7), activities_per_week)

        for day_in_week in activity_days:
            day_offset = week * 7 + day_in_week
            if day_offset >= days:
                continue

            activity_date = datetime.now(UTC) - timedelta(days=day_offset)

            # Select random activity type
            activity_template = random.choice(activity_pool)
            duration = random.randint(*activity_template["duration_range"])

            # Set time (morning or evening based on profile)
            if profile["exercise_frequency"] in ["very_high", "high"]:
                # Athletes prefer morning workouts
                hour = random.randint(6, 8) if random.random() < 0.7 else random.randint(17, 19)
            else:
                # Others prefer evening
                hour = random.randint(17, 20)

            activity_time = activity_date.replace(hour=hour, minute=random.randint(0, 59))

            activity = Activity(
                user_id=user_id,
                timestamp=activity_time,
                activity_type=activity_template["type"],
                duration_minutes=duration,
                intensity=activity_template["intensity"],
                calories_burned=estimate_calories_burned(activity_template, duration, profile),
                notes=f"{duration} min {activity_template['type']}"
            )
            session.add(activity)

def estimate_calories_burned(activity: dict, duration: int, profile: dict) -> int:
    """Estimate calories burned based on activity, duration, and user profile."""
    # MET (Metabolic Equivalent) values
    met_values = {
        "running": 10,
        "cycling": 8,
        "swimming": 9,
        "weight_training": 6,
        "hiit": 12,
        "walking": 3.5,
        "yoga": 2.5,
        "stretching": 2,
    }

    met = met_values.get(activity["type"], 5)
    weight_kg = profile["weight_kg"]

    # Calories = MET * weight_kg * hours
    calories = met * weight_kg * (duration / 60)

    return int(calories)
```

### ML Insights Pre-computation

After generating all data, run ML pipelines to pre-compute insights:

```python
async def precompute_ml_insights(session: AsyncSession, user_id: UUID):
    """Run ML pipelines to generate insights for demo user."""

    # 1. Run correlation analysis
    from app.tasks_ml import analyze_correlations_task
    analyze_correlations_task.delay(str(user_id))

    # 2. Run pattern discovery
    from app.tasks_ml import discover_patterns_task
    discover_patterns_task.delay(str(user_id))

    # 3. Run PCMCI (if enough data)
    glucose_count = await session.execute(
        select(func.count()).select_from(GlucoseReading).where(GlucoseReading.user_id == user_id)
    )
    if glucose_count.scalar() >= 1000:  # Minimum for PCMCI
        from app.tasks_ml import run_pcmci_analysis_task
        run_pcmci_analysis_task.delay(str(user_id))

    # 4. Run STUMPY pattern detection
    from app.tasks_ml import run_stumpy_analysis_task
    run_stumpy_analysis_task.delay(str(user_id))

    print(f"✅ ML insights queued for user {user_id}")
```

### Complete Data Generation Flow

```python
async def generate_complete_demo_data():
    """Generate all demo data for 3 users."""

    async with async_session_maker() as session:
        for user_profile in DEMO_USERS:
            print(f"\n{'='*60}")
            print(f"Generating data for {user_profile['full_name']}")
            print(f"{'='*60}")

            # 1. Create user
            user = await create_demo_user(session, user_profile)
            print(f"✅ Created user: {user.email}")

            # 2. Generate glucose data (25,920 readings for 90 days)
            await generate_glucose_data(session, user.id, user_profile, days=90)
            print(f"✅ Generated 25,920 glucose readings")

            # 3. Generate sleep data (90 records)
            await generate_sleep_data(session, user.id, user_profile, days=90)
            print(f"✅ Generated 90 sleep records")

            # 4. Generate meals (270-360 meals)
            await generate_meals_data(session, user.id, user_profile, days=90)
            print(f"✅ Generated meals data")

            # 5. Generate activities (based on frequency)
            await generate_activities_data(session, user.id, user_profile, days=90)
            print(f"✅ Generated activities data")

            # 6. Generate health metrics
            await generate_health_metrics(session, user.id, user_profile)
            print(f"✅ Generated health metrics (HbA1c, medications, BP, body metrics)")

            # 7. Commit all data
            await session.commit()
            print(f"✅ All data committed to database")

            # 8. Pre-compute ML insights
            await precompute_ml_insights(session, user.id)
            print(f"✅ ML insights computation queued")

        print(f"\n{'='*60}")
        print(f"✅ Demo data generation complete!")
        print(f"{'='*60}")
        print(f"\nDemo users:")
        for user in DEMO_USERS:
            print(f"  - {user['full_name']}: {user['email']}")
```

---

## Free-Tier Deployment Options

### Option 1: Railway.app (RECOMMENDED) ⭐

**Free Tier:**
- $5 free credit per month (sufficient for demo)
- Easy PostgreSQL + Redis setup
- GitHub integration (auto-deploy)
- Environment variables management
- Decent performance

**Setup:**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add PostgreSQL
railway add --plugin postgresql

# 5. Add Redis
railway add --plugin redis

# 6. Deploy
railway up
```

**Costs (after free tier):**
- PostgreSQL: ~$5/month
- Redis: ~$2/month
- Web service: ~$5/month
- **Total: ~$12/month** (first month free)

**Pros:**
- ✅ Easiest setup
- ✅ Automatic SSL
- ✅ Built-in monitoring
- ✅ PostgreSQL + Redis included

**Cons:**
- ❌ Free tier limited to $5 credit/month
- ❌ Sleeps after inactivity

---

### Option 2: Render.com

**Free Tier:**
- Free PostgreSQL (90-day expiry, then $7/month)
- Free Redis (25MB)
- Free web service (512MB RAM, sleeps after 15min)
- Auto-deploy from GitHub

**Setup:**
```yaml
# render.yaml
services:
  - type: web
    name: glucolens-api
    env: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: glucolens-db
          property: connectionString
      - key: REDIS_URL
        fromDatabase:
          name: glucolens-redis
          property: connectionString

databases:
  - name: glucolens-db
    databaseName: glucolens
    user: glucolens

  - name: glucolens-redis
    type: redis
```

**Pros:**
- ✅ True free tier (with limits)
- ✅ PostgreSQL + Redis free
- ✅ Auto-deploy from GitHub
- ✅ Good documentation

**Cons:**
- ❌ Service sleeps after 15 min inactivity
- ❌ PostgreSQL expires after 90 days on free tier
- ❌ Slow cold starts

---

### Option 3: Fly.io

**Free Tier:**
- 3 shared-cpu VMs with 256MB RAM
- 3GB persistent volume storage
- 160GB outbound data transfer

**Setup:**
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch

# Add Postgres
fly postgres create

# Add Redis
fly redis create

# Deploy
fly deploy
```

**fly.toml:**
```toml
app = "glucolens"

[build]
  dockerfile = "Dockerfile"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

**Pros:**
- ✅ Good free tier
- ✅ No sleep on inactivity
- ✅ Fast performance

**Cons:**
- ❌ More complex setup
- ❌ Need to manage Dockerfile

---

### Option 4: Vercel (Frontend) + Supabase (Backend)

**Free Tier:**
- Vercel: Unlimited deployments, 100GB bandwidth
- Supabase: 500MB database, 1GB file storage, 2GB bandwidth

**Architecture:**
```
Vercel (React Frontend) → Supabase (PostgreSQL + Auth + Storage)
```

**Limitations:**
- ❌ No custom backend (FastAPI won't work)
- ❌ Would need to rewrite backend as Supabase Edge Functions
- ❌ ML services (PCMCI, STUMPY) won't work

**Verdict:** ❌ Not suitable for this project

---

### Option 5: AWS Free Tier (Lambda + RDS)

Already implemented! (See `QUICKSTART_DEMO.md`)

**Free Tier:**
- Lambda: 1M requests/month
- RDS: Not free (Aurora Serverless ~$35/month minimum)
- S3: 5GB storage
- CloudFront: 50GB data transfer

**Costs:**
- Lambda: Free (within limits)
- Aurora Serverless: **$35-50/month** (NOT FREE)
- S3: ~$0.50/month
- **Total: ~$35-50/month**

**Verdict:** ⚠️ Good for production, but NOT free tier

---

### Option 6: Google Cloud Run + Cloud SQL (Free Tier)

**Free Tier:**
- Cloud Run: 2M requests/month
- Cloud SQL: **NOT FREE** ($10+/month)
- Cloud Storage: 5GB

**Verdict:** ⚠️ Similar cost to AWS (~$10-15/month)

---

### Recommendation Matrix

| Platform | Complexity | True Free? | Best For | Monthly Cost (After Free) |
|----------|-----------|------------|----------|---------------------------|
| **Railway.app** | ⭐ Easy | ❌ $5 credit | Quick demo | $12 |
| **Render.com** | ⭐⭐ Easy | ✅ Yes (90 days) | Short-term demo | $7 (after 90 days) |
| **Fly.io** | ⭐⭐⭐ Medium | ✅ Yes (with limits) | Long-term free | $0 (within limits) |
| **AWS Lambda** | ⭐⭐⭐⭐ Hard | ❌ No | Production | $35-50 |
| **Vercel + Supabase** | ⭐⭐ Easy | ✅ Yes | Simple apps only | $0 (not suitable) |

---

### 🏆 FINAL RECOMMENDATION: Render.com

**Reasoning:**
1. ✅ **Truly free for 90 days** - PostgreSQL + Redis + Web service
2. ✅ **Easy setup** - Just connect GitHub, add render.yaml
3. ✅ **No credit card required** (for initial 90 days)
4. ✅ **Auto-deploy** from GitHub
5. ✅ **Good for demo purposes**
6. ⚠️ Service sleeps after 15 min (acceptable for demo)

**After 90 days:**
- Either pay $7/month for PostgreSQL
- Or migrate to Fly.io free tier
- Or deploy to production AWS

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1)

**Priority 1: Authentication Unification**
- [ ] Update sleep.py - Add `get_current_user` dependency
- [ ] Update meals.py - Add `get_current_user` dependency
- [ ] Update activities.py - Add `get_current_user` dependency
- [ ] Update insights.py - Add `get_current_user` dependency
- [ ] Remove all `MOCK_USER_ID` references
- [ ] Test all endpoints with JWT tokens

**Priority 2: Add Missing GET Endpoints**
- [ ] Add `GET /api/v1/sleep` endpoint
- [ ] Add `GET /api/v1/meals` endpoint
- [ ] Add `GET /api/v1/activities` endpoint
- [ ] Add query parameters (start, end, limit)
- [ ] Test with Postman/curl

**Priority 3: Fix Frontend Auth**
- [ ] Update AuthForm.tsx - Add password field
- [ ] Update authService.ts - Use `/api/v1/auth/login`
- [ ] Remove magic link references
- [ ] Test login flow end-to-end

**Estimated Time:** 3-4 days
**Outcome:** Core functionality working with proper auth

---

### Phase 2: Enhanced Data & Features (Week 2)

**Priority 1: Enhanced Dummy Data**
- [ ] Update generate_demo_users.py
- [ ] Add health metrics generation
- [ ] Add insulin dose generation
- [ ] Add enhanced meal generation
- [ ] Add realistic activity generation
- [ ] Run ML pipeline after generation
- [ ] Verify all data in database

**Priority 2: Implement File Upload**
- [ ] Create uploads.py route
- [ ] Implement CSV parser
- [ ] Implement JSON parser
- [ ] Add bulk data validation
- [ ] Test with sample files
- [ ] Update frontend UploadWizard

**Priority 3: Connect Dashboard to Real Data**
- [ ] Create RealDashboard.tsx component
- [ ] Fetch glucose data from API
- [ ] Fetch sleep data from API
- [ ] Fetch meals data from API
- [ ] Fetch activities from API
- [ ] Fetch insights from API
- [ ] Add loading states
- [ ] Add error handling

**Estimated Time:** 5-7 days
**Outcome:** Full data visualization with realistic dummy data

---

### Phase 3: Polish & Deploy (Week 3)

**Priority 1: Testing**
- [ ] Set up pytest
- [ ] Write auth tests
- [ ] Write endpoint tests
- [ ] Set up frontend tests
- [ ] Write component tests
- [ ] Achieve >50% coverage

**Priority 2: Documentation**
- [ ] Update API documentation
- [ ] Add inline code comments
- [ ] Update README with new features
- [ ] Create user guide
- [ ] Create deployment guide for Render

**Priority 3: Deployment**
- [ ] Create render.yaml
- [ ] Set up Render.com account
- [ ] Connect GitHub repository
- [ ] Configure environment variables
- [ ] Deploy to Render
- [ ] Test deployed application
- [ ] Set up monitoring

**Estimated Time:** 5-7 days
**Outcome:** Production-ready application deployed on free tier

---

### Phase 4: Nice-to-Haves (Week 4+)

**Optional Enhancements:**
- [ ] Add Alembic migrations
- [ ] Implement rate limiting
- [ ] Add comprehensive logging
- [ ] Add error monitoring (Sentry free tier)
- [ ] Add loading skeletons
- [ ] Add error boundaries
- [ ] Implement API caching
- [ ] Add WebSocket support for real-time alerts
- [ ] Implement data export (CSV/PDF)
- [ ] Add email notifications

**Estimated Time:** Ongoing

---

## Summary

### Current State
- **Backend:** 70% complete, solid foundation
- **Frontend:** 60% complete, good UI but not connected
- **Critical Issues:** 6 major gaps blocking production
- **Lines of Code:** ~15,000+

### Immediate Next Steps

**THIS WEEK:**
1. ✅ Fix authentication (remove MOCK_USER_ID)
2. ✅ Add missing GET endpoints (sleep, meals, activities)
3. ✅ Update frontend auth (email/password)

**NEXT WEEK:**
4. ✅ Enhance dummy data generation
5. ✅ Implement file upload
6. ✅ Connect dashboard to real API

**WEEK 3:**
7. ✅ Add tests
8. ✅ Deploy to Render.com free tier
9. ✅ Share demo URL

### Estimated Timeline

- **Critical Fixes:** 3-4 days
- **Enhanced Features:** 5-7 days
- **Polish & Deploy:** 5-7 days
- **Total: 2-3 weeks to production-ready demo**

### Recommended Free-Tier Deployment

**🏆 Render.com**
- Truly free for 90 days
- Easy setup with render.yaml
- PostgreSQL + Redis included
- Auto-deploy from GitHub
- Perfect for demo purposes

---

**Last Updated:** January 2025
**Next Review:** After Phase 1 completion
