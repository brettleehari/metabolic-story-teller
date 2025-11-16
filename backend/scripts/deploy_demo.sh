#!/bin/bash
# Deployment script for GlucoLens AWS Lambda Demo
# Usage: ./deploy_demo.sh [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-demo}
STACK_NAME="glucolens-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GlucoLens AWS Lambda Demo Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Environment:${NC} $ENVIRONMENT"
echo -e "${YELLOW}Stack Name:${NC} $STACK_NAME"
echo -e "${YELLOW}Region:${NC} $REGION"
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS CLI found${NC}"

if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ AWS SAM CLI not found. Please install it first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS SAM CLI found${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install it first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure'.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS credentials configured${NC}"

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${YELLOW}AWS Account:${NC} $AWS_ACCOUNT_ID"
echo ""

# Validate required environment variables
echo -e "${BLUE}Validating environment variables...${NC}"

if [ -z "$AWS_DB_ENDPOINT" ]; then
    echo -e "${RED}❌ AWS_DB_ENDPOINT not set${NC}"
    echo "Please set: export AWS_DB_ENDPOINT=your-db-endpoint.rds.amazonaws.com"
    exit 1
fi
echo -e "${GREEN}✅ AWS_DB_ENDPOINT set${NC}"

if [ -z "$AWS_DB_NAME" ]; then
    echo -e "${YELLOW}⚠️  AWS_DB_NAME not set, using default: glucolens${NC}"
    AWS_DB_NAME="glucolens"
fi

if [ -z "$AWS_DB_USERNAME" ]; then
    echo -e "${RED}❌ AWS_DB_USERNAME not set${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS_DB_USERNAME set${NC}"

if [ -z "$AWS_DB_PASSWORD" ]; then
    echo -e "${RED}❌ AWS_DB_PASSWORD not set${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS_DB_PASSWORD set${NC}"

echo ""

# Build SAM application
echo -e "${BLUE}Building SAM application...${NC}"
cd "$BACKEND_DIR"
sam build --use-container

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ SAM build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ SAM build completed${NC}"
echo ""

# Deploy SAM application
echo -e "${BLUE}Deploying to AWS...${NC}"
sam deploy \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset \
    --parameter-overrides \
        DBEndpoint="$AWS_DB_ENDPOINT" \
        DBName="$AWS_DB_NAME" \
        DBUsername="$AWS_DB_USERNAME" \
        DBPassword="$AWS_DB_PASSWORD"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ SAM deployment failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ SAM deployment completed${NC}"
echo ""

# Get API Gateway URL
echo -e "${BLUE}Retrieving API Gateway URL...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

if [ -z "$API_URL" ]; then
    echo -e "${YELLOW}⚠️  Could not retrieve API URL. Check CloudFormation outputs.${NC}"
else
    echo -e "${GREEN}✅ API URL: $API_URL${NC}"
fi
echo ""

# Generate demo data
echo -e "${BLUE}Generate demo data? (y/n)${NC}"
read -r GENERATE_DATA

if [ "$GENERATE_DATA" = "y" ] || [ "$GENERATE_DATA" = "Y" ]; then
    echo -e "${BLUE}Generating demo data...${NC}"

    # Set database URL for demo data generation
    export DATABASE_URL="postgresql+asyncpg://$AWS_DB_USERNAME:$AWS_DB_PASSWORD@$AWS_DB_ENDPOINT:5432/$AWS_DB_NAME"

    python3 scripts/generate_demo_users.py

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Demo data generation failed${NC}"
    else
        echo -e "${GREEN}✅ Demo data generated successfully${NC}"
    fi
fi
echo ""

# Test API
echo -e "${BLUE}Testing API health...${NC}"
if [ -n "$API_URL" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/")

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "${GREEN}✅ API health check passed (HTTP $HTTP_CODE)${NC}"
    else
        echo -e "${RED}❌ API health check failed (HTTP $HTTP_CODE)${NC}"
    fi
fi
echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}API URL:${NC} $API_URL"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update VITE_DEMO_API_URL in frontend .env with the API URL above"
echo "2. Build and deploy frontend: npm run build"
echo "3. Upload frontend to S3: aws s3 sync dist/ s3://your-bucket/"
echo "4. Access demo at: /demo"
echo ""
echo -e "${YELLOW}Demo Users:${NC}"
echo "  - Alice Thompson (11111111-1111-1111-1111-111111111111)"
echo "  - Bob Martinez (22222222-2222-2222-2222-222222222222)"
echo "  - Carol Chen (33333333-3333-3333-3333-333333333333)"
echo ""
