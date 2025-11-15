# GlucoLens Development Workflow Guide

Complete guide for setting up a safe, efficient development environment and making incremental improvements to GlucoLens.

---

## Table of Contents

1. [Development Philosophy](#development-philosophy)
2. [Git Workflow](#git-workflow)
3. [Local Development Setup](#local-development-setup)
4. [Making Changes Safely](#making-changes-safely)
5. [Testing Strategy](#testing-strategy)
6. [Code Review Process](#code-review-process)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Common Development Tasks](#common-development-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Development Philosophy

### Core Principles

1. **Incremental Improvements** - Small, focused changes are easier to review and less likely to break things
2. **Test Early, Test Often** - Catch issues before they reach production
3. **Documentation First** - Document what you're about to build before building it
4. **Code Review Everything** - Two pairs of eyes are better than one
5. **Never Break Main** - Main branch should always be deployable

### Feature Lifecycle

```
Idea → Documentation → Implementation → Testing → Review → Merge → Deploy
```

---

## Git Workflow

### Branch Strategy

We use **Git Flow** with slight modifications:

```
main (production)
  └── develop (integration/staging)
       ├── feature/add-magic-link-auth
       ├── feature/fix-auth-consistency
       ├── bugfix/celery-task-retry
       └── hotfix/security-patch
```

### Branch Types

**`main`** - Production-ready code
- Always deployable
- Protected branch (requires PR + review)
- Auto-deploys to production (when CI/CD configured)

**`develop`** - Integration branch
- Latest development code
- Merge from feature branches
- Deploy to staging environment
- Merge to `main` when stable

**`feature/*`** - New features
- Branch from: `develop`
- Merge to: `develop`
- Naming: `feature/short-description`
- Examples: `feature/magic-link-auth`, `feature/health-metrics-ui`

**`bugfix/*`** - Bug fixes
- Branch from: `develop`
- Merge to: `develop`
- Naming: `bugfix/short-description`
- Examples: `bugfix/celery-retry-logic`, `bugfix/timezone-handling`

**`hotfix/*`** - Critical production fixes
- Branch from: `main`
- Merge to: `main` AND `develop`
- Naming: `hotfix/short-description`
- Examples: `hotfix/security-vulnerability`, `hotfix/data-loss-bug`

### Commit Message Convention

We follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build config)

**Examples:**
```bash
feat(auth): add magic link authentication

Implement passwordless login using email magic links.
Users receive a time-limited token via email.

Closes #123

---

fix(glucose): handle missing timestamp in bulk upload

Add validation to reject glucose readings without timestamps
and return clear error message to user.

Fixes #456

---

docs(deployment): add Kubernetes deployment guide

Add comprehensive K8s deployment instructions including
Helm charts and monitoring setup.
```

### Workflow Steps

#### 1. Create Feature Branch

```bash
# Update develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/add-magic-link-auth
```

#### 2. Make Changes

```bash
# Edit files
# ...

# Stage changes
git add .

# Commit with conventional message
git commit -m "feat(auth): implement magic link generation endpoint"

# Push regularly
git push -u origin feature/add-magic-link-auth
```

#### 3. Create Pull Request

**On GitHub:**
1. Click "New Pull Request"
2. Base: `develop` ← Compare: `feature/add-magic-link-auth`
3. Fill in PR template:

```markdown
## Description
Adds magic link authentication flow for passwordless login.

## Changes
- [ ] Add `/auth/request-magic-link` endpoint
- [ ] Add `/auth/verify-magic-link` endpoint
- [ ] Integrate SendGrid for email delivery
- [ ] Add rate limiting (5 requests/hour per email)
- [ ] Update frontend authService

## Testing
- [ ] Unit tests for magic link generation
- [ ] Integration tests for full auth flow
- [ ] Manual testing with real email

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
```

4. Request review from teammate
5. Link related issues

#### 4. Code Review

**Reviewer checklist:**
- [ ] Code is clear and readable
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Documentation updated
- [ ] Follows project conventions

**Address feedback:**
```bash
# Make requested changes
git add .
git commit -m "refactor(auth): extract magic link logic to service"
git push
```

#### 5. Merge

**After approval:**
1. Squash and merge (for cleaner history)
2. Delete feature branch
3. Pull latest develop

```bash
git checkout develop
git pull origin develop
```

---

## Local Development Setup

### Prerequisites

- **Docker Desktop** (or Docker + Docker Compose)
- **Node.js 18+** and npm
- **Git**
- **Code Editor** (VS Code recommended)

### First-Time Setup

#### 1. Clone Repository

```bash
git clone https://github.com/your-username/metabolic-story-teller.git
cd metabolic-story-teller
```

#### 2. Configure Environment

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with your settings
nano backend/.env
```

**Development `.env`:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://glucolens:devpassword@timescaledb:5432/glucolens
DB_PASSWORD=devpassword

# Redis
REDIS_URL=redis://redis:6379/0

# Security - Safe for development
SECRET_KEY=dev-secret-key-not-for-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Allow local frontend
CORS_ORIGINS=http://localhost:8080,http://localhost:5173

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Development flags
DEBUG=true
ENVIRONMENT=development

# Optional: Sentry (leave empty for dev)
SENTRY_DSN=
```

#### 3. Start Backend Services

```bash
# Start database, Redis, API, Celery
docker-compose up -d

# Check all services are running
docker-compose ps

# View logs
docker-compose logs -f api
```

**Expected output:**
```
✓ timescaledb started
✓ redis started
✓ api started
✓ celery_worker started
✓ celery_beat started
```

#### 4. Initialize Database

```bash
# Option A: Run migrations (when Alembic is setup)
docker-compose exec api alembic upgrade head

# Option B: Manual SQL (current approach)
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /migrations/init.sql
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /migrations/mvp2_schema.sql
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /migrations/health_data_additions.sql

# Create TimescaleDB hypertable
docker-compose exec timescaledb psql -U glucolens -d glucolens -c \
  "SELECT create_hypertable('glucose_readings', 'timestamp', if_not_exists => TRUE);"
```

#### 5. Generate Test Data

```bash
# Generate 90 days of realistic synthetic data
docker-compose exec api python scripts/generate_sample_data.py --days 90

# Verify data was created
docker-compose exec timescaledb psql -U glucolens -d glucolens -c \
  "SELECT COUNT(*) FROM glucose_readings;"
```

#### 6. Setup Frontend

```bash
# Install dependencies
npm install

# Start dev server (with hot reload)
npm run dev
```

**Frontend will be available at:** http://localhost:8080

#### 7. Verify Setup

**Test Backend:**
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

**Test Frontend:**
- Open http://localhost:8080
- Should see GlucoLens landing page
- Try logging in (create account first)

### VS Code Setup (Recommended)

#### Install Extensions

- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **ESLint** (dbaeumer.vscode-eslint)
- **Prettier** (esbenp.prettier-vscode)
- **Docker** (ms-azuretools.vscode-docker)
- **GitLens** (eamodio.gitlens)

#### Workspace Settings

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## Making Changes Safely

### Before Starting

1. **Check for existing issues** - Someone might already be working on it
2. **Create GitHub issue** - Describe what you want to build
3. **Discuss approach** - Get feedback before coding
4. **Create branch** - Start from latest `develop`

### Development Loop

```bash
# 1. Pull latest changes
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make small, incremental changes
# Edit files...

# 4. Test locally
# Backend changes: Check http://localhost:8000/docs
# Frontend changes: Check http://localhost:8080

# 5. Run linters
npm run lint                    # Frontend
docker-compose exec api black app/  # Backend (when configured)

# 6. Commit frequently with good messages
git add .
git commit -m "feat(scope): short description"

# 7. Push regularly (backup + show progress)
git push -u origin feature/your-feature

# 8. Repeat steps 3-7 until feature complete

# 9. Create PR when ready
# Use GitHub web interface
```

### Testing Changes

#### Backend Changes

**Manual Testing:**
```bash
# 1. Check API docs
open http://localhost:8000/docs

# 2. Test endpoint with curl
curl -X POST http://localhost:8000/api/v1/your-endpoint \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}'

# 3. Check database
docker-compose exec timescaledb psql -U glucolens -d glucolens
# Run SQL queries to verify data
```

**Automated Testing (when setup):**
```bash
# Run all tests
docker-compose exec api pytest

# Run specific test file
docker-compose exec api pytest tests/test_auth.py

# Run with coverage
docker-compose exec api pytest --cov=app --cov-report=html
```

#### Frontend Changes

**Manual Testing:**
```bash
# 1. Check in browser
open http://localhost:8080

# 2. Check browser console for errors (F12)

# 3. Test different screen sizes (responsive design)

# 4. Test in different browsers (Chrome, Firefox, Safari)
```

**Automated Testing (when setup):**
```bash
# Run tests
npm run test

# Run with coverage
npm run test:coverage
```

### Database Changes

#### Current Approach (Manual SQL)

1. **Create migration file:**
```bash
# Create new file: backend/migrations/YYYYMMDD_description.sql
# Example: backend/migrations/20250115_add_notifications_table.sql
```

2. **Write SQL:**
```sql
-- Add new table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add index
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
```

3. **Apply migration:**
```bash
docker-compose exec timescaledb psql -U glucolens -d glucolens \
  -f /migrations/20250115_add_notifications_table.sql
```

4. **Add corresponding model:**
```python
# backend/app/models/notification.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.models.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### Future Approach (Alembic)

**After Alembic is setup:**
```bash
# 1. Generate migration automatically
docker-compose exec api alembic revision --autogenerate -m "add notifications table"

# 2. Review generated migration
# Edit: backend/alembic/versions/xxxx_add_notifications_table.py

# 3. Apply migration
docker-compose exec api alembic upgrade head

# 4. Rollback if needed
docker-compose exec api alembic downgrade -1
```

---

## Testing Strategy

### Test Pyramid

```
           /\
          /  \        E2E Tests (Few)
         /----\       - Full user flows
        /      \      - Critical paths only
       /--------\     Integration Tests (Some)
      /          \    - API endpoint tests
     /------------\   - Database interactions
    /______________\  Unit Tests (Many)
                      - Business logic
                      - Utility functions
                      - ML algorithms
```

### Backend Testing

#### Unit Tests

**Test business logic in isolation:**

```python
# backend/tests/test_pcmci_service.py
import pytest
from app.services.pcmci_service import PCMCIAnalyzer

class TestPCMCIAnalyzer:
    def test_analyze_causality_with_sufficient_data(self):
        """Test PCMCI analysis with adequate data points."""
        analyzer = PCMCIAnalyzer()

        # Create mock data (100 data points)
        data = create_mock_timeseries(n_points=100)
        variables = ['glucose', 'sleep', 'exercise']

        result = analyzer.analyze_causality(data, variables)

        assert result is not None
        assert 'causal_graph' in result
        assert len(result['causal_links']) > 0

    def test_analyze_causality_fallback_on_insufficient_data(self):
        """Test fallback to correlation with insufficient data."""
        analyzer = PCMCIAnalyzer()

        # Create mock data (30 data points - below threshold)
        data = create_mock_timeseries(n_points=30)
        variables = ['glucose', 'sleep']

        result = analyzer.analyze_causality(data, variables)

        # Should fall back to correlation
        assert result is not None
        assert 'correlation' in result
```

#### Integration Tests

**Test API endpoints end-to-end:**

```python
# backend/tests/test_auth_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login_flow(async_client: AsyncClient):
    """Test complete registration and login flow."""

    # 1. Register new user
    register_data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }

    register_response = await async_client.post(
        "/api/v1/auth/register",
        json=register_data
    )

    assert register_response.status_code == 200
    user_data = register_response.json()
    assert "access_token" in user_data
    assert user_data["email"] == "test@example.com"

    # 2. Login with credentials
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data

    # 3. Access protected endpoint
    token = login_data["access_token"]
    profile_response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["email"] == "test@example.com"
```

#### Test Fixtures

**Setup reusable test data:**

```python
# backend/tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_db():
    """Create test database session."""
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=True
    )

    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with engine.begin() as conn:
        # Drop tables
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_user(test_db):
    """Create test user."""
    from app.models.user import User
    from app.utils.auth import get_password_hash

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User"
    )

    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return user
```

### Frontend Testing

#### Component Tests

**Test React components in isolation:**

```typescript
// src/components/__tests__/Dashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { Dashboard } from '@/components/Dashboard';
import { insightsService } from '@/services/insightsService';

// Mock the service
jest.mock('@/services/insightsService');

describe('Dashboard', () => {
  it('displays loading state initially', () => {
    render(<Dashboard userId="test-user-id" />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays insights after loading', async () => {
    // Mock API response
    const mockInsights = {
      correlations: [
        { factor: 'sleep', correlation: 0.75, p_value: 0.001 }
      ],
      patterns: []
    };

    (insightsService.getUserInsights as jest.Mock).mockResolvedValue(mockInsights);

    render(<Dashboard userId="test-user-id" />);

    await waitFor(() => {
      expect(screen.getByText(/sleep/i)).toBeInTheDocument();
      expect(screen.getByText(/0.75/)).toBeInTheDocument();
    });
  });

  it('displays error message on API failure', async () => {
    (insightsService.getUserInsights as jest.Mock).mockRejectedValue(
      new Error('API Error')
    );

    render(<Dashboard userId="test-user-id" />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

#### Integration Tests (E2E)

**Use Playwright or Cypress:**

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('user can register and login', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:8080');

    // Click register
    await page.click('text=Sign Up');

    // Fill registration form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.fill('input[name="confirmPassword"]', 'SecurePass123!');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('h1')).toContainText('Dashboard');
  });
});
```

### Running Tests

```bash
# Backend
docker-compose exec api pytest                    # All tests
docker-compose exec api pytest -v                 # Verbose
docker-compose exec api pytest -k test_auth       # Specific test
docker-compose exec api pytest --cov=app          # With coverage

# Frontend
npm run test                                      # Unit tests
npm run test:e2e                                  # E2E tests
npm run test:coverage                             # Coverage report
```

---

## Code Review Process

### Reviewer Responsibilities

**Check for:**

1. **Correctness** - Does the code do what it's supposed to?
2. **Readability** - Can others understand it?
3. **Maintainability** - Can it be easily modified later?
4. **Performance** - Are there obvious inefficiencies?
5. **Security** - Any vulnerabilities?
6. **Tests** - Are changes adequately tested?

### Review Checklist

**Code Quality:**
- [ ] Code follows project style guidelines
- [ ] No unnecessary complexity
- [ ] Functions are focused and single-purpose
- [ ] Variable names are clear and descriptive
- [ ] No commented-out code
- [ ] No console.log or print statements left in

**Architecture:**
- [ ] Changes fit existing architecture
- [ ] No tight coupling introduced
- [ ] Proper error handling
- [ ] Database queries are efficient
- [ ] No N+1 query problems

**Security:**
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Authentication/authorization checked
- [ ] Secrets not hardcoded
- [ ] Input validation present
- [ ] Rate limiting on sensitive endpoints

**Testing:**
- [ ] Unit tests for business logic
- [ ] Integration tests for API endpoints
- [ ] Edge cases covered
- [ ] Tests pass locally
- [ ] Coverage hasn't decreased

**Documentation:**
- [ ] Code is self-documenting
- [ ] Complex logic has comments
- [ ] API changes documented
- [ ] README updated if needed
- [ ] Migration guide if breaking changes

### Providing Feedback

**Good feedback:**
✅ "Consider extracting this into a separate function for better testability"
✅ "This query might be slow with large datasets. Consider adding an index on user_id"
✅ "Great approach! Small suggestion: we could use a list comprehension here for better performance"

**Bad feedback:**
❌ "This is wrong"
❌ "Why did you do it this way?"
❌ "I would have done it differently"

### Responding to Feedback

**As author:**
1. Don't take it personally - reviews improve code quality
2. Ask questions if feedback is unclear
3. Explain your reasoning, but be open to change
4. Thank reviewers for their time

**Disagreements:**
- Discuss in comments
- If can't resolve, ask team lead for input
- Remember: code review is collaborative, not combative

---

## CI/CD Pipeline

### GitHub Actions Workflow

**`.github/workflows/ci.yml`:**
```yaml
name: CI Pipeline

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop, main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: timescale/timescaledb:latest-pg15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov

    - name: Run tests
      env:
        DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test
        REDIS_URL: redis://localhost:6379/0
      run: |
        cd backend
        pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run linter
      run: npm run lint

    - name: Run tests
      run: npm run test

    - name: Build
      run: npm run build

  security-scan:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Run Snyk security scan
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
```

### Deployment Pipeline

**`.github/workflows/deploy.yml`:**
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        script: |
          cd /opt/metabolic-story-teller
          git pull origin main
          docker compose -f docker-compose.prod.yml pull
          docker compose -f docker-compose.prod.yml up -d
          docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

---

## Common Development Tasks

### Task 1: Add New API Endpoint

See [CLAUDE.md](CLAUDE.md#task-1-add-a-new-api-endpoint) for detailed guide.

**Quick reference:**
1. Define Pydantic schema in `backend/app/schemas/`
2. Create database model in `backend/app/models/`
3. Create route handler in `backend/app/routes/`
4. Register router in `backend/app/main.py`
5. Write tests in `backend/tests/`
6. Test in Swagger UI: http://localhost:8000/docs

### Task 2: Add New React Component

See [CLAUDE.md](CLAUDE.md#task-2-add-a-new-frontend-component) for detailed guide.

**Quick reference:**
1. Create component in `src/components/YourComponent.tsx`
2. Add TypeScript interfaces
3. Import Shadcn UI components as needed
4. Create service in `src/services/` if API calls needed
5. Write tests in `src/components/__tests__/`
6. Use in page component

### Task 3: Fix Authentication Bug

**Example: Add auth to sleep endpoint**

```python
# backend/app/routes/sleep.py

# BEFORE (broken)
MOCK_USER_ID = UUID("...")

@router.post("/")
async def create_sleep_data(
    sleep: SleepDataCreate,
    db: AsyncSession = Depends(get_db)
):
    new_sleep = SleepData(
        user_id=MOCK_USER_ID,  # ❌ Hardcoded
        **sleep.model_dump()
    )
    # ...

# AFTER (fixed)
from app.dependencies import get_current_user
from app.models.user import User

@router.post("/")
async def create_sleep_data(
    sleep: SleepDataCreate,
    current_user: User = Depends(get_current_user),  # ✅ From JWT
    db: AsyncSession = Depends(get_db)
):
    new_sleep = SleepData(
        user_id=current_user.id,  # ✅ Authenticated user
        **sleep.model_dump()
    )
    # ...
```

### Task 4: Update Database Schema

**With Alembic (recommended):**
```bash
# 1. Make model changes
# Edit backend/app/models/user.py

# 2. Generate migration
docker-compose exec api alembic revision --autogenerate -m "add phone to user"

# 3. Review migration
# Check backend/alembic/versions/xxxx_add_phone_to_user.py

# 4. Apply migration
docker-compose exec api alembic upgrade head
```

**Manual SQL (current approach):**
```bash
# 1. Create migration file
echo "ALTER TABLE users ADD COLUMN phone VARCHAR(20);" > \
  backend/migrations/20250115_add_phone_to_user.sql

# 2. Apply migration
docker-compose exec timescaledb psql -U glucolens -d glucolens \
  -f /migrations/20250115_add_phone_to_user.sql

# 3. Update model
# Edit backend/app/models/user.py
```

---

## Troubleshooting

### Issue: Docker containers won't start

**Check logs:**
```bash
docker-compose logs -f [service-name]
```

**Common fixes:**
```bash
# Remove all containers and volumes (CAUTION: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

### Issue: Frontend can't connect to backend

**Check CORS settings:**
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Add frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Check network:**
```bash
# Is backend running?
curl http://localhost:8000/health

# Is frontend making correct requests?
# Check browser console (F12 → Network tab)
```

### Issue: Database migration fails

**Check current version:**
```bash
docker-compose exec api alembic current
```

**Manual rollback:**
```bash
docker-compose exec api alembic downgrade -1
```

**Start fresh (CAUTION: deletes data):**
```bash
docker-compose down -v timescaledb
docker-compose up -d timescaledb
# Wait for DB to be ready
docker-compose exec api alembic upgrade head
```

### Issue: Tests are failing

**Check test database:**
```bash
# Is test DB configured?
# Check backend/.env or conftest.py for TEST_DATABASE_URL
```

**Run single test for debugging:**
```bash
docker-compose exec api pytest tests/test_auth.py::test_register_user -v -s
```

**Check test output:**
```bash
docker-compose exec api pytest --tb=short  # Short traceback
docker-compose exec api pytest --tb=long   # Detailed traceback
```

---

## Best Practices Summary

### DO ✅

- Write small, focused commits
- Test changes locally before pushing
- Write tests for new features
- Document complex logic
- Ask for help when stuck
- Review your own PR before requesting review
- Keep PRs small (< 400 lines changed)
- Update documentation with code changes
- Use feature flags for risky changes

### DON'T ❌

- Commit to `main` directly
- Push broken code
- Skip tests
- Leave TODO comments without GitHub issues
- Make unrelated changes in same PR
- Hardcode secrets or credentials
- Ignore linter warnings
- Skip code review
- Deploy on Fridays (unless necessary)

---

## Next Steps

1. **Setup local environment** - Follow setup guide above
2. **Pick a starter task** - Look for "good first issue" labels
3. **Make first contribution** - Start small to learn the workflow
4. **Ask questions** - Don't hesitate to ask for help

**Happy coding! 🎉**

For questions, check [CLAUDE.md](CLAUDE.md) or open a GitHub issue.
