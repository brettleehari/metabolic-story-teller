# CLAUDE.md - AI Assistant Guide for GlucoLens

This document provides comprehensive guidance for AI assistants working on the GlucoLens codebase.

## Project Overview

**GlucoLens (Metabolic Story Teller)** is an AI-powered glucose monitoring and pattern discovery platform that combines continuous glucose monitoring (CGM) data with lifestyle factors (sleep, exercise, meals) to discover personalized metabolic patterns using machine learning.

**Current Status**: MVP2 Phase - Full-stack application with authentication, advanced ML, and integrated frontend

## Quick Orientation

### Tech Stack
- **Frontend**: React 18 + TypeScript + Vite + Shadcn UI + TailwindCSS
- **Backend**: FastAPI (Python 3.11) + TimescaleDB + Redis + Celery
- **ML Libraries**: tigramite (PCMCI causal discovery), stumpy (pattern detection), mlxtend (association rules)
- **Deployment**: Docker Compose

### Repository Structure
```
metabolic-story-teller/
├── src/                    # React frontend (TypeScript)
│   ├── components/        # React components
│   ├── services/          # API client services
│   ├── pages/             # Route pages
│   └── lib/               # Utilities
├── backend/               # FastAPI backend (Python)
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # ML services (PCMCI, STUMPY)
│   │   ├── utils/        # Auth utilities
│   │   ├── main.py       # FastAPI app
│   │   ├── config.py     # Settings
│   │   └── tasks*.py     # Celery tasks
│   └── scripts/          # Utility scripts
├── docker-compose.yml    # Service orchestration
├── package.json          # Frontend dependencies
└── vite.config.ts        # Frontend build config
```

### Services Architecture
```
┌─────────────────┐
│  React Frontend │ :8080
│   (Vite Dev)    │
└────────┬────────┘
         │ HTTP
┌────────▼────────────┐
│   FastAPI Backend   │ :8000
│  (uvicorn + async)  │
└────────┬────────────┘
         │
    ┌────┴────┬──────────┬─────────┐
    │         │          │         │
┌───▼───┐ ┌──▼──────┐ ┌─▼──────┐ ┌▼────────┐
│Timescale│ │ Redis   │ │ Celery │ │ Celery │
│   DB    │ │(cache/  │ │ Worker │ │  Beat  │
│ (Postgres│ │ queue)  │ │        │ │(scheduler)
└─────────┘ └─────────┘ └────────┘ └─────────┘
```

---

## Development Workflows

### Starting the Development Environment

```bash
# Start all services (database, Redis, API, Celery)
docker-compose up -d

# Start frontend dev server (in separate terminal)
npm run dev

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker
```

**Access Points**:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs (Swagger UI)
- Database: localhost:5432 (user: glucolens, db: glucolens)
- Redis: localhost:6379

### Making Code Changes

**Frontend Changes**:
- Edit files in `src/` directory
- Vite provides hot module replacement (HMR)
- Changes appear immediately in browser
- TypeScript errors shown in console

**Backend Changes**:
- Edit files in `backend/app/` directory
- Uvicorn runs with `--reload` flag in development
- API server restarts automatically
- Check `docker-compose logs -f api` for errors

**Celery Task Changes**:
- Edit `backend/app/tasks.py` or `backend/app/tasks_ml.py`
- Restart worker: `docker-compose restart celery_worker`
- View task logs: `docker-compose logs -f celery_worker`

### Running Tests

```bash
# Backend tests (when implemented)
docker-compose exec api pytest

# Frontend linting
npm run lint

# Type checking
npx tsc --noEmit
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec timescaledb psql -U glucolens -d glucolens

# Run migrations (when using Alembic)
docker-compose exec api alembic upgrade head

# Generate sample data
docker-compose exec api python scripts/generate_sample_data.py --days 90

# Run ML pipeline manually
docker-compose exec api python scripts/run_ml_pipeline.py
```

---

## Key Conventions & Patterns

### Backend Conventions

#### 1. Async/Await Everywhere
**All database operations and route handlers must be async**:

