# Quick Start: AWS Lambda Demo Deployment

Get the GlucoLens read-only demo running on AWS in 2-3 hours.

---

## Prerequisites (15 minutes)

1. **AWS Account** with billing enabled
2. **Tools installed:**
   ```bash
   # AWS CLI
   pip install awscli
   aws configure

   # AWS SAM CLI
   pip install aws-sam-cli
   sam --version

   # Node.js & npm
   node --version
   npm --version

   # Python 3.11+
   python3 --version
   ```

3. **Aurora Serverless v2 Database** (or skip to use existing)
   - Go to AWS RDS Console
   - Create Aurora Serverless v2 PostgreSQL cluster
   - Note the endpoint, username, password

---

## Step 1: Clone & Configure (5 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/metabolic-story-teller.git
cd metabolic-story-teller

# Copy environment template
cp .env.demo.example .env.demo

# Edit .env.demo with your values
nano .env.demo
```

**Required values in `.env.demo`:**
```bash
AWS_DB_ENDPOINT=your-cluster.cluster-xxxxx.us-east-1.rds.amazonaws.com
AWS_DB_USERNAME=glucolens_user
AWS_DB_PASSWORD=your-secure-password
```

---

## Step 2: Deploy Backend (20 minutes)

```bash
# Load environment variables
source .env.demo

# Navigate to backend
cd backend

# Build and deploy with SAM
./scripts/deploy_demo.sh demo
```

**What this does:**
- Builds Lambda function with dependencies
- Creates API Gateway REST API
- Sets up CloudWatch logs and alarms
- Deploys to AWS (stack: `glucolens-demo`)

**Expected output:**
```
✅ SAM build completed
✅ SAM deployment completed
✅ API URL: https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/Prod
```

**Copy the API URL** - you'll need it for the frontend!

---

## Step 3: Generate Demo Data (10 minutes)

```bash
# Still in backend directory
python3 scripts/generate_demo_users.py
```

**Expected output:**
```
✅ Created user: Alice Thompson (11111111-1111-1111-1111-111111111111)
✅ Created user: Bob Martinez (22222222-2222-2222-2222-222222222222)
✅ Created user: Carol Chen (33333333-3333-3333-3333-333333333333)

Generating data for Alice Thompson...
✅ Generated 25920 glucose readings (90 days, every 5 min)
✅ Generated 90 sleep records
✅ Generated 270 meals
✅ Generated 36 activities

... (similar for Bob and Carol)

Demo data generation complete!
Total time: ~8 minutes
```

---

## Step 4: Test Backend (5 minutes)

```bash
# Test API health
./scripts/validate_deployment.sh

# Or manually test
curl https://YOUR_API_URL/users
curl https://YOUR_API_URL/dashboard/11111111-1111-1111-1111-111111111111?period=30
```

**Expected:** JSON responses with user data and insights

---

## Step 5: Build & Deploy Frontend (15 minutes)

```bash
# Navigate back to root
cd ..

# Set environment variables for frontend build
export VITE_DEMO_MODE=true
export VITE_DEMO_API_URL=https://YOUR_API_URL

# Install dependencies
npm install

# Build for production
npm run build
```

**Create S3 bucket:**
```bash
# Create bucket (replace with your bucket name)
aws s3 mb s3://glucolens-demo-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://glucolens-demo-frontend \
  --index-document index.html \
  --error-document index.html

# Set bucket policy for public read
cat > bucket-policy.json <<EOF
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
EOF

aws s3api put-bucket-policy \
  --bucket glucolens-demo-frontend \
  --policy file://bucket-policy.json
```

**Deploy frontend:**
```bash
# Upload build to S3
aws s3 sync dist/ s3://glucolens-demo-frontend/ --delete
```

---

## Step 6: Access Demo (2 minutes)

**Frontend URL:**
```
http://glucolens-demo-frontend.s3-website-us-east-1.amazonaws.com
```

**Or set up CloudFront (recommended):**
```bash
# Create CloudFront distribution (via AWS Console)
# Origin: glucolens-demo-frontend.s3-website-us-east-1.amazonaws.com
# Default cache behavior: Redirect HTTP to HTTPS
# SSL: Use default CloudFront certificate

