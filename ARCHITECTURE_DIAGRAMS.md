# GlucoLens Architecture Diagrams

Comprehensive Mermaid diagrams for all components and their integrations.

---

## Table of Contents

1. [High-Level System Overview](#1-high-level-system-overview)
2. [Component Integration](#2-component-integration)
3. [Backend Architecture](#3-backend-architecture)
4. [Frontend Architecture](#4-frontend-architecture)
5. [ML Pipeline Architecture](#5-ml-pipeline-architecture)
6. [Database Schema](#6-database-schema)
7. [Authentication Flow](#7-authentication-flow)
8. [Data Flow](#8-data-flow)
9. [Deployment Architecture](#9-deployment-architecture)

---

## 1. High-Level System Overview

```mermaid
graph TB
    subgraph "Users"
        U1[Web Browser]
        U2[Mobile App - Future]
        U3[API Clients]
    end

    subgraph "Frontend Layer"
        FE[React Frontend<br/>Port 8080]
    end

    subgraph "Backend Layer"
        API[FastAPI Backend<br/>Port 8000]
        CELERY_W[Celery Workers]
        CELERY_B[Celery Beat<br/>Scheduler]
    end

    subgraph "Data Layer"
        DB[(TimescaleDB<br/>PostgreSQL)]
        REDIS[(Redis<br/>Cache & Queue)]
    end

    subgraph "ML Services"
        PCMCI[PCMCI Causal<br/>Discovery]
        STUMPY[STUMPY Pattern<br/>Detection]
        ASSOC[Association<br/>Rules Mining]
    end

    U1 --> FE
    U2 -.-> FE
    U3 --> API
    FE --> API
    API --> DB
    API --> REDIS
    CELERY_W --> DB
    CELERY_W --> REDIS
    CELERY_B --> REDIS
    CELERY_W --> PCMCI
    CELERY_W --> STUMPY
    CELERY_W --> ASSOC

    style FE fill:#61dafb,stroke:#333,stroke-width:2px
    style API fill:#009688,stroke:#333,stroke-width:2px
    style DB fill:#336791,stroke:#333,stroke-width:2px
    style REDIS fill:#dc382d,stroke:#333,stroke-width:2px
    style PCMCI fill:#ff9800,stroke:#333,stroke-width:2px
    style STUMPY fill:#ff9800,stroke:#333,stroke-width:2px
    style ASSOC fill:#ff9800,stroke:#333,stroke-width:2px
```

---

## 2. Component Integration

```mermaid
graph LR
    subgraph "Frontend Components"
        AUTH_UI[AuthForm]
        DASH[Dashboard]
        UPLOAD[UploadWizard]
        CHARTS[Charts & Viz]
    end

    subgraph "Frontend Services"
        AUTH_SVC[authService]
        INSIGHTS_SVC[insightsService]
        UPLOAD_SVC[uploadService]
        ANALYSIS_SVC[analysisService]
    end

    subgraph "API Layer"
        AUTH_API[/api/v1/auth]
        GLUCOSE_API[/api/v1/glucose]
        INSIGHTS_API[/api/v1/insights]
        ADV_INSIGHTS_API[/api/v1/advanced_insights]
        HEALTH_API[/api/v1/health_metrics]
    end

    subgraph "Backend Services"
        PCMCI_SVC[PCMCI Service]
        STUMPY_SVC[STUMPY Service]
        CORR_SVC[Correlation Service]
    end

    subgraph "Background Tasks"
        AGG_TASK[Daily Aggregation]
        CORR_TASK[Correlation Analysis]
        PATTERN_TASK[Pattern Discovery]
        ML_TASK[ML Analysis]
    end

    subgraph "Data Storage"
        USERS_DB[(Users)]
        GLUCOSE_DB[(Glucose Readings)]
        INSIGHTS_DB[(Correlations<br/>Patterns)]
        AGG_DB[(Daily Aggregates)]
    end

    AUTH_UI --> AUTH_SVC
    DASH --> INSIGHTS_SVC
    UPLOAD --> UPLOAD_SVC
    DASH --> ANALYSIS_SVC

    AUTH_SVC --> AUTH_API
    INSIGHTS_SVC --> INSIGHTS_API
    INSIGHTS_SVC --> ADV_INSIGHTS_API
    UPLOAD_SVC --> GLUCOSE_API
    ANALYSIS_SVC --> ADV_INSIGHTS_API

    AUTH_API --> USERS_DB
    GLUCOSE_API --> GLUCOSE_DB
    INSIGHTS_API --> INSIGHTS_DB
    ADV_INSIGHTS_API --> PCMCI_SVC
    ADV_INSIGHTS_API --> STUMPY_SVC

    AGG_TASK --> GLUCOSE_DB
    AGG_TASK --> AGG_DB
    CORR_TASK --> AGG_DB
    CORR_TASK --> PCMCI_SVC
    PATTERN_TASK --> AGG_DB
    ML_TASK --> PCMCI_SVC
    ML_TASK --> STUMPY_SVC

    PCMCI_SVC --> INSIGHTS_DB
    STUMPY_SVC --> INSIGHTS_DB
    CORR_SVC --> INSIGHTS_DB

    style AUTH_UI fill:#61dafb
    style DASH fill:#61dafb
    style UPLOAD fill:#61dafb
    style PCMCI_SVC fill:#ff9800
    style STUMPY_SVC fill:#ff9800
```

---

## 3. Backend Architecture

```mermaid
graph TB
    subgraph "FastAPI Application"
        MAIN[main.py<br/>FastAPI App]
        DEPS[dependencies.py<br/>Auth & DB]
        CONFIG[config.py<br/>Settings]
    end

    subgraph "API Routes"
        AUTH_ROUTE[routes/auth.py]
        GLUCOSE_ROUTE[routes/glucose.py]
        SLEEP_ROUTE[routes/sleep.py]
        MEALS_ROUTE[routes/meals.py]
        ACTIVITIES_ROUTE[routes/activities.py]
        INSIGHTS_ROUTE[routes/insights.py]
        ADV_INSIGHTS_ROUTE[routes/advanced_insights.py]
        HEALTH_ROUTE[routes/health_metrics.py]
    end

    subgraph "Pydantic Schemas"
        AUTH_SCHEMA[schemas/auth.py]
        GLUCOSE_SCHEMA[schemas/glucose.py]
        INSIGHTS_SCHEMA[schemas/insights.py]
    end

    subgraph "Database Models"
        USER_MODEL[models/user.py]
        GLUCOSE_MODEL[models/glucose.py]
        SLEEP_MODEL[models/sleep.py]
        CORR_MODEL[models/correlation.py]
        PATTERN_MODEL[models/pattern.py]
        AGG_MODEL[models/aggregate.py]
    end

    subgraph "ML Services"
        PCMCI_SERVICE[services/pcmci_service.py<br/>Causal Discovery]
        STUMPY_SERVICE[services/stumpy_service.py<br/>Pattern Detection]
    end

    subgraph "Utilities"
        AUTH_UTIL[utils/auth.py<br/>JWT & Password]
    end

    subgraph "Background Tasks"
        TASKS[tasks.py<br/>Aggregation, Correlation]
        TASKS_ML[tasks_ml.py<br/>PCMCI, STUMPY]
    end

    subgraph "Database"
        DB[(TimescaleDB)]
    end

    MAIN --> AUTH_ROUTE
    MAIN --> GLUCOSE_ROUTE
    MAIN --> INSIGHTS_ROUTE
    MAIN --> ADV_INSIGHTS_ROUTE

    AUTH_ROUTE --> AUTH_SCHEMA
    AUTH_ROUTE --> USER_MODEL
    AUTH_ROUTE --> AUTH_UTIL

    GLUCOSE_ROUTE --> GLUCOSE_SCHEMA
    GLUCOSE_ROUTE --> GLUCOSE_MODEL

    ADV_INSIGHTS_ROUTE --> PCMCI_SERVICE
    ADV_INSIGHTS_ROUTE --> STUMPY_SERVICE

    TASKS --> AGG_MODEL
    TASKS --> CORR_MODEL
    TASKS_ML --> PCMCI_SERVICE
    TASKS_ML --> STUMPY_SERVICE

    USER_MODEL --> DB
    GLUCOSE_MODEL --> DB
    CORR_MODEL --> DB
    PATTERN_MODEL --> DB

    DEPS --> AUTH_UTIL
    DEPS --> DB

    style MAIN fill:#009688
    style PCMCI_SERVICE fill:#ff9800
    style STUMPY_SERVICE fill:#ff9800
    style DB fill:#336791
```

---

## 4. Frontend Architecture

```mermaid
graph TB
    subgraph "Entry Point"
        MAIN[main.tsx]
        APP[App.tsx]
    end

    subgraph "Pages"
        INDEX[pages/Index.tsx<br/>Landing/Main Page]
        DEMO[pages/DemoIndex.tsx<br/>Demo Mode]
        NOT_FOUND[pages/NotFound.tsx]
    end

    subgraph "Core Components"
        AUTH_FORM[AuthForm.tsx<br/>Login/Register]
        DASHBOARD[Dashboard.tsx<br/>Insights Display]
        UPLOAD_WIZARD[UploadWizard.tsx<br/>Data Upload]
        HERO[HeroSection.tsx<br/>Landing Page]
    end

    subgraph "UI Components (Shadcn)"
        BUTTON[ui/button.tsx]
        CARD[ui/card.tsx]
        DIALOG[ui/dialog.tsx]
        CHART[ui/chart.tsx]
        FORM[ui/form.tsx]
        TABLE[ui/table.tsx]
        TOAST[ui/toast.tsx]
        MORE[... 40+ components]
    end

    subgraph "Services"
        AUTH_SVC[authService.ts<br/>Authentication]
        INSIGHTS_SVC[insightsService.ts<br/>Insights API]
        UPLOAD_SVC[uploadService.ts<br/>File Upload]
        ANALYSIS_SVC[analysisService.ts<br/>ML Triggers]
    end

    subgraph "Configuration"
        API_CONFIG[config/api.ts<br/>Endpoints]
        DEMO_CONFIG[config/demo.ts<br/>Demo Users]
    end

    subgraph "State Management"
        LOCAL_STATE[Local State<br/>useState]
        SERVER_STATE[React Query<br/>Server State]
    end

    subgraph "Routing"
        ROUTER[React Router<br/>Routes]
    end

    MAIN --> APP
    APP --> ROUTER
    ROUTER --> INDEX
    ROUTER --> DEMO
    ROUTER --> NOT_FOUND

    INDEX --> AUTH_FORM
    INDEX --> DASHBOARD
    INDEX --> UPLOAD_WIZARD
    INDEX --> HERO

    AUTH_FORM --> AUTH_SVC
    DASHBOARD --> INSIGHTS_SVC
    UPLOAD_WIZARD --> UPLOAD_SVC
    DASHBOARD --> ANALYSIS_SVC

    AUTH_FORM --> BUTTON
    AUTH_FORM --> FORM
    DASHBOARD --> CARD
    DASHBOARD --> CHART
    UPLOAD_WIZARD --> DIALOG

    AUTH_SVC --> API_CONFIG
    INSIGHTS_SVC --> API_CONFIG
    AUTH_SVC --> LOCAL_STATE

    DASHBOARD --> SERVER_STATE

    style MAIN fill:#61dafb
    style APP fill:#61dafb
    style AUTH_SVC fill:#4caf50
    style INSIGHTS_SVC fill:#4caf50
    style API_CONFIG fill:#ff9800
```

---

## 5. ML Pipeline Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        GLUCOSE_DATA[(Glucose Readings)]
        SLEEP_DATA[(Sleep Data)]
        MEAL_DATA[(Meal Data)]
        ACTIVITY_DATA[(Activity Data)]
    end

    subgraph "Daily Aggregation"
        AGG_TASK[Celery: aggregate_daily_data<br/>Scheduled 3 AM]
        AGG_COMPUTE[Compute Statistics<br/>- Avg glucose<br/>- TIR %<br/>- Variability<br/>- Sleep hours<br/>- Exercise mins]
        AGG_STORE[(Daily Aggregates)]
    end

    subgraph "Feature Engineering"
        FEATURE_PREP[Prepare Feature Matrix<br/>- Time alignment<br/>- Missing data handling<br/>- Normalization]
        FEATURE_BINARY[Binary Features<br/>- High/low glucose<br/>- Good/poor sleep<br/>- Exercise yes/no]
    end

    subgraph "ML Analysis"
        PCMCI[PCMCI Analysis<br/>Tigramite Library]
        STUMPY[STUMPY Analysis<br/>Matrix Profile]
        ASSOC[Association Rules<br/>Apriori Algorithm]
        CORR[Correlation Analysis<br/>Pearson + p-value]
    end

    subgraph "Results Processing"
        CAUSAL_GRAPH[Causal Graph<br/>DAG Structure]
        PATTERNS[Recurring Patterns<br/>Motifs]
        ANOMALIES[Anomalies<br/>Discords]
        RULES[IF-THEN Rules]
    end

    subgraph "Storage"
        CORR_DB[(Correlations Table)]
        PATTERN_DB[(Patterns Table)]
        CACHE[(Redis Cache<br/>1 hour TTL)]
    end

    subgraph "API Exposure"
        INSIGHTS_API[GET /insights/correlations]
        PATTERNS_API[GET /insights/patterns]
        ADV_API[GET /advanced_insights/*]
    end

    GLUCOSE_DATA --> AGG_TASK
    SLEEP_DATA --> AGG_TASK
    MEAL_DATA --> AGG_TASK
    ACTIVITY_DATA --> AGG_TASK

    AGG_TASK --> AGG_COMPUTE
    AGG_COMPUTE --> AGG_STORE

    AGG_STORE --> FEATURE_PREP
    AGG_STORE --> FEATURE_BINARY

    FEATURE_PREP --> PCMCI
    FEATURE_PREP --> STUMPY
    FEATURE_PREP --> CORR
    FEATURE_BINARY --> ASSOC

    PCMCI --> CAUSAL_GRAPH
    STUMPY --> PATTERNS
    STUMPY --> ANOMALIES
    ASSOC --> RULES
    CORR --> CAUSAL_GRAPH

    CAUSAL_GRAPH --> CORR_DB
    PATTERNS --> PATTERN_DB
    ANOMALIES --> PATTERN_DB
    RULES --> PATTERN_DB

    CORR_DB --> CACHE
    PATTERN_DB --> CACHE

    CACHE --> INSIGHTS_API
    CACHE --> PATTERNS_API
    CACHE --> ADV_API

    style AGG_TASK fill:#4caf50
    style PCMCI fill:#ff9800
    style STUMPY fill:#ff9800
    style ASSOC fill:#ff9800
    style CORR fill:#ff9800
```

---

## 6. Database Schema

```mermaid
erDiagram
    USER ||--o{ GLUCOSE_READING : has
    USER ||--o{ SLEEP_DATA : has
    USER ||--o{ MEAL : has
    USER ||--o{ ACTIVITY : has
    USER ||--o{ DAILY_AGGREGATE : has
    USER ||--o{ CORRELATION : has
    USER ||--o{ PATTERN : has
    USER ||--o{ HBA1C : has
    USER ||--o{ MEDICATION : has
    USER ||--o{ INSULIN_DOSE : has
    USER ||--o{ REFRESH_TOKEN : has

    USER {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        int age
        string gender
        string diabetes_type
        date diagnosis_date
        timestamp created_at
    }

    GLUCOSE_READING {
        int id PK
        uuid user_id FK
        timestamp timestamp
        float value
        string source
        timestamp created_at
    }

    SLEEP_DATA {
        int id PK
        uuid user_id FK
        date date
        timestamp sleep_start
        timestamp sleep_end
        int deep_sleep_minutes
        int rem_sleep_minutes
        int light_sleep_minutes
        float quality_score
    }

    MEAL {
        int id PK
        uuid user_id FK
        timestamp timestamp
        string meal_type
        float carbs_grams
        float protein_grams
        float fat_grams
        int calories
        float glycemic_load
        text description
    }

    ACTIVITY {
        int id PK
        uuid user_id FK
        timestamp timestamp
        string activity_type
        int duration_minutes
        string intensity
        int calories_burned
        int avg_heart_rate
    }

    DAILY_AGGREGATE {
        int id PK
        uuid user_id FK
        date date UK
        float avg_glucose
        float min_glucose
        float max_glucose
        float std_glucose
        float time_in_range_pct
        int total_sleep_minutes
        int total_exercise_minutes
        float total_carbs_grams
    }

    CORRELATION {
        int id PK
        uuid user_id FK
        string factor_x
        string factor_y
        float correlation
        float p_value
        float abs_correlation
        int time_lag_days
        timestamp created_at
    }

    PATTERN {
        int id PK
        uuid user_id FK
        string pattern_type
        text description
        float confidence
        float support
        jsonb metadata
        timestamp created_at
    }

    HBA1C {
        int id PK
        uuid user_id FK
        date test_date
        float value_percent
        string lab_name
    }

    MEDICATION {
        int id PK
        uuid user_id FK
        string name
        string dosage
        string frequency
        boolean is_active
        date start_date
        date end_date
    }

    INSULIN_DOSE {
        int id PK
        uuid user_id FK
        timestamp timestamp
        string insulin_type
        float units
        string dose_type
    }

    REFRESH_TOKEN {
        int id PK
        uuid user_id FK
        string token UK
        timestamp expires_at
        boolean is_revoked
    }
```

---

## 7. Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant DB as Database
    participant AUTH as Auth Utils

    rect rgb(200, 220, 240)
        Note over U,AUTH: Registration Flow
        U->>FE: Enter email & password
        FE->>API: POST /api/v1/auth/register
        API->>AUTH: Hash password
        AUTH-->>API: Hashed password
        API->>DB: Create user record
        DB-->>API: User created
        API->>AUTH: Generate JWT tokens
        AUTH-->>API: Access token (30 min)<br/>Refresh token (7 days)
        API->>DB: Store refresh token
        API-->>FE: {access_token, refresh_token, user}
        FE->>FE: Store tokens in localStorage
        FE-->>U: Redirect to dashboard
    end

    rect rgb(220, 240, 200)
        Note over U,AUTH: Login Flow
        U->>FE: Enter credentials
        FE->>API: POST /api/v1/auth/login
        API->>DB: Find user by email
        DB-->>API: User record
        API->>AUTH: Verify password
        AUTH-->>API: Password valid
        API->>AUTH: Generate JWT tokens
        AUTH-->>API: Access & refresh tokens
        API->>DB: Store refresh token
        API-->>FE: {access_token, refresh_token, user}
        FE->>FE: Store in localStorage
        FE-->>U: Redirect to dashboard
    end

    rect rgb(240, 220, 200)
        Note over U,AUTH: Protected API Call
        U->>FE: View dashboard
        FE->>FE: Get access token from localStorage
        FE->>API: GET /api/v1/insights<br/>Authorization: Bearer {token}
        API->>AUTH: Verify JWT token
        AUTH-->>API: Valid user_id
        API->>DB: Query user data
        DB-->>API: Data
        API-->>FE: Response
        FE-->>U: Display insights
    end

    rect rgb(240, 200, 220)
        Note over U,AUTH: Token Refresh
        FE->>API: GET /api/v1/insights<br/>(Expired token)
        API-->>FE: 401 Unauthorized
        FE->>FE: Get refresh token
        FE->>API: POST /api/v1/auth/refresh<br/>{refresh_token}
        API->>DB: Verify refresh token
        DB-->>API: Token valid
        API->>AUTH: Generate new access token
        AUTH-->>API: New access token
        API-->>FE: {access_token}
        FE->>FE: Update localStorage
        FE->>API: Retry original request with new token
        API-->>FE: Success
    end
```

---

## 8. Data Flow

```mermaid
graph TB
    subgraph "User Actions"
        UPLOAD[Upload CSV Files]
        VIEW[View Dashboard]
        TRIGGER[Trigger Analysis]
    end

    subgraph "Frontend Processing"
        VALIDATE[Validate Files]
        PARSE[Parse CSV]
        DISPLAY[Display Results]
    end

    subgraph "API Endpoints"
        BULK_API[POST /glucose/bulk]
        INSIGHTS_API[GET /insights/*]
        TRIGGER_API[POST /insights/trigger]
    end

    subgraph "Backend Processing"
        VALIDATE_DATA[Validate Data]
        STORE_RAW[Store Raw Data]
        QUEUE_TASK[Queue Celery Task]
    end

    subgraph "Background Tasks"
        AGG[Daily Aggregation]
        ML[ML Analysis Pipeline]
    end

    subgraph "ML Processing"
        COMPUTE[Compute Features]
        PCMCI_RUN[Run PCMCI]
        STUMPY_RUN[Run STUMPY]
        STORE_INSIGHTS[Store Insights]
    end

    subgraph "Data Storage"
        RAW_DB[(Raw Data<br/>glucose_readings)]
        AGG_DB[(Aggregates<br/>daily_aggregates)]
        INSIGHTS_DB[(Insights<br/>correlations, patterns)]
        CACHE[(Redis Cache)]
    end

    subgraph "Results Delivery"
        FETCH_INSIGHTS[Fetch from Cache/DB]
        FORMAT[Format Response]
        RENDER[Render Charts]
    end

    UPLOAD --> VALIDATE
    VALIDATE --> PARSE
    PARSE --> BULK_API
    BULK_API --> VALIDATE_DATA
    VALIDATE_DATA --> STORE_RAW
    STORE_RAW --> RAW_DB
    STORE_RAW --> QUEUE_TASK

    QUEUE_TASK --> AGG
    QUEUE_TASK --> ML

    AGG --> RAW_DB
    AGG --> AGG_DB

    TRIGGER --> TRIGGER_API
    TRIGGER_API --> ML

    ML --> COMPUTE
    COMPUTE --> AGG_DB
    COMPUTE --> PCMCI_RUN
    COMPUTE --> STUMPY_RUN
    PCMCI_RUN --> STORE_INSIGHTS
    STUMPY_RUN --> STORE_INSIGHTS
    STORE_INSIGHTS --> INSIGHTS_DB
    STORE_INSIGHTS --> CACHE

    VIEW --> INSIGHTS_API
    INSIGHTS_API --> FETCH_INSIGHTS
    FETCH_INSIGHTS --> CACHE
    CACHE -.->|Cache miss| INSIGHTS_DB
    FETCH_INSIGHTS --> FORMAT
    FORMAT --> DISPLAY
    DISPLAY --> RENDER

    style UPLOAD fill:#61dafb
    style VIEW fill:#61dafb
    style PCMCI_RUN fill:#ff9800
    style STUMPY_RUN fill:#ff9800
    style RAW_DB fill:#336791
    style INSIGHTS_DB fill:#336791
    style CACHE fill:#dc382d
```

---

## 9. Deployment Architecture

### 9.1 Docker Compose (Development/MVP)

```mermaid
graph TB
    subgraph "Host Machine"
        subgraph "Docker Network"
            NGINX[Nginx Reverse Proxy<br/>:80, :443]

            subgraph "Frontend Container"
                VITE[Vite Dev Server<br/>:8080]
            end

            subgraph "Backend Container"
                API[FastAPI<br/>uvicorn :8000]
            end

            subgraph "Database Container"
                TIMESCALE[(TimescaleDB<br/>:5432)]
            end

            subgraph "Cache Container"
                REDIS_SVC[(Redis<br/>:6379)]
            end

            subgraph "Worker Containers"
                CELERY_W[Celery Worker]
                CELERY_B[Celery Beat]
            end
        end

        subgraph "Volumes"
            DB_VOL[timescale_data]
            REDIS_VOL[redis_data]
        end
    end

    NGINX --> VITE
    NGINX --> API
    API --> TIMESCALE
    API --> REDIS_SVC
    CELERY_W --> TIMESCALE
    CELERY_W --> REDIS_SVC
    CELERY_B --> REDIS_SVC
    TIMESCALE --> DB_VOL
    REDIS_SVC --> REDIS_VOL

    style NGINX fill:#009688
    style API fill:#009688
    style TIMESCALE fill:#336791
    style REDIS_SVC fill:#dc382d
```

### 9.2 AWS Lambda (Read-Only Demo Deployment)

**Purpose:** Serverless read-only demo with pre-loaded data (3 demo users, 90 days of synthetic data)

**Key Features:**
- No authentication required (demo mode)
- GET endpoints only (read-only)
- Pre-computed ML insights (PCMCI, STUMPY, association rules)
- Global CDN distribution via CloudFront
- Auto-scaling with Lambda
- Cost: ~$50/month (optimizable to $15-20)

```mermaid
graph TB
    subgraph "Users"
        BROWSER[Web Browser]
    end

    subgraph "AWS Cloud"
        subgraph "Edge Layer - Global CDN"
            CF[CloudFront Distribution<br/>SSL, Caching, Compression]
        end

        subgraph "Static Assets - S3"
            S3[S3 Bucket<br/>React Demo Frontend<br/>DemoIndex + DemoDashboard]
        end

        subgraph "API Layer - API Gateway"
            APIGW[API Gateway REST API<br/>CORS Enabled<br/>/Prod Stage]
        end

        subgraph "Compute Layer - Lambda Functions"
            LF[Lambda Function<br/>glucolens-demo-DemoFunction<br/>512MB, 30s timeout<br/>Mangum Handler]
        end

        subgraph "Endpoints Handled by Lambda"
            E1[GET /users]
            E2[GET /insights/:userId]
            E3[GET /correlations/:userId]
            E4[GET /patterns/:userId]
            E5[GET /dashboard/:userId]
            E6[GET /glucose/readings/:userId]
        end

        subgraph "VPC - Database Tier"
            subgraph "Aurora Cluster"
                AURORA[(Aurora Serverless v2<br/>PostgreSQL + TimescaleDB<br/>0.5-1 ACU, Auto-pause)]
            end
        end

        subgraph "Monitoring & Logging"
            CW[CloudWatch Logs<br/>7-day retention]
            ALARM1[Error Alarm<br/>> 5 errors/5min]
            ALARM2[Throttle Alarm<br/>> 10 throttles/5min]
        end

        subgraph "Infrastructure as Code"
            SAM[AWS SAM Template<br/>template.yaml]
            GHA[GitHub Actions<br/>CI/CD Pipeline]
        end

        subgraph "Demo Data - 3 Profiles"
            ALICE[Alice Thompson<br/>11111111...<br/>Well-controlled]
            BOB[Bob Martinez<br/>22222222...<br/>Variable]
            CAROL[Carol Chen<br/>33333333...<br/>Active]
        end
    end

    BROWSER --> CF
    CF --> S3
    CF --> APIGW
    S3 -.->|Contains| DemoIndex
    S3 -.->|Contains| DemoDashboard

    APIGW --> LF
    LF --> E1
    LF --> E2
    LF --> E3
    LF --> E4
    LF --> E5
    LF --> E6

    E1 --> AURORA
    E2 --> AURORA
    E3 --> AURORA
    E4 --> AURORA
    E5 --> AURORA
    E6 --> AURORA

    AURORA -.->|Contains| ALICE
    AURORA -.->|Contains| BOB
    AURORA -.->|Contains| CAROL

    LF --> CW
    CW --> ALARM1
    CW --> ALARM2

    SAM -.->|Deploys| APIGW
    SAM -.->|Deploys| LF
    SAM -.->|Deploys| CW
    GHA -.->|Executes| SAM

    style CF fill:#ff9900,stroke:#333,stroke-width:2px
    style S3 fill:#ff9900,stroke:#333,stroke-width:2px
    style APIGW fill:#ff9900,stroke:#333,stroke-width:2px
    style LF fill:#ff9900,stroke:#333,stroke-width:2px
    style AURORA fill:#336791,stroke:#333,stroke-width:2px
    style CW fill:#ff9900,stroke:#333,stroke-width:2px
    style ALICE fill:#4caf50,stroke:#333,stroke-width:2px
    style BOB fill:#ff9800,stroke:#333,stroke-width:2px
    style CAROL fill:#2196f3,stroke:#333,stroke-width:2px
```

**Data Flow:**
1. User visits demo URL (CloudFront)
2. CloudFront serves React frontend from S3
3. User selects demo profile (Alice/Bob/Carol)
4. Frontend calls API Gateway endpoints
5. API Gateway triggers Lambda function
6. Lambda queries Aurora Serverless for demo data
7. Pre-computed insights returned to frontend
8. Dashboard renders with charts and visualizations

**Deployment Steps:**
1. `sam build --use-container` (Build Lambda package)
2. `sam deploy` (Deploy infrastructure)
3. `python scripts/generate_demo_users.py` (Generate demo data)
4. `npm run build` (Build frontend with `VITE_DEMO_MODE=true`)
5. `aws s3 sync dist/ s3://bucket/` (Deploy frontend)
6. `aws cloudfront create-invalidation` (Clear CDN cache)

See `AWS_DEPLOYMENT_CHECKLIST.md` for full deployment guide.

### 9.3 Kubernetes (Production Scale)

```mermaid
graph TB
    subgraph "External"
        LB[Cloud Load Balancer<br/>SSL Termination]
    end

    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            INGRESS[Nginx Ingress<br/>Controller]
        end

        subgraph "Frontend Deployment"
            FE1[Frontend Pod 1]
            FE2[Frontend Pod 2]
            FE3[Frontend Pod 3]
        end

        subgraph "Backend Deployment"
            API1[API Pod 1]
            API2[API Pod 2]
            API3[API Pod 3]
        end

        subgraph "Worker Deployment"
            W1[Celery Worker 1]
            W2[Celery Worker 2]
            W3[Celery Worker 3]
        end

        subgraph "Beat Deployment"
            BEAT[Celery Beat Pod]
        end

        subgraph "Services"
            FE_SVC[Frontend Service]
            API_SVC[API Service]
        end
    end

    subgraph "External Services"
        RDS[(RDS TimescaleDB<br/>Multi-AZ)]
        ELASTICACHE[(ElastiCache Redis<br/>Cluster)]
    end

    subgraph "Monitoring"
        PROM[Prometheus]
        GRAF[Grafana]
    end

    LB --> INGRESS
    INGRESS --> FE_SVC
    INGRESS --> API_SVC
    FE_SVC --> FE1
    FE_SVC --> FE2
    FE_SVC --> FE3
    API_SVC --> API1
    API_SVC --> API2
    API_SVC --> API3
    API1 --> RDS
    API2 --> RDS
    API3 --> RDS
    API1 --> ELASTICACHE
    W1 --> RDS
    W2 --> RDS
    W3 --> RDS
    W1 --> ELASTICACHE
    W2 --> ELASTICACHE
    BEAT --> ELASTICACHE

    API1 --> PROM
    API2 --> PROM
    API3 --> PROM
    PROM --> GRAF

    style INGRESS fill:#009688
    style API1 fill:#009688
    style API2 fill:#009688
    style API3 fill:#009688
    style RDS fill:#336791
    style ELASTICACHE fill:#dc382d
```

---

## Component Legend

**Colors:**
- 🔵 **Blue (#61dafb)** - Frontend components
- 🟢 **Green (#009688)** - Backend API/servers
- 🔴 **Red (#dc382d)** - Redis/caching
- 🟣 **Purple (#336791)** - Databases
- 🟠 **Orange (#ff9800)** - ML services/AWS services
- 🟢 **Green (#4caf50)** - Services/utilities

**Shapes:**
- Rectangle - Components/services
- Cylinder - Databases/storage
- Circle - External services
- Diamond - Decision points

---

## Using These Diagrams

1. **For Development:** Reference component diagrams to understand code organization
2. **For Deployment:** Use deployment diagrams to set up infrastructure
3. **For Documentation:** Copy diagrams into presentations or technical docs
4. **For Onboarding:** Walk new team members through the architecture

---

## Updating Diagrams

When adding new features:
1. Update relevant component diagram
2. Update integration diagram if new connections
3. Update data flow if new data paths
4. Regenerate from this markdown file

All diagrams use Mermaid syntax and render automatically on GitHub, GitLab, and most documentation platforms.

---

**Last Updated:** 2025-01-15
**Maintained By:** Development Team
