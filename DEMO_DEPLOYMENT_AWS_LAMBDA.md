# GlucoLens Demo Deployment - AWS Lambda (Read-Only)

Complete guide for deploying a **read-only demonstration** of GlucoLens using AWS Lambda and serverless technologies with pre-generated synthetic data.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Cost Estimates](#cost-estimates)
4. [Prerequisites](#prerequisites)
5. [Step 1: Prepare Demo Data](#step-1-prepare-demo-data)
6. [Step 2: Setup AWS Infrastructure](#step-2-setup-aws-infrastructure)
7. [Step 3: Deploy Backend (Lambda)](#step-3-deploy-backend-lambda)
8. [Step 4: Deploy Frontend (S3 + CloudFront)](#step-4-deploy-frontend-s3--cloudfront)
9. [Step 5: Configure & Test](#step-5-configure--test)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Transition to Full Product](#transition-to-full-product)

---

## Overview

### Purpose
Deploy a **read-only demo** of GlucoLens to showcase the ML-powered insights platform to potential users and investors **without** the complexity of user authentication, data ingestion, or multi-user support.

### What's Included
- ✅ **Pre-generated synthetic data** (3 demo user profiles)
- ✅ **ML insights** (PCMCI, STUMPY, correlations, patterns)
- ✅ **Interactive dashboard** (React frontend)
- ✅ **Read-only API** (GET endpoints only)
- ❌ No user registration/login
- ❌ No data upload capability
- ❌ No user-specific data (shared demo data)

### Use Cases
1. **Investor demos** - Show the product vision
2. **User research** - Get feedback on UX/insights
3. **Marketing** - Public demo on website
4. **Beta recruitment** - Show what users will get

---

## Architecture

### Serverless Demo Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Internet Users                        │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              CloudFront CDN (Global)                     │
│         - Frontend static files (React build)            │
│         - SSL certificate (*.yourdomain.com)             │
│         - Edge caching                                   │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌────────▼──────────┐
│   S3 Bucket    │            │   API Gateway     │
│  (Frontend)    │            │   (REST API)      │
│  - index.html  │            │   /api/v1/*       │
│  - JS bundles  │            └────────┬──────────┘
│  - CSS         │                     │
└────────────────┘            ┌────────▼──────────────────────┐
                              │   Lambda Functions            │
                              │  ┌─────────────────────────┐  │
                              │  │ GET /insights           │  │
                              │  │ GET /correlations       │  │
                              │  │ GET /patterns           │  │
                              │  │ GET /dashboard          │  │
                              │  │ GET /glucose/readings   │  │
                              │  └─────────────────────────┘  │
                              └────────┬──────────────────────┘
                                       │
                              ┌────────▼──────────────────────┐
                              │   RDS Aurora Serverless v2    │
                              │   (PostgreSQL 15)             │
                              │  ┌─────────────────────────┐  │
                              │  │ Pre-seeded demo data:   │  │
                              │  │ - 3 demo users          │  │
                              │  │ - 90 days glucose       │  │
                              │  │ - Sleep/meals/exercise  │  │
                              │  │ - Pre-computed insights │  │
                              │  └─────────────────────────┘  │
                              └───────────────────────────────┘
```

### Simplified Data Flow

```
User opens demo URL
  → CloudFront serves React app
    → User selects demo profile (Alice, Bob, or Carol)
      → Frontend calls Lambda API
        → Lambda queries Aurora DB (read-only)
          → Returns pre-computed insights
            → Frontend displays charts & patterns
```

---

## Cost Estimates

### Monthly Cost Breakdown (Estimated)

**Assumes:** 1,000 demo sessions/month, 5 API calls per session

| Service | Usage | Cost |
|---------|-------|------|
| **S3 (Frontend)** | 1 GB storage, 10 GB transfer | $0.50 |
| **CloudFront** | 10 GB transfer | $1.00 |
| **API Gateway** | 5,000 requests | $0.02 |
| **Lambda** | 5,000 invocations, 512 MB, 2s avg | $0.10 |
| **Aurora Serverless v2** | 0.5 ACU (min), mostly idle | $43.80 |
| **Route 53** | Hosted zone + DNS queries | $0.50 |
| **Certificate Manager** | SSL certificate | $0.00 |
| **CloudWatch Logs** | Basic monitoring | $5.00 |
| **TOTAL** | | **~$50.92/month** |

**Cost Optimization:**
- Use Aurora Serverless v2 with min 0.5 ACU (scales to zero when idle)
- Enable CloudFront caching (reduce Lambda calls)
- Set short Lambda timeout (5 seconds max)
- Use S3 Intelligent Tiering

**Alternative (Even Cheaper - ~$15/month):**
- Replace Aurora with **Amazon RDS Proxy + RDS db.t4g.micro** ($15/mo)
- Or use **DynamoDB** for NoSQL storage ($5/mo)

---

## Prerequisites

### Required AWS Services
- AWS Account with billing enabled
- AWS CLI installed and configured
- Domain name (optional, but recommended)

### Required Tools
- **Node.js 18+** and npm
- **Python 3.11+**
- **AWS CLI** v2
- **AWS SAM CLI** (for Lambda deployment)
- **Git**

### Install AWS SAM CLI

```bash
# macOS
brew install aws-sam-cli

# Linux
pip install aws-sam-cli

# Windows
# Download from: https://aws.amazon.com/serverless/sam/

# Verify installation
sam --version
```

### Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format: json
```

---

## Step 1: Prepare Demo Data

### 1.1 Generate Synthetic Data Locally

```bash
# Start local database
docker-compose up -d timescaledb

# Run migrations
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /migrations/init.sql
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /migrations/mvp2_schema.sql
docker-compose exec timescaledb psql -U glucolens -d glucolens -f /migrations/health_data_additions.sql

# Create hypertable
docker-compose exec timescaledb psql -U glucolens -d glucolens -c \
  "SELECT create_hypertable('glucose_readings', 'timestamp', if_not_exists => TRUE);"

# Generate data for 3 demo users
docker-compose exec api python scripts/generate_demo_users.py
```

### 1.2 Create Demo User Script

**File:** `backend/scripts/generate_demo_users.py`

```python
"""
Generate 3 demo user profiles with realistic data for read-only demo.
"""
import asyncio
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import async_session_maker
from app.models.user import User
from app.utils.auth import get_password_hash
import subprocess

# Demo user profiles
DEMO_USERS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "alice@demo.glucolens.com",
        "full_name": "Alice Thompson",
        "age": 34,
        "gender": "female",
        "diabetes_type": "type_1",
        "profile": "well_controlled",  # Stable glucose, good sleep
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "bob@demo.glucolens.com",
        "full_name": "Bob Martinez",
        "age": 52,
        "gender": "male",
        "diabetes_type": "type_2",
        "profile": "variable",  # Variable glucose, stress patterns
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "email": "carol@demo.glucolens.com",
        "full_name": "Carol Chen",
        "age": 28,
        "gender": "female",
        "diabetes_type": "type_1",
        "profile": "active",  # Active lifestyle, exercise impact
    },
]

async def create_demo_users():
    """Create demo users in database."""
    async with async_session_maker() as session:
        for user_data in DEMO_USERS:
            user = User(
                id=UUID(user_data["id"]),
                email=user_data["email"],
                hashed_password=get_password_hash("demo123"),  # Not used in read-only
                full_name=user_data["full_name"],
                age=user_data["age"],
                gender=user_data["gender"],
                diabetes_type=user_data["diabetes_type"],
                diagnosis_date=datetime.now() - timedelta(days=365 * 5),
                timezone="America/New_York",
            )
            session.add(user)

        await session.commit()
        print(f"✅ Created {len(DEMO_USERS)} demo users")

def generate_data_for_user(user_id: str, profile: str):
    """Generate 90 days of data for a user using existing script."""
    print(f"Generating data for user {user_id} ({profile} profile)...")

    subprocess.run([
        "python", "scripts/generate_sample_data.py",
        "--days", "90",
        "--user-id", user_id,
        "--profile", profile
    ], check=True)

async def run_ml_analysis():
    """Run ML analysis to pre-compute insights."""
    print("Running ML analysis pipeline...")

    subprocess.run([
        "python", "scripts/run_ml_pipeline.py"
    ], check=True)

async def main():
    print("🚀 Generating demo data for GlucoLens...")

    # Step 1: Create users
    await create_demo_users()

    # Step 2: Generate data for each user
    for user_data in DEMO_USERS:
        generate_data_for_user(user_data["id"], user_data["profile"])

    # Step 3: Run ML analysis
    await run_ml_analysis()

    print("✅ Demo data generation complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

### 1.3 Export Demo Database

```bash
# Dump demo data
docker-compose exec timescaledb pg_dump -U glucolens -d glucolens \
  --data-only --inserts > demo_data.sql

# Verify file size
ls -lh demo_data.sql
```

---

## Step 2: Setup AWS Infrastructure

### 2.1 Create Aurora Serverless Database

**Via AWS Console:**

1. Go to **RDS** → **Create Database**
2. Choose **Aurora (PostgreSQL Compatible)**
3. Select **Serverless v2**
4. Settings:
   - DB cluster identifier: `glucolens-demo`
   - Master username: `glucolens`
   - Master password: (generate secure password)
   - Capacity: Min 0.5 ACU, Max 1 ACU
5. Connectivity:
   - VPC: Default VPC
   - Public access: **No** (Lambda will access via VPC)
   - VPC security group: Create new `glucolens-db-sg`
6. Create database

**Via AWS CLI:**

```bash
# Create DB cluster
aws rds create-db-cluster \
  --db-cluster-identifier glucolens-demo \
  --engine aurora-postgresql \
  --engine-version 15.4 \
  --engine-mode provisioned \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=1 \
  --master-username glucolens \
  --master-user-password YOUR_SECURE_PASSWORD \
  --database-name glucolens

# Create DB instance
aws rds create-db-instance \
  --db-instance-identifier glucolens-demo-instance-1 \
  --db-instance-class db.serverless \
  --engine aurora-postgresql \
  --db-cluster-identifier glucolens-demo
```

### 2.2 Setup VPC Security Group

```bash
# Get VPC ID
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" --output text)

# Create security group for Lambda
aws ec2 create-security-group \
  --group-name glucolens-lambda-sg \
  --description "Security group for GlucoLens Lambda functions" \
  --vpc-id $VPC_ID

LAMBDA_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=glucolens-lambda-sg" \
  --query "SecurityGroups[0].GroupId" --output text)

# Get DB security group
DB_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=glucolens-db-sg" \
  --query "SecurityGroups[0].GroupId" --output text)

# Allow Lambda to access DB (port 5432)
aws ec2 authorize-security-group-ingress \
  --group-id $DB_SG_ID \
  --protocol tcp \
  --port 5432 \
  --source-group $LAMBDA_SG_ID
```

### 2.3 Load Demo Data into Aurora

```bash
# Get Aurora endpoint
DB_ENDPOINT=$(aws rds describe-db-clusters \
  --db-cluster-identifier glucolens-demo \
  --query "DBClusters[0].Endpoint" --output text)

# Connect to database (from EC2 instance or Cloud9)
psql -h $DB_ENDPOINT -U glucolens -d glucolens

# In psql, load schema and data
\i migrations/init.sql
\i migrations/mvp2_schema.sql
\i migrations/health_data_additions.sql
\i demo_data.sql

# Create hypertable
SELECT create_hypertable('glucose_readings', 'timestamp', if_not_exists => TRUE);

# Verify data
SELECT COUNT(*) FROM users;  -- Should be 3
SELECT COUNT(*) FROM glucose_readings;
SELECT COUNT(*) FROM correlations;
SELECT COUNT(*) FROM patterns;
```

---

## Step 3: Deploy Backend (Lambda)

### 3.1 Create SAM Template

**File:** `backend/template.yaml`

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: GlucoLens Demo - Read-Only API

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.11
    Environment:
      Variables:
        DATABASE_URL: !Sub 'postgresql+asyncpg://glucolens:${DBPassword}@${DBEndpoint}:5432/glucolens'
        ENVIRONMENT: production
    VpcConfig:
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

Parameters:
  DBEndpoint:
    Type: String
    Description: Aurora database endpoint

  DBPassword:
    Type: String
    NoEcho: true
    Description: Database password

Resources:
  # API Gateway
  GlucoLensAPI:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Cors:
        AllowOrigin: "'*'"
        AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'"
        AllowMethods: "'GET,OPTIONS'"

  # Lambda Functions
  GetInsightsFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: app.lambda.insights_handler
      Events:
        GetInsights:
          Type: Api
          Properties:
            RestApiId: !Ref GlucoLensAPI
            Path: /insights/{user_id}
            Method: GET

  GetCorrelationsFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: app.lambda.correlations_handler
      Events:
        GetCorrelations:
          Type: Api
          Properties:
            RestApiId: !Ref GlucoLensAPI
            Path: /correlations/{user_id}
            Method: GET

  GetPatternsFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: app.lambda.patterns_handler
      Events:
        GetPatterns:
          Type: Api
          Properties:
            RestApiId: !Ref GlucoLensAPI
            Path: /patterns/{user_id}
            Method: GET

  GetDashboardFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: app.lambda.dashboard_handler
      Events:
        GetDashboard:
          Type: Api
          Properties:
            RestApiId: !Ref GlucoLensAPI
            Path: /dashboard/{user_id}
            Method: GET

  GetGlucoseReadingsFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: app.lambda.glucose_handler
      Events:
        GetReadings:
          Type: Api
          Properties:
            RestApiId: !Ref GlucoLensAPI
            Path: /glucose/readings/{user_id}
            Method: GET

  # Security Group for Lambda
  LambdaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Lambda functions
      VpcId: !Ref VPC

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${GlucoLensAPI}.execute-api.${AWS::Region}.amazonaws.com/prod/'
```

### 3.2 Create Lambda Handlers

**File:** `backend/app/lambda.py`

```python
"""
Lambda function handlers for read-only demo API.
Simplified - no authentication, only GET operations.
"""
import json
from mangum import Mangum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.config import async_session_maker
from app.models.user import User
from app.models.correlation import Correlation
from app.models.pattern import Pattern
from app.models.aggregate import DailyAggregate
from app.models.glucose import GlucoseReading

# Create simplified FastAPI app
app = FastAPI(title="GlucoLens Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo only - restrict in production
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/users")
async def get_demo_users():
    """Get list of demo user profiles."""
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        return [
            {
                "id": str(user.id),
                "full_name": user.full_name,
                "age": user.age,
                "diabetes_type": user.diabetes_type,
            }
            for user in users
        ]

@app.get("/insights/{user_id}")
async def get_insights(user_id: str):
    """Get insights summary for a demo user."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    async with async_session_maker() as session:
        # Get top correlations
        corr_query = select(Correlation).where(
            Correlation.user_id == user_uuid
        ).order_by(Correlation.abs_correlation.desc()).limit(10)
        corr_result = await session.execute(corr_query)
        correlations = corr_result.scalars().all()

        # Get patterns
        pattern_query = select(Pattern).where(
            Pattern.user_id == user_uuid
        ).order_by(Pattern.confidence.desc()).limit(10)
        pattern_result = await session.execute(pattern_query)
        patterns = pattern_result.scalars().all()

        return {
            "user_id": user_id,
            "correlations": [
                {
                    "factor_x": c.factor_x,
                    "factor_y": c.factor_y,
                    "correlation": c.correlation,
                    "p_value": c.p_value,
                }
                for c in correlations
            ],
            "patterns": [
                {
                    "description": p.description,
                    "confidence": p.confidence,
                    "support": p.support,
                    "pattern_type": p.pattern_type,
                }
                for p in patterns
            ],
        }

@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str, period_days: int = 7):
    """Get dashboard summary."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    from datetime import datetime, timedelta

    async with async_session_maker() as session:
        # Get recent aggregates
        start_date = datetime.now().date() - timedelta(days=period_days)

        agg_query = select(DailyAggregate).where(
            DailyAggregate.user_id == user_uuid,
            DailyAggregate.date >= start_date
        ).order_by(DailyAggregate.date.desc())

        agg_result = await session.execute(agg_query)
        aggregates = agg_result.scalars().all()

        return {
            "user_id": user_id,
            "period_days": period_days,
            "summary": {
                "avg_glucose": sum(a.avg_glucose for a in aggregates) / len(aggregates) if aggregates else 0,
                "time_in_range_pct": sum(a.time_in_range_pct for a in aggregates) / len(aggregates) if aggregates else 0,
                "avg_sleep_hours": sum(a.total_sleep_minutes or 0 for a in aggregates) / 60 / len(aggregates) if aggregates else 0,
            },
            "daily_data": [
                {
                    "date": str(a.date),
                    "avg_glucose": a.avg_glucose,
                    "time_in_range_pct": a.time_in_range_pct,
                    "total_sleep_minutes": a.total_sleep_minutes,
                }
                for a in aggregates
            ],
        }

@app.get("/glucose/readings/{user_id}")
async def get_glucose_readings(
    user_id: str,
    limit: int = 288  # 24 hours at 5-min intervals
):
    """Get recent glucose readings."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    async with async_session_maker() as session:
        query = select(GlucoseReading).where(
            GlucoseReading.user_id == user_uuid
        ).order_by(GlucoseReading.timestamp.desc()).limit(limit)

        result = await session.execute(query)
        readings = result.scalars().all()

        return {
            "user_id": user_id,
            "count": len(readings),
            "readings": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "value": r.value,
                    "source": r.source,
                }
                for r in reversed(readings)  # Return chronological order
            ],
        }

# Mangum handler for Lambda
handler = Mangum(app)
```

### 3.3 Update Requirements for Lambda

**File:** `backend/requirements-lambda.txt`

```txt
fastapi==0.104.1
mangum==0.17.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

### 3.4 Deploy with SAM

```bash
cd backend

# Build Lambda package
sam build

# Deploy (first time - guided)
sam deploy --guided

# Answer prompts:
# - Stack name: glucolens-demo
# - AWS Region: us-east-1
# - Parameter DBEndpoint: (paste Aurora endpoint)
# - Parameter DBPassword: (paste DB password)
# - Confirm changes before deploy: Y
# - Allow SAM CLI IAM role creation: Y
# - Save arguments to config file: Y

# Subsequent deploys (uses saved config)
sam deploy
```

### 3.5 Test Lambda API

```bash
# Get API endpoint from SAM output
API_ENDPOINT="https://xxxxx.execute-api.us-east-1.amazonaws.com/prod"

# Test health
curl $API_ENDPOINT/health

# Get demo users
curl $API_ENDPOINT/users

# Get insights for Alice
curl $API_ENDPOINT/insights/11111111-1111-1111-1111-111111111111

# Get dashboard
curl "$API_ENDPOINT/dashboard/11111111-1111-1111-1111-111111111111?period_days=7"
```

---

## Step 4: Deploy Frontend (S3 + CloudFront)

### 4.1 Update Frontend for Demo Mode

**File:** `src/config/demo.ts`

```typescript
export const DEMO_MODE = true;

export const DEMO_USERS = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    name: 'Alice Thompson',
    age: 34,
    diabetesType: 'Type 1',
    description: 'Well-controlled glucose with consistent sleep patterns',
    avatar: '👩‍⚕️',
  },
  {
    id: '22222222-2222-2222-2222-222222222222',
    name: 'Bob Martinez',
    age: 52,
    diabetesType: 'Type 2',
    description: 'Variable glucose levels with stress-related patterns',
    avatar: '👨‍💼',
  },
  {
    id: '33333333-3333-3333-3333-333333333333',
    name: 'Carol Chen',
    age: 28,
    diabetesType: 'Type 1',
    description: 'Active lifestyle with clear exercise impact',
    avatar: '👩‍🏫',
  },
];

export const API_BASE_URL = 'https://xxxxx.execute-api.us-east-1.amazonaws.com/prod';
```

**File:** `src/pages/DemoIndex.tsx`

```typescript
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dashboard } from '@/components/Dashboard';
import { DEMO_USERS } from '@/config/demo';

export const DemoIndex = () => {
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  if (selectedUser) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b p-4">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary">GlucoLens Demo</h1>
            <Button variant="outline" onClick={() => setSelectedUser(null)}>
              ← Change Profile
            </Button>
          </div>
        </header>
        <Dashboard userId={selectedUser} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-8">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            GlucoLens Interactive Demo
          </h1>
          <p className="text-xl text-gray-600">
            Explore AI-powered glucose insights with our demo profiles
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {DEMO_USERS.map((user) => (
            <Card
              key={user.id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedUser(user.id)}
            >
              <CardHeader>
                <div className="text-6xl text-center mb-4">{user.avatar}</div>
                <CardTitle>{user.name}</CardTitle>
                <CardDescription>
                  {user.age} years old • {user.diabetesType}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">{user.description}</p>
                <Button className="w-full">View Dashboard</Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-12 text-center text-sm text-gray-500">
          <p>
            This is a demonstration with synthetic data.{' '}
            <a href="#contact" className="text-primary underline">
              Sign up
            </a>{' '}
            for the beta to use with your own data.
          </p>
        </div>
      </div>
    </div>
  );
};
```

**Update:** `src/main.tsx`

```typescript
import { DemoIndex } from './pages/DemoIndex';
import { DEMO_MODE } from './config/demo';

// Use DemoIndex for demo deployment
root.render(
  <React.StrictMode>
    {DEMO_MODE ? <DemoIndex /> : <Index />}
  </React.StrictMode>
);
```

### 4.2 Build Frontend

```bash
# Update API endpoint in src/config/demo.ts with your Lambda API URL

# Build for production
npm run build

# Output will be in dist/
ls -lh dist/
```

### 4.3 Create S3 Bucket

```bash
# Create bucket (must be globally unique name)
aws s3 mb s3://glucolens-demo-frontend

# Enable static website hosting
aws s3 website s3://glucolens-demo-frontend \
  --index-document index.html \
  --error-document index.html

# Upload build files
aws s3 sync dist/ s3://glucolens-demo-frontend/ \
  --delete \
  --cache-control "public, max-age=31536000" \
  --exclude "index.html"

# Upload index.html separately (no cache)
aws s3 cp dist/index.html s3://glucolens-demo-frontend/index.html \
  --cache-control "no-cache"

# Set bucket policy for public read
aws s3api put-bucket-policy \
  --bucket glucolens-demo-frontend \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::glucolens-demo-frontend/*"
    }]
  }'
```

### 4.4 Setup CloudFront Distribution

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name glucolens-demo-frontend.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html

# Get distribution ID from output
DISTRIBUTION_ID="E1234567890ABC"

# Wait for deployment (takes 5-10 minutes)
aws cloudfront wait distribution-deployed \
  --id $DISTRIBUTION_ID

# Get CloudFront URL
aws cloudfront get-distribution \
  --id $DISTRIBUTION_ID \
  --query "Distribution.DomainName" \
  --output text

# Example output: d111111abcdef8.cloudfront.net
```

### 4.5 Configure Custom Domain (Optional)

```bash
# Request SSL certificate (us-east-1 required for CloudFront)
aws acm request-certificate \
  --domain-name demo.yourdomain.com \
  --validation-method DNS \
  --region us-east-1

# Follow email/DNS validation

# Update CloudFront to use custom domain
# (Use AWS Console - easier for SSL configuration)
```

---

## Step 5: Configure & Test

### 5.1 Test Full Flow

1. **Open demo URL:** `https://d111111abcdef8.cloudfront.net`
2. **Select demo profile:** Click on Alice, Bob, or Carol
3. **View dashboard:** Should see glucose chart, correlations, patterns
4. **Check browser console:** Look for API calls to Lambda
5. **Verify data:** Check that insights match expected profiles

### 5.2 Enable CloudFront Caching

**CloudFront cache policy:**
```json
{
  "Name": "GlucoLens-Demo-Cache",
  "MinTTL": 3600,
  "MaxTTL": 86400,
  "DefaultTTL": 3600,
  "ParametersInCacheKeyAndForwardedToOrigin": {
    "EnableAcceptEncodingGzip": true,
    "QueryStringsConfig": {
      "QueryStringBehavior": "whitelist",
      "QueryStrings": ["period_days"]
    }
  }
}
```

This reduces Lambda invocations and costs.

### 5.3 Setup CloudWatch Alarms

```bash
# Alarm for Lambda errors
aws cloudwatch put-metric-alarm \
  --alarm-name glucolens-demo-lambda-errors \
  --alarm-description "Alert on Lambda function errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1

# Alarm for API Gateway 5xx errors
aws cloudwatch put-metric-alarm \
  --alarm-name glucolens-demo-api-errors \
  --metric-name 5XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

---

## Monitoring & Maintenance

### Monitor Lambda Performance

```bash
# View Lambda logs
aws logs tail /aws/lambda/glucolens-demo-GetInsightsFunction --follow

# Get Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=glucolens-demo-GetInsightsFunction \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average,Maximum
```

### Cost Monitoring

**Setup billing alert:**
```bash
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget '{
    "BudgetName": "GlucoLens-Demo-Monthly",
    "BudgetLimit": {
      "Amount": "60",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

### Update Demo Data

```bash
# Regenerate data locally
docker-compose exec api python scripts/generate_demo_users.py

# Export new data
docker-compose exec timescaledb pg_dump -U glucolens -d glucolens \
  --data-only --inserts > demo_data_v2.sql

# Load into Aurora
psql -h $DB_ENDPOINT -U glucolens -d glucolens < demo_data_v2.sql
```

### Update Frontend

```bash
# Make changes
# Edit src/

# Rebuild
npm run build

# Deploy to S3
aws s3 sync dist/ s3://glucolens-demo-frontend/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"
```

---

## Transition to Full Product

### When Ready for Real Users

**Phase 1: Add User Registration (Keep Demo)**
- Add `/register` and `/login` endpoints
- Keep demo profiles accessible without login
- Deploy authentication Lambda functions

**Phase 2: Add Data Upload**
- Enable POST endpoints for data ingestion
- Add file upload to S3
- Process uploads with Lambda/Step Functions

**Phase 3: Multi-User with Data Isolation**
- Add user_id authentication
- Enable RLS (Row Level Security) in database
- Separate user data

**Phase 4: Scale Infrastructure**
- Increase Aurora ACU capacity
- Add read replicas
- Enable auto-scaling for Lambda

---

## Troubleshooting

### Issue: Lambda timeout

**Solution:**
- Increase timeout in template.yaml (max 30s for API Gateway)
- Optimize database queries (add indexes)
- Enable connection pooling

### Issue: CORS errors

**Solution:**
```python
# Update Lambda CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-cloudfront-domain.cloudfront.net"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)
```

### Issue: High Aurora costs

**Solution:**
- Reduce min ACU to 0.5
- Enable Aurora Serverless v2 auto-pause (shuts down when idle)
- Consider RDS Proxy to reduce connections

---

## Summary

**What You Built:**
- ✅ Read-only demo with 3 user profiles
- ✅ AWS Lambda serverless backend
- ✅ S3 + CloudFront static frontend
- ✅ Aurora Serverless database
- ✅ ~$50/month cost (optimizable to $15-20)

**Next Steps:**
1. Share demo URL with potential users
2. Collect feedback on insights/UX
3. Iterate on frontend based on feedback
4. Plan transition to full product (auth + data upload)

**Demo URL:** `https://your-cloudfront-domain.cloudfront.net`

🎉 **Your read-only demo is live!**