```python
# ✅ CORRECT
@router.get("/readings")
async def get_readings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(GlucoseReading).where(GlucoseReading.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()

# ❌ WRONG - Don't use synchronous operations
def get_readings(db: Session = Depends(get_db)):
    return db.query(GlucoseReading).all()  # Blocks event loop!
```

#### 2. Pydantic Schema Pattern
**Separate schemas for input validation and output serialization**:

```python
# Input validation
class GlucoseReadingCreate(BaseModel):
    timestamp: datetime
    value: float = Field(ge=20.0, le=600.0)  # Validation
    source: Optional[str] = None

# Output serialization
class GlucoseReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode
    id: int
    user_id: UUID
    timestamp: datetime
    value: float
    created_at: datetime
```

#### 3. Authentication Pattern
**All protected routes use dependency injection**:

```python
from app.dependencies import get_current_user

@router.post("/readings")
async def create_reading(
    reading: GlucoseReadingCreate,
    current_user: User = Depends(get_current_user),  # Auto-validates JWT
    db: AsyncSession = Depends(get_db)
):
    # current_user is guaranteed to be authenticated
    new_reading = GlucoseReading(user_id=current_user.id, **reading.model_dump())
    db.add(new_reading)
    await db.commit()
    return new_reading
```

#### 4. Error Handling Pattern
**Use HTTPException with appropriate status codes**:

```python
from fastapi import HTTPException, status

# 404 for not found
if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

# 400 for validation errors
if value < 0:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Value must be positive"
    )

# 401 for authentication failures
if not verify_token(token):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )
```

#### 5. Database Query Pattern
**Use SQLAlchemy 2.0 select() syntax**:

```python
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

# Basic query
query = select(Model).where(Model.user_id == user_id)

# With joins/eager loading
query = select(User).options(
    selectinload(User.glucose_readings)
).where(User.id == user_id)

# Complex filters
query = select(GlucoseReading).where(
    and_(
        GlucoseReading.user_id == user_id,
        GlucoseReading.timestamp >= start_date,
        GlucoseReading.timestamp < end_date
    )
).order_by(GlucoseReading.timestamp.desc())

# Execute
result = await db.execute(query)
items = result.scalars().all()  # For multiple results
item = result.scalar_one_or_none()  # For single result
```

#### 6. Celery Task Pattern
**Decorate tasks and handle errors gracefully**:

```python
from app.tasks import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_data(self, user_id: str):
    try:
        # Task logic here
        logger.info(f"Processing data for user {user_id}")
        # ...
        return {"status": "success"}
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Frontend Conventions

#### 1. Component Structure Pattern
**Functional components with TypeScript**:

```typescript
// src/components/MyComponent.tsx
import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface MyComponentProps {
  title: string;
  onAction?: () => void;
}

export const MyComponent = ({ title, onAction }: MyComponentProps) => {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await onAction?.();
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">{title}</h2>
      <Button onClick={handleClick} disabled={loading}>
        {loading ? 'Loading...' : 'Click Me'}
      </Button>
    </div>
  );
};
```

#### 2. Service Layer Pattern
**Singleton classes for API communication**:

```typescript
// src/services/myService.ts
import { API_CONFIG } from '@/config/api';
import { getAuthHeaders } from '@/services/authService';

export interface MyData {
  id: string;
  value: number;
}

class MyService {
  private baseUrl = `${API_CONFIG.BASE_URL}/my-endpoint`;

  async getData(): Promise<MyData[]> {
    const response = await fetch(this.baseUrl, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.statusText}`);
    }

    return await response.json();
  }

  async createData(data: Partial<MyData>): Promise<MyData> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to create data: ${response.statusText}`);
    }

    return await response.json();
  }
}

export const myService = new MyService();
```

#### 3. Shadcn UI Component Usage
**Import from `@/components/ui/` and use variants**:

```typescript
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

// Usage
<Card>
  <CardHeader>
    <CardTitle>Form Example</CardTitle>
  </CardHeader>
  <CardContent>
    <Input placeholder="Enter value" />
    <Button variant="default" size="lg">Submit</Button>
    <Button variant="outline" size="sm">Cancel</Button>
  </CardContent>
</Card>