# After distribution created, note the domain
# Distribution domain: dxxxxxxxxxxxxxx.cloudfront.net
```

---

## Step 7: Explore Demo

**Visit frontend URL and:**
1. ✅ See 3 demo profiles (Alice, Bob, Carol)
2. ✅ Click on any profile
3. ✅ View dashboard with:
   - Glucose stats (avg, time in range)
   - Top correlations (sleep, exercise, meals → glucose)
   - Discovered patterns (association rules)
   - Period selector (7/30/90 days)

**Demo User Details:**

| User | ID (first 8 chars) | Profile | Avg Glucose | Time in Range |
|------|-------------------|---------|-------------|---------------|
| Alice Thompson | 11111111... | Well-controlled | 105 mg/dL | 85% |
| Bob Martinez | 22222222... | Variable | 140 mg/dL | 60% |
| Carol Chen | 33333333... | Active | 115 mg/dL | 75% |

---

## Verification Checklist

- [ ] Backend API responds at `/users` endpoint
- [ ] Demo data exists (3 users, ~78K glucose readings)
- [ ] Frontend loads demo index page
- [ ] All 3 profiles display correctly
- [ ] Clicking profile navigates to dashboard
- [ ] Dashboard shows glucose stats
- [ ] Correlations table populated
- [ ] Patterns display with confidence scores
- [ ] Period selector works (7/30/90 days)
- [ ] No console errors in browser
- [ ] Page loads in < 3 seconds

---

## Troubleshooting

### Backend Issues

**Problem:** `sam deploy` fails with "Unable to upload artifact"

**Solution:**
```bash
# Ensure Docker is running
docker ps

# Build with container
sam build --use-container --debug
```

**Problem:** API returns 502 Bad Gateway

**Solution:**
```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/glucolens-demo-DemoFunction --follow

# Verify database connection
aws lambda invoke \
  --function-name glucolens-demo-DemoFunction \
  --payload '{"httpMethod":"GET","path":"/"}' \
  response.json
```

### Frontend Issues

**Problem:** CORS errors in browser console

**Solution:**
- Verify API Gateway CORS is enabled in `template.yaml`
- Check S3 bucket CORS configuration
- Ensure `VITE_DEMO_API_URL` matches deployed API URL

**Problem:** Blank page after deployment

**Solution:**
```bash
# Check build output
ls -la dist/

# Verify S3 upload
aws s3 ls s3://glucolens-demo-frontend/

# Check browser console for errors
```

### Data Issues

**Problem:** No demo users appear

**Solution:**
```bash
# Verify data in database
# Connect to Aurora
psql -h $AWS_DB_ENDPOINT -U $AWS_DB_USERNAME -d $AWS_DB_NAME

# Check user count
SELECT COUNT(*) FROM users;  -- Should be 3

# Re-run generation if needed
python3 backend/scripts/generate_demo_users.py
```

---

## Cost Estimate

**Monthly costs (with demo running 24/7):**

| Service | Cost |
|---------|------|
| Lambda (1M requests/month) | $5 |
| API Gateway (1M requests/month) | $3.50 |
| Aurora Serverless v2 (0.5 ACU) | $35 |
| S3 (1GB storage) | $0.50 |
| CloudFront (optional, 1GB transfer) | $1 |
| **Total** | **~$45/month** |

**Optimization tips:**
- Configure Aurora auto-pause → Save $20-25/month
- Use Lambda reserved concurrency → Save $2-3/month
- **Optimized total: $15-20/month**

---

## Next Steps

After demo is running:

1. **Share URL** with stakeholders
2. **Gather feedback** on UX and insights
3. **Monitor costs** in AWS Billing Dashboard
4. **Plan next phase:**
   - Add authentication for real users
   - Implement write operations (POST/PUT/DELETE)
   - Add more ML insights (time series forecasting)
   - Integrate Apple HealthKit

---

## Cleanup

To remove all resources:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name glucolens-demo

# Delete S3 bucket
aws s3 rm s3://glucolens-demo-frontend --recursive
aws s3 rb s3://glucolens-demo-frontend

# Delete CloudFront distribution (if created)
# Via AWS Console: CloudFront > Distributions > Disable > Delete

# Delete Aurora cluster (WARNING: Data loss!)
aws rds delete-db-cluster \
  --db-cluster-identifier your-cluster-id \
  --skip-final-snapshot
```

---

## Support

- **Full Deployment Guide:** See `DEMO_DEPLOYMENT_AWS_LAMBDA.md`
- **Detailed Checklist:** See `AWS_DEPLOYMENT_CHECKLIST.md`
- **Architecture Diagrams:** See `ARCHITECTURE_DIAGRAMS.md`
- **GitHub Issues:** Report bugs at repository issues page

---

**Estimated Total Time:** 2-3 hours (including AWS resource provisioning)

**Difficulty:** Intermediate (requires AWS experience)

**Result:** Production-ready demo accessible globally via CDN
