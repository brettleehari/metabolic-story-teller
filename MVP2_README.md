# GlucoLens MVP2 - Feature Guide

**Advanced Glucose Monitoring with Authentication, ML, and Real-time Features**

---

## 🚀 What's New in MVP2

### Phase 1: Authentication & Multi-User ✅ COMPLETED

#### Features
- **JWT Authentication** - Secure token-based auth
- **User Registration** - Create new accounts
- **User Login** - Secure login with refresh tokens
- **Password Management** - Change password functionality
- **Profile Management** - Update user profile
- **Protected Endpoints** - All data endpoints now require authentication

#### New API Endpoints

**Authentication**
```bash
# Register new user
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "diabetes_type": "type1"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "securepassword123"
}
# Returns: { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }

# Refresh token
POST /api/v1/auth/refresh
{
  "refresh_token": "..."
}

# Logout
POST /api/v1/auth/logout
{
  "refresh_token": "..."
}

# Get current user
GET /api/v1/auth/me
Authorization: Bearer <access_token>

# Update profile
PUT /api/v1/auth/profile
Authorization: Bearer <access_token>
{
  "full_name": "John Smith",
  "target_glucose_min": 70.0,
  "target_glucose_max": 180.0
}

# Change password
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
{
  "old_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

#### Using Authentication

All existing endpoints now require authentication:

```bash
# Example: Upload glucose reading
curl -X POST http://localhost:8000/api/v1/glucose/readings \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-01-15T08:00:00Z",
    "value": 95.0,
    "source": "manual"
  }'
```

#### Frontend Integration

Update your API client:

```javascript
import GlucoLensAPI from './api/client';

// Initialize with base URL
const api = new GlucoLensAPI('http://localhost:8000/api/v1');

// Login
const { access_token, refresh_token } = await api.login(email, password);

// Store tokens
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// Use authenticated requests
api.setToken(access_token);
const readings = await api.getGlucoseReadings();
```

Enhanced API client with auth:

```javascript
class GlucoLensAPI {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Token expired - refresh or redirect to login
      throw new Error('Unauthorized');
    }

    return await response.json();
  }

  // Auth methods
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async refreshToken(refreshToken) {
    return this.request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async logout(refreshToken) {
    return this.request('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async getProfile() {
    return this.request('/auth/me');
  }

  // ... other methods
}
```

---

### Phase 2: Advanced ML Models (In Progress)

#### PCMCI Causal Discovery
- Time-lag analysis (1-7 days)
- Causal graph generation
- Statistical significance testing
- Discover patterns like "sleep yesterday → glucose today"

#### STUMPY Pattern Detection
- Recurring pattern discovery
- Anomaly detection
- Motif analysis

#### New Endpoints (Coming Soon)
```
GET /api/v1/insights/causal-graph
GET /api/v1/insights/recurring-patterns
GET /api/v1/insights/anomalies
GET /api/v1/insights/predictions
```

---

### Phase 3: Real-time Alerts (Coming Soon)

#### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts?token=<access_token>');

ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log('Alert:', alert);
  // { type: 'high_glucose', value: 250, message: 'High glucose detected!' }
};
```

#### Alert Configuration
```
GET /api/v1/alerts/config
POST /api/v1/alerts/config
GET /api/v1/alerts/history
PUT /api/v1/alerts/mark-read
```

---

### Phase 4: Frontend Dashboard (Coming Soon)

React/Next.js dashboard with:
- Login/Register pages
- Dashboard with glucose graphs
- Data entry forms
- Insights visualization
- Alert configuration
- Profile settings

---

### Phase 5: Apple HealthKit (Coming Soon)

iOS integration for automatic sync:
```
POST /api/v1/integrations/healthkit/sync
GET /api/v1/integrations/healthkit/status
```

---

## 🗄️ Database Changes

New tables in MVP2:

```sql
-- JWT refresh tokens
refresh_tokens

-- Alert system
alert_configs
alerts

-- HealthKit integration
healthkit_sync_status

-- API keys for external integrations
api_keys

-- ML predictions
glucose_predictions

-- WebSocket sessions
user_sessions
```

Run migration:
```bash
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /docker-entrypoint-initdb.d/mvp2_schema.sql
```

---

## 🔐 Security Features

### Token Management
- **Access Token**: Short-lived (30 min default)
- **Refresh Token**: Long-lived (7 days default)
- Automatic token refresh
- Secure token storage

### Password Security
- Bcrypt hashing
- Minimum 8 characters
- Change password functionality

### API Security
- All endpoints protected by default
- Bearer token authentication
- CORS protection
- Rate limiting (coming soon)

---

## 📊 Migration from MVP1

### For Existing Users

1. **Create Account**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "your_secure_password"
  }'
```

2. **Login and Get Token**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "your_secure_password"
  }'
```

3. **Update Frontend**
- Add auth to API calls
- Store tokens securely
- Implement token refresh logic

### Data Migration

MVP1 test user data (UUID: `00000000-0000-0000-0000-000000000001`) can be migrated:

```sql
-- Update test data to new user
UPDATE glucose_readings SET user_id = '<your_new_user_id>'
WHERE user_id = '00000000-0000-0000-0000-000000000001';

UPDATE sleep_data SET user_id = '<your_new_user_id>'
WHERE user_id = '00000000-0000-0000-0000-000000000001';

-- Repeat for other tables...
```

---

## 🧪 Testing MVP2

### Test User Accounts

Create test accounts:
```bash
# User 1
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test1@glucolens.com",
    "password": "test123456",
    "full_name": "Test User 1",
    "diabetes_type": "type1"
  }'

# User 2
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@glucolens.com",
    "password": "test123456",
    "full_name": "Test User 2",
    "diabetes_type": "type2"
  }'
```

### Test Authentication Flow

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test1@glucolens.com", "password": "test123456"}' \
  | jq -r '.access_token')

# 2. Get profile
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 3. Upload data
curl -X POST http://localhost:8000/api/v1/glucose/readings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-01-15T08:00:00Z",
    "value": 95.0,
    "source": "manual"
  }'

# 4. Get data
curl "http://localhost:8000/api/v1/glucose/readings?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🚀 Running MVP2

```bash
# 1. Update environment
cp backend/.env.example backend/.env
# Edit backend/.env and set SECRET_KEY

# 2. Start services
docker-compose down
docker-compose up -d --build

# 3. Run migrations
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /docker-entrypoint-initdb.d/init.sql
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /docker-entrypoint-initdb.d/mvp2_schema.sql

# 4. Test
curl http://localhost:8000/health
# Should show version 2.0.0
```

---

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 🎯 Next Steps

- [ ] Implement PCMCI causal discovery
- [ ] Add STUMPY pattern detection
- [ ] Create WebSocket real-time alerts
- [ ] Build React/Next.js frontend
- [ ] Add Apple HealthKit integration
- [ ] Implement rate limiting
- [ ] Add email notifications
- [ ] Create admin dashboard

---

**MVP2 Phase 1 Complete!** 🎉

Authentication and multi-user support are now live. Continue with Phase 2 for advanced ML features!