// Toast notifications
toast.success('Operation completed!');
toast.error('Something went wrong');
```

#### 4. State Management Pattern
**Local state for UI, services for server data**:

```typescript
import { useState, useEffect } from 'react';
import { myService } from '@/services/myService';

export const MyPage = () => {
  // UI state
  const [view, setView] = useState<'list' | 'detail'>('list');
  const [loading, setLoading] = useState(false);

  // Server data
  const [data, setData] = useState<MyData[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const result = await myService.getData();
        setData(result);
      } catch (error) {
        toast.error('Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return <div>{/* Render data */}</div>;
};
```

#### 5. Tailwind CSS Pattern
**Use utility classes, avoid inline styles**:

```typescript
// ✅ CORRECT - Tailwind utilities
<div className="flex flex-col gap-4 p-6 bg-white rounded-lg shadow-md">
  <h2 className="text-2xl font-bold text-gray-900">Title</h2>
  <p className="text-gray-600">Description</p>
</div>

// ❌ AVOID - Inline styles
<div style={{ display: 'flex', padding: '24px' }}>
```

#### 6. TypeScript Type Safety
**Define interfaces for all API responses**:

```typescript
// Define types matching backend schemas
interface GlucoseReading {
  id: number;
  user_id: string;
  timestamp: string;  // ISO datetime string
  value: number;
  source?: string;
}

interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Use in service methods
async getReadings(): Promise<GlucoseReading[]> {
  const response = await fetch(this.endpoint);
  const data: ApiResponse<GlucoseReading[]> = await response.json();
  return data.data;
}
```

---

## Common Tasks & How to Accomplish Them

### Task 1: Add a New API Endpoint

**Steps**:

1. **Define Pydantic schemas** (`backend/app/schemas/`):
```python
# backend/app/schemas/my_feature.py
from pydantic import BaseModel, Field
from datetime import datetime

class MyFeatureCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float = Field(..., ge=0)

class MyFeatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: UUID
    name: str
    value: float
    created_at: datetime
```

2. **Create database model** (`backend/app/models/`):
```python
# backend/app/models/my_feature.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
import uuid

class MyFeature(Base):
    __tablename__ = "my_features"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_my_features_user_created', 'user_id', 'created_at'),
    )
```

3. **Create route handler** (`backend/app/routes/`):
```python
# backend/app/routes/my_feature.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.my_feature import MyFeature
from app.schemas.my_feature import MyFeatureCreate, MyFeatureResponse

router = APIRouter(prefix="/my-feature", tags=["my-feature"])

@router.post("/", response_model=MyFeatureResponse)
async def create_feature(
    feature: MyFeatureCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_feature = MyFeature(
        user_id=current_user.id,
        **feature.model_dump()
    )
    db.add(new_feature)
    await db.commit()
    await db.refresh(new_feature)
    return new_feature

@router.get("/", response_model=list[MyFeatureResponse])
async def get_features(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(MyFeature).where(MyFeature.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()
```

4. **Register router in main app** (`backend/app/main.py`):
```python
from app.routes import my_feature

app.include_router(my_feature.router, prefix="/api/v1")
```

5. **Create database migration** (if using Alembic):
```bash
docker-compose exec api alembic revision --autogenerate -m "Add my_feature table"
docker-compose exec api alembic upgrade head
```

6. **Test the endpoint**:
```bash
# Create feature
curl -X POST http://localhost:8000/api/v1/my-feature \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "value": 123.45}'

# Get features
curl http://localhost:8000/api/v1/my-feature \
  -H "Authorization: Bearer <token>"
```

### Task 2: Add a New Frontend Component

**Steps**:

1. **Create component file** (`src/components/MyNewComponent.tsx`):
```typescript
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface MyNewComponentProps {
  title: string;
  onSave?: (data: any) => void;
}

export const MyNewComponent = ({ title, onSave }: MyNewComponentProps) => {
  const [data, setData] = useState('');

  const handleSubmit = () => {
    onSave?.(data);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <input
          value={data}
          onChange={(e) => setData(e.target.value)}
          className="w-full px-3 py-2 border rounded"
        />
        <Button onClick={handleSubmit}>Save</Button>
      </CardContent>
    </Card>
  );
};
```

2. **Create service if needed** (`src/services/myNewService.ts`):
```typescript
import { API_CONFIG } from '@/config/api';
import { getAuthHeaders } from '@/services/authService';

class MyNewService {
  async saveData(data: any) {
    const response = await fetch(`${API_CONFIG.BASE_URL}/my-feature`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to save data');
    }

    return await response.json();
  }
}

export const myNewService = new MyNewService();
```

3. **Use component in page**:
```typescript
import { MyNewComponent } from '@/components/MyNewComponent';
import { myNewService } from '@/services/myNewService';
import { toast } from 'sonner';

export const MyPage = () => {
  const handleSave = async (data: any) => {
    try {
      await myNewService.saveData(data);
      toast.success('Data saved successfully');
    } catch (error) {
      toast.error('Failed to save data');
    }
  };

  return <MyNewComponent title="My Feature" onSave={handleSave} />;
};
```

### Task 3: Add a Celery Background Task

**Steps**:

1. **Define task** (`backend/app/tasks.py` or `backend/app/tasks_ml.py`):
```python
from app.tasks import celery_app
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import async_session_maker

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def my_background_task(self, user_id: str, param: str):
    """
    Process data for a user in the background.
    """
    try:
        logger.info(f"Starting task for user {user_id} with param {param}")

        # For async operations, use AsyncSession
        async def process():
            async with async_session_maker() as session:
                # Your async logic here
                result = await some_async_operation(session, user_id, param)
                await session.commit()
                return result

        # Run async code in Celery (sync context)
        import asyncio
        result = asyncio.run(process())

        logger.info(f"Task completed for user {user_id}")
        return {"status": "success", "result": result}

    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

2. **Schedule task (if periodic)** (`backend/app/tasks.py`):
```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'my-periodic-task': {
        'task': 'app.tasks.my_background_task',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
        'args': ('default_user_id', 'default_param'),
    },
}
```

3. **Trigger task from API** (`backend/app/routes/`):
```python
@router.post("/trigger-task")
async def trigger_task(
    param: str,
    current_user: User = Depends(get_current_user)
):
    # Trigger async task
    task = my_background_task.delay(str(current_user.id), param)

    return {
        "task_id": task.id,
        "status": "Task queued",
        "message": "Processing in background"
    }
```

4. **Check task status** (optional):
```python
@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task_result.state,
        "result": task_result.result if task_result.ready() else None
    }
```

5. **Restart Celery worker** after changes:
```bash
docker-compose restart celery_worker
docker-compose logs -f celery_worker  # Monitor logs
```

### Task 4: Add a New Shadcn UI Component

```bash
# List available components
npx shadcn-ui@latest add

# Add specific component (e.g., dialog)
npx shadcn-ui@latest add dialog

# Component will be added to src/components/ui/dialog.tsx
# Import and use:
# import { Dialog, DialogContent, DialogHeader } from '@/components/ui/dialog'
```

### Task 5: Generate Sample Data

```bash
# Generate 90 days of realistic synthetic data
docker-compose exec api python scripts/generate_sample_data.py --days 90

# Generate with custom user
docker-compose exec api python scripts/generate_sample_data.py --days 30 --user-id <uuid>
```

### Task 6: Run ML Analysis Pipeline

```bash
# Trigger via API
curl -X POST http://localhost:8000/api/v1/insights/trigger-analysis \
  -H "Authorization: Bearer <token>"

# Or run directly
docker-compose exec api python scripts/run_ml_pipeline.py

# Check results
curl http://localhost:8000/api/v1/insights/correlations \
  -H "Authorization: Bearer <token>"
curl http://localhost:8000/api/v1/insights/patterns \
  -H "Authorization: Bearer <token>"
```

---

## Important Gotchas & Considerations

### 1. Async/Await in Celery
**Problem**: Celery tasks run in sync context, but our DB uses async.

**Solution**: Use `asyncio.run()` to execute async code:
```python
@celery_app.task
def my_task(user_id: str):
    async def async_work():
        async with async_session_maker() as session:
            # Async database operations
            pass

    asyncio.run(async_work())
```

### 2. CORS Configuration
**Problem**: Frontend on :8080 can't access backend on :8000 without CORS.

**Current Setup**: CORS middleware in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),  # From .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For Development**: Ensure `.env` has:
```
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
```

### 3. Database Session Management
**Problem**: Forgetting to commit or close sessions leads to locks.

**Solution**: Always use the `get_db()` dependency:
```python
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Auto-commits on success
        except Exception:
            await session.rollback()  # Auto-rollbacks on error
            raise
```

### 4. JWT Token Expiration
**Current Setup**:
- Access tokens: 30 minutes
- Refresh tokens: 7 days

**Handling Expiration**:
- Frontend should implement token refresh logic
- Currently, user must re-login after access token expires
- Implement refresh endpoint call before token expires

### 5. TimescaleDB Hypertables
**Problem**: Regular PostgreSQL operations don't work on hypertables.

**Solution**: Use TimescaleDB-specific functions:
```sql
-- Create hypertable (already done for glucose_readings)
SELECT create_hypertable('glucose_readings', 'timestamp');

-- Don't use regular indexes on time column
-- TimescaleDB handles this automatically
```

### 6. Environment Variables
**Backend**: Uses Pydantic Settings, reads from `.env`:
```python
# backend/app/config.py
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    # ...
```

**Frontend**: Uses Vite env vars (must start with `VITE_`):
```typescript
// Must be in .env as VITE_API_URL
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### 7. Docker Volume Permissions
**Problem**: Files created in containers may have wrong permissions.

**Solution**: Use docker-compose exec with proper user, or:
```bash
# Fix permissions on host
sudo chown -R $USER:$USER backend/
```

### 8. ML Model Dependencies
**PCMCI requires**: Sufficient data points (min 50 recommended)
**STUMPY requires**: Minimum 3x window size data points

**Handle gracefully**:
```python
try:
    results = pcmci_service.analyze_causality(data)
except InsufficientDataError:
    # Fall back to simple correlation
    results = correlation_analysis(data)
```

### 9. Time Zones
**Database**: Stores timestamps in UTC
**Frontend**: Should convert to user's local timezone
**Backend**: Timezone-aware datetimes required

```python
from datetime import datetime, timezone

# Always use timezone-aware datetimes
now = datetime.now(timezone.utc)
```

### 10. Password Security
**Never log passwords or tokens**:
```python
# ❌ BAD
logger.info(f"User logged in: {user.email}, password: {password}")

# ✅ GOOD
logger.info(f"User logged in: {user.email}")
```

**Always hash passwords**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(password)
```

---

## Testing Guidelines

### Backend Testing (Future)

**Structure**:
```
backend/tests/
├── conftest.py          # Pytest fixtures
├── test_auth.py         # Authentication tests
├── test_glucose.py      # Glucose endpoint tests
├── test_insights.py     # Insights tests
└── test_ml.py           # ML pipeline tests
```

**Example Test**:
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_glucose_reading(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/api/v1/glucose/readings",
        json={
            "timestamp": "2025-01-15T08:00:00Z",
            "value": 95.0,
            "source": "dexcom_g7"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == 95.0
```

### Frontend Testing (Future)

Use Vitest + React Testing Library:
```typescript
import { render, screen } from '@testing-library/react';
import { MyComponent } from '@/components/MyComponent';

describe('MyComponent', () => {
  it('renders title', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

---

## Git Workflow

### Branch Naming
- Feature branches: `feature/description` or `claude/claude-md-*`
- Bug fixes: `fix/description`
- Hotfixes: `hotfix/description`

### Commit Messages
Follow conventional commits:
```
feat: Add PCMCI causal discovery endpoint
fix: Resolve token refresh bug
docs: Update API documentation
refactor: Simplify correlation analysis
test: Add tests for glucose endpoints
```

### Pull Request Process
1. Create feature branch from main
2. Make changes with descriptive commits
3. Test locally (frontend + backend)
4. Push to remote: `git push -u origin branch-name`
5. Create PR with description of changes
6. Wait for review and tests to pass
7. Merge to main

### Current Branch
Working on: `claude/claude-md-mi0pyo7shwm0r0lk-01SW4k3xQDN1X4aYYpGh5QXK`

---

## API Documentation

### Authentication Endpoints

```
POST   /api/v1/auth/register          # Create new user account
POST   /api/v1/auth/login             # Get JWT access token
POST   /api/v1/auth/refresh           # Refresh access token
POST   /api/v1/auth/logout            # Invalidate refresh token
GET    /api/v1/auth/me                # Get current user profile
PUT    /api/v1/auth/profile           # Update user profile
POST   /api/v1/auth/change-password   # Change password
```

### Data Ingestion Endpoints

```
POST   /api/v1/glucose/readings       # Create glucose reading
POST   /api/v1/glucose/bulk           # Bulk upload (up to 10,000)
GET    /api/v1/glucose/readings       # Get user's readings
DELETE /api/v1/glucose/readings/{id}  # Delete reading

POST   /api/v1/sleep                  # Create sleep data
GET    /api/v1/sleep                  # Get sleep data
POST   /api/v1/sleep/bulk             # Bulk upload

POST   /api/v1/activities             # Log activity
GET    /api/v1/activities             # Get activities
POST   /api/v1/activities/bulk        # Bulk upload

POST   /api/v1/meals                  # Log meal
GET    /api/v1/meals                  # Get meals
POST   /api/v1/meals/bulk             # Bulk upload
```

### Insights Endpoints

```
GET    /api/v1/insights/correlations  # Top correlations (sleep, exercise, diet → glucose)
GET    /api/v1/insights/patterns      # Discovered patterns (association rules)
GET    /api/v1/insights/dashboard     # Dashboard summary (7/30/90 day periods)
POST   /api/v1/insights/trigger-analysis  # Manual trigger for analysis pipeline

GET    /api/v1/advanced_insights/pcmci     # PCMCI causal discovery results
POST   /api/v1/advanced_insights/run_pcmci # Trigger PCMCI analysis
GET    /api/v1/advanced_insights/stumpy_patterns  # STUMPY recurring patterns
POST   /api/v1/advanced_insights/run_stumpy      # Trigger STUMPY analysis
```

### Health Metrics Endpoints

```
POST   /api/v1/hba1c                  # Log HbA1c test result
GET    /api/v1/hba1c                  # Get HbA1c history

POST   /api/v1/medications            # Add medication
GET    /api/v1/medications            # Get medications
PUT    /api/v1/medications/{id}       # Update medication

POST   /api/v1/insulin                # Log insulin dose
GET    /api/v1/insulin                # Get insulin history

POST   /api/v1/blood_pressure         # Log BP reading
GET    /api/v1/blood_pressure         # Get BP history

POST   /api/v1/body_metrics           # Log weight, BMI, etc.
GET    /api/v1/body_metrics           # Get body metrics
```

---

## Configuration Reference

### Backend Environment Variables (`.env`)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://glucolens:password@timescaledb:5432/glucolens

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:8080,http://localhost:5173

# ML Configuration
MIN_DATA_POINTS_PCMCI=50
PCMCI_ALPHA_LEVEL=0.05
PCMCI_MAX_LAG=7  # Days
STUMPY_WINDOW_SIZE=288  # 24 hours at 5-min intervals
ML_CACHE_TTL=3600  # 1 hour

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Frontend Environment Variables

```bash
# API Base URL
VITE_API_URL=http://localhost:8000
```

### Docker Compose Services

```yaml
services:
  timescaledb:    # PostgreSQL + TimescaleDB
  redis:          # Cache + task queue
  api:            # FastAPI backend
  celery_worker:  # Background task processor
  celery_beat:    # Task scheduler
```

---

## Quick Reference Commands

### Docker Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build

# View logs
docker-compose logs -f [service-name]

# Execute command in service
docker-compose exec api python script.py

# Restart service
docker-compose restart [service-name]
```

### Database Operations
```bash
# Access database
docker-compose exec timescaledb psql -U glucolens -d glucolens

# Useful SQL queries
SELECT COUNT(*) FROM glucose_readings;
SELECT * FROM users LIMIT 10;
SELECT * FROM correlations ORDER BY abs_correlation DESC LIMIT 10;
SELECT * FROM patterns WHERE confidence > 0.7;
```

### Celery Operations
```bash
# View active tasks
docker-compose exec celery_worker celery -A app.tasks inspect active

# View scheduled tasks
docker-compose exec celery_worker celery -A app.tasks inspect scheduled

# View registered tasks
docker-compose exec celery_worker celery -A app.tasks inspect registered

# Purge all tasks
docker-compose exec celery_worker celery -A app.tasks purge
```

### Frontend Operations
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## Debugging Tips

### 1. Backend Debugging
**Enable detailed logging**:
```python
# backend/app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check API logs**:
```bash
docker-compose logs -f api
```

**Test endpoint in browser**: http://localhost:8000/docs

### 2. Frontend Debugging
**Check browser console**: F12 → Console tab

**View network requests**: F12 → Network tab

**Check component state**: Install React DevTools extension

### 3. Database Debugging
**Check connections**:
```sql
SELECT * FROM pg_stat_activity WHERE datname = 'glucolens';
```

**Check table sizes**:
```sql
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 4. Celery Debugging
**Monitor task execution**:
```bash
docker-compose logs -f celery_worker | grep "Task"
```

**Check task history**:
```python
from app.tasks import celery_app
task_result = celery_app.AsyncResult(task_id)
print(task_result.state, task_result.result)
```

### 5. Authentication Debugging
**Decode JWT token**: Use https://jwt.io to inspect token contents

**Check token in requests**:
```bash
# Include token in Authorization header
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/auth/me
```

---

## Performance Optimization

### Backend
- Use database indexes on frequently queried columns
- Implement caching with Redis for expensive computations
- Use bulk operations for large data uploads
- Optimize SQL queries with `.options(selectinload())`
- Use async operations throughout

### Frontend
- Lazy load components with `React.lazy()`
- Memoize expensive computations with `useMemo()`
- Debounce search inputs
- Use virtual scrolling for large lists
- Optimize bundle size with tree shaking

### Database
- Create indexes on (user_id, timestamp) for time-series queries
- Use TimescaleDB continuous aggregates for pre-computed stats
- Implement retention policies for old data
- Use connection pooling (already configured in SQLAlchemy)

---

## Security Best Practices

1. **Never commit secrets**: Use `.env` files (gitignored)
2. **Validate all inputs**: Use Pydantic schemas
3. **Sanitize outputs**: Prevent XSS attacks
4. **Use parameterized queries**: SQLAlchemy prevents SQL injection
5. **Implement rate limiting**: Protect against brute force (TODO)
6. **Use HTTPS in production**: Terminate SSL at reverse proxy
7. **Implement CSRF protection**: For form submissions (TODO)
8. **Regular dependency updates**: Check for vulnerabilities
9. **Audit logging**: Log security-relevant events
10. **Principle of least privilege**: Database user permissions

---

## Additional Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- React: https://react.dev/
- Shadcn UI: https://ui.shadcn.com/
- Celery: https://docs.celeryq.dev/
- TimescaleDB: https://docs.timescale.com/

### Internal Docs
- `README.md` - Project overview
- `backend_architecture.md` - Detailed backend design
- `FRONTEND_INTEGRATION.md` - Frontend integration guide
- `ML_PIPELINE_EXECUTION_GUIDE.md` - ML pipeline documentation
- `MVP2_PLAN.md` - Roadmap and features

### API Documentation
- Interactive Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc

---

## Summary

This codebase follows modern full-stack development practices with:
- **Type Safety**: TypeScript frontend, Pydantic backend
- **Async Operations**: Full async/await throughout
- **Separation of Concerns**: Clear boundaries between layers
- **ML Integration**: PCMCI and STUMPY for advanced analytics
- **Production Ready**: Docker, background tasks, authentication

When working on this project:
1. Always use async/await for database operations
2. Follow the schema pattern (Create/Response)
3. Use dependency injection for auth and DB sessions
4. Write type-safe code (TypeScript/Pydantic)
5. Test changes locally before committing
6. Document API changes in Swagger docstrings
7. Handle errors gracefully with appropriate status codes
8. Never commit secrets or credentials

**Happy coding!**
