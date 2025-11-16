# AWS Lambda Demo Deployment Checklist

This checklist guides you through deploying the GlucoLens read-only demo to AWS Lambda.

**Estimated Time:** 2-3 hours
**Cost:** ~$50/month (optimizable to $15-20/month)

---

## Pre-Deployment Checklist

### 1. AWS Account Setup ✅

- [ ] AWS account created and active
- [ ] Billing alerts configured
- [ ] IAM user with appropriate permissions created
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] AWS SAM CLI installed (`pip install aws-sam-cli`)

**Verify:**
```bash
aws sts get-caller-identity
sam --version
```

### 2. Database Setup (Aurora Serverless v2) ✅

- [ ] Aurora Serverless v2 PostgreSQL cluster created
- [ ] Database name: `glucolens` (or custom name)
- [ ] Database user created with full permissions
- [ ] VPC and security groups configured
- [ ] Database accessible from Lambda (same VPC or public access)
- [ ] TimescaleDB extension installed

**Database Setup SQL:**
```sql
-- Connect to your Aurora instance
CREATE DATABASE glucolens;
\c glucolens

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create user (if needed)
CREATE USER glucolens_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE glucolens TO glucolens_user;
```

**Environment Variables to Set:**
```bash
export AWS_DB_ENDPOINT="your-cluster.cluster-xxxxx.us-east-1.rds.amazonaws.com"
export AWS_DB_NAME="glucolens"
export AWS_DB_USERNAME="glucolens_user"
export AWS_DB_PASSWORD="your-secure-password"
```

### 3. S3 Bucket for Frontend ✅

- [ ] S3 bucket created (e.g., `glucolens-demo-frontend`)
- [ ] Static website hosting enabled
- [ ] Bucket policy configured for public read access
- [ ] CORS configured for API access

**S3 Bucket Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::glucolens-demo-frontend/*"
    }
  ]
}
```

**CORS Configuration:**
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

### 4. CloudFront Distribution (Optional but Recommended) ✅

- [ ] CloudFront distribution created
- [ ] Origin: S3 bucket
- [ ] Default cache behavior configured
- [ ] SSL certificate configured (ACM)
- [ ] Custom domain configured (optional)

### 5. GitHub Secrets (For CI/CD) ✅

If using GitHub Actions, configure these secrets:

- [ ] `AWS_ACCESS_KEY_ID`
- [ ] `AWS_SECRET_ACCESS_KEY`
- [ ] `AWS_DB_ENDPOINT`
- [ ] `AWS_DB_NAME`
- [ ] `AWS_DB_USERNAME`
- [ ] `AWS_DB_PASSWORD`
- [ ] `AWS_S3_BUCKET`
- [ ] `AWS_CLOUDFRONT_DISTRIBUTION_ID` (if using CloudFront)
- [ ] `AWS_CLOUDFRONT_DOMAIN` (if using CloudFront)

---

## Deployment Steps

### Step 1: Deploy Backend (Lambda + API Gateway)

**Option A: Using Deployment Script**
```bash
cd backend
./scripts/deploy_demo.sh demo
```

**Option B: Manual SAM Deployment**
```bash
cd backend

# Build
sam build --use-container

# Deploy
sam deploy \
  --stack-name glucolens-demo \
  --region us-east-1 \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    DBEndpoint=$AWS_DB_ENDPOINT \
    DBName=$AWS_DB_NAME \
    DBUsername=$AWS_DB_USERNAME \
    DBPassword=$AWS_DB_PASSWORD
```

**Verify:**
```bash
# Get API URL
aws cloudformation describe-stacks \
  --stack-name glucolens-demo \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text

# Test API
curl https://YOUR_API_URL/
```

**Expected Output:**
```json
{
  "status": "healthy",
  "message": "GlucoLens Demo API is running"
}
```

### Step 2: Generate Demo Data

```bash
cd backend

# Set database URL
export DATABASE_URL="postgresql+asyncpg://$AWS_DB_USERNAME:$AWS_DB_PASSWORD@$AWS_DB_ENDPOINT:5432/$AWS_DB_NAME"

# Generate demo users
python scripts/generate_demo_users.py
```

**Expected Output:**
```
Creating demo users...
✅ Created user: Alice Thompson (11111111-1111-1111-1111-111111111111)
✅ Created user: Bob Martinez (22222222-2222-2222-2222-222222222222)
✅ Created user: Carol Chen (33333333-3333-3333-3333-333333333333)

Generating data for Alice Thompson...
✅ Generated 25920 glucose readings
✅ Generated 90 sleep records
✅ Generated 270 meals
✅ Generated 36 activities

... (similar for Bob and Carol)

Demo data generation complete!
```

### Step 3: Build and Deploy Frontend

```bash
# Set environment variables
export VITE_DEMO_MODE=true
export VITE_DEMO_API_URL=https://YOUR_API_GATEWAY_URL/Prod

# Build frontend
npm run build

# Deploy to S3
aws s3 sync dist/ s3://glucolens-demo-frontend/ --delete

# Invalidate CloudFront cache (if using CloudFront)
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

### Step 4: Validate Deployment

```bash
cd backend

# Run validation script
./scripts/validate_deployment.sh https://YOUR_API_GATEWAY_URL/Prod
```

**Expected Output:**
```
Testing: Root endpoint health check... ✅ PASS (HTTP 200)
Testing: Get demo users list... ✅ PASS (HTTP 200)
Testing: Get Alice's insights... ✅ PASS (HTTP 200)
... (15-20 tests)

Total Tests: 20
Passed: 20
Failed: 0

🎉 All tests passed!
```

### Step 5: Access Demo

**Frontend URL:**
- S3: `http://glucolens-demo-frontend.s3-website-us-east-1.amazonaws.com`
- CloudFront: `https://your-custom-domain.com` or `https://xxxxx.cloudfront.net`

**Demo Users:**
1. **Alice Thompson** (11111111-1111-1111-1111-111111111111)
   - Well-controlled glucose
   - 85% time in range

2. **Bob Martinez** (22222222-2222-2222-2222-222222222222)
   - Variable glucose
   - 60% time in range

3. **Carol Chen** (33333333-3333-3333-3333-333333333333)
   - Active lifestyle
   - 75% time in range

---

## Post-Deployment Verification

### API Endpoints to Test

```bash
# Health check
curl https://YOUR_API_URL/

# Get demo users
curl https://YOUR_API_URL/users

# Get Alice's dashboard
curl https://YOUR_API_URL/dashboard/11111111-1111-1111-1111-111111111111?period=30

# Get correlations
curl https://YOUR_API_URL/correlations/11111111-1111-1111-1111-111111111111

# Get patterns
curl https://YOUR_API_URL/patterns/11111111-1111-1111-1111-111111111111

# Get glucose readings
curl https://YOUR_API_URL/glucose/readings/11111111-1111-1111-1111-111111111111?limit=10
```

### Frontend Features to Test

- [ ] Landing page loads with 3 demo profiles
- [ ] Profile cards display correct stats
- [ ] Click on profile navigates to dashboard
- [ ] Dashboard loads for each user
- [ ] Period selector works (7/30/90 days)
- [ ] Glucose stats display correctly
- [ ] Correlations table shows data
- [ ] Patterns display with confidence scores
- [ ] No console errors
- [ ] Page loads in < 3 seconds

---

## Cost Monitoring

### Expected Monthly Costs (First Month)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 1M requests, 512MB, 1s avg | $5 |
| API Gateway | 1M requests | $3.50 |
| Aurora Serverless v2 | 0.5 ACU, 24/7 | $35 |
| S3 | 1GB storage, 10K requests | $0.50 |
| CloudFront | 1GB transfer, 10K requests | $1 |
| **Total** | | **~$45/month** |

### Cost Optimization Tips

1. **Aurora Serverless v2:**
   - Configure auto-pause after 5 minutes of inactivity
   - Reduce min ACU to 0.5
   - **Savings:** $20-25/month

2. **Lambda:**
   - Enable Lambda function caching
   - Optimize cold starts
   - **Savings:** $2-3/month

3. **CloudFront:**
   - Use CloudFront compression
   - Configure cache headers
   - **Savings:** $0.50/month

**Optimized Total:** ~$15-20/month

---

## Troubleshooting

### Issue: Lambda times out

**Symptoms:** 502 Bad Gateway or timeout errors

**Solutions:**
1. Check Lambda timeout setting (should be 30s)
2. Verify database connection from Lambda
3. Check VPC configuration if using private subnet
4. Review CloudWatch logs:
   ```bash
   aws logs tail /aws/lambda/glucolens-demo-DemoFunction --follow
   ```

### Issue: Database connection failed

**Symptoms:** "Could not connect to database" errors

**Solutions:**
1. Verify database endpoint: `AWS_DB_ENDPOINT`
2. Check database credentials
3. Verify security group allows Lambda access
4. Test connection from Lambda:
   ```bash
   aws lambda invoke \
     --function-name glucolens-demo-DemoFunction \
     --payload '{"httpMethod":"GET","path":"/"}' \
     response.json
   ```

### Issue: No demo data appears

**Symptoms:** Empty dashboard, no users

**Solutions:**
1. Verify demo data generation completed:
   ```sql
   SELECT COUNT(*) FROM users;  -- Should be 3
   SELECT COUNT(*) FROM glucose_readings;  -- Should be ~78,000
   ```
2. Re-run generation script:
   ```bash
   python backend/scripts/generate_demo_users.py
   ```

### Issue: CORS errors in frontend

**Symptoms:** "CORS policy" errors in browser console

**Solutions:**
1. Verify API Gateway CORS configuration in `template.yaml`
2. Check S3 bucket CORS configuration
3. Ensure API URL is correct in frontend `.env`

### Issue: CloudFront shows old content

**Symptoms:** Changes don't appear after deployment

**Solutions:**
1. Invalidate CloudFront cache:
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id YOUR_DIST_ID \
     --paths "/*"
   ```
2. Clear browser cache
3. Use incognito mode for testing

---

## Monitoring & Maintenance

### CloudWatch Alarms

The SAM template includes alarms for:
- Lambda errors > 5 in 5 minutes
- Lambda throttles > 10 in 5 minutes

**View Alarms:**
```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix glucolens-demo
```

### Log Analysis

**Lambda Logs:**
```bash
# View recent logs
aws logs tail /aws/lambda/glucolens-demo-DemoFunction --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/glucolens-demo-DemoFunction \
  --filter-pattern "ERROR"
```

**API Gateway Logs:**
```bash
# Enable execution logging in API Gateway console
# Then view logs in CloudWatch
```

### Backup Strategy

**Database Backups:**
- Aurora automated backups (enabled by default, 7-day retention)
- Manual snapshots before major changes

**Create Manual Snapshot:**
```bash
aws rds create-db-cluster-snapshot \
  --db-cluster-snapshot-identifier glucolens-demo-backup-$(date +%Y%m%d) \
  --db-cluster-identifier your-cluster-id
```

---

## Cleanup (Teardown)

To remove all resources and stop incurring costs:

```bash
# Delete CloudFormation stack (Lambda + API Gateway)
aws cloudformation delete-stack --stack-name glucolens-demo

# Empty and delete S3 bucket
aws s3 rm s3://glucolens-demo-frontend --recursive
aws s3 rb s3://glucolens-demo-frontend

# Delete CloudFront distribution
aws cloudfront delete-distribution \
  --id YOUR_DISTRIBUTION_ID \
  --if-match ETAG

# Delete Aurora cluster (WARNING: Data loss!)
aws rds delete-db-cluster \
  --db-cluster-identifier your-cluster-id \
  --skip-final-snapshot
```

---

## Next Steps

After successful deployment:

1. **Share demo URL** with stakeholders
2. **Gather feedback** on UX and insights
3. **Monitor costs** and optimize as needed
4. **Plan next phase:**
   - Add authentication for real users
   - Implement write operations
   - Add more ML insights
   - Integrate HealthKit

---

## Support & Resources

- **Documentation:** See `DEMO_DEPLOYMENT_AWS_LAMBDA.md` for detailed architecture
- **Architecture Diagrams:** See `ARCHITECTURE_DIAGRAMS.md`
- **GitHub Issues:** Report bugs at repository issues page
- **AWS Support:** https://console.aws.amazon.com/support/

---

**Last Updated:** {{ current_date }}
**Version:** 1.0.0
**Status:** ✅ Ready for deployment
