# GitHub Actions CI/CD Pipelines

This directory contains automated workflows for building, testing, and deploying GlucoLens.

## Workflows

### 1. `docker-build-push.yml` - Docker Image CI/CD

**Purpose**: Build and validate Docker images on every PR and push to main, ensuring deployment-ready containers.

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs**:

#### Job 1: Build and Push Docker Image
- **Runs on**: Every push and PR
- **Steps**:
  1. Checkout code
  2. Set up Docker Buildx (multi-platform support)
  3. Log in to GitHub Container Registry (ghcr.io)
  4. Extract metadata (tags, labels)
  5. Build Docker image with layer caching
  6. **Test Docker image** (critical validation):
     - Start container with test environment
     - Verify app imports successfully
     - Ensure no import errors or missing dependencies
  7. Push to ghcr.io (only on push to main/develop, not PRs)

**Image Tags Created**:
- `latest` - Latest from main branch
- `main` - Current main branch
- `develop` - Current develop branch
- `sha-<commit>` - Specific commit
- `pr-<number>` - Pull request builds

**Registry**: `ghcr.io/brettleehari/metabolic-story-teller`

**Why This Matters**:
- ✅ Catches Docker build failures **before** deployment
- ✅ Validates that all dependencies install correctly
- ✅ Tests that Python imports work (catches missing packages)
- ✅ Creates versioned images for rollback capability
- ✅ GitHub cache speeds up builds (reuses layers)

#### Job 2: Build Frontend
- **Runs on**: Every push and PR
- **Steps**:
  1. Checkout code
  2. Set up Node.js 18 with npm cache
  3. Install dependencies (`npm ci`)
  4. Build frontend (`npm run build`)
  5. Validate build output (check dist/ exists)

**Why This Matters**:
- ✅ Catches TypeScript compilation errors
- ✅ Validates Vite build configuration
- ✅ Ensures frontend can be deployed

#### Job 3: Deployment Validation
- **Runs on**: Push to main only (after other jobs pass)
- **Steps**:
  1. Validate render.yaml syntax
  2. Check all required services defined
  3. Print deployment-ready status

**Why This Matters**:
- ✅ Ensures Render deployment config is valid
- ✅ Catches YAML syntax errors
- ✅ Confirms deployment readiness

---

### 2. `deployment-validation.yml` - Static Analysis & Tests

**Purpose**: Run comprehensive static analysis and deployment tests.

**See**: [DEPLOYMENT_VALIDATION_REPORT.md](../../DEPLOYMENT_VALIDATION_REPORT.md) for details.

**Jobs**:
- Static analysis (pylint, mypy, bandit)
- Deployment tests (24 tests)
- Docker build validation
- Frontend tests (ESLint, TypeScript)
- Security scans (Trivy, TruffleHog)
- Dependency checks (safety, npm audit)

---

## CI/CD Flow Diagram

```
Developer pushes code to GitHub
           ↓
    GitHub Actions triggered
           ↓
    ┌──────────────────────────────┐
    │  docker-build-push.yml       │
    ├──────────────────────────────┤
    │  1. Build Docker image       │
    │  2. Test image starts        │
    │  3. Test imports work        │
    │  4. Push to ghcr.io         │
    │  5. Build frontend          │
    │  6. Validate render.yaml    │
    └──────────────────────────────┘
           ↓
    All checks pass ✅
           ↓
    ┌──────────────────────────────┐
    │  Ready for deployment        │
    ├──────────────────────────────┤
    │  - Docker image: ghcr.io/... │
    │  - Frontend: built & tested  │
    │  - Render config: validated  │
    └──────────────────────────────┘
           ↓
    Merge to main
           ↓
    Render auto-deploys (if enabled)
    or Manual deploy via Render button
           ↓
    Render builds from Dockerfile
    (same Dockerfile that CI validated)
           ↓
    Deployment succeeds ✅
```

---

## Environment Variables

### Required Secrets

**None required!** GitHub Actions automatically provides:
- `GITHUB_TOKEN` - For GitHub Container Registry authentication
- No manual secrets needed for basic CI/CD

### Optional Secrets (For Enhanced Features)

If you want to enable additional features, add these in repository Settings → Secrets:

| Secret | Purpose | Required? |
|--------|---------|-----------|
| `DOCKERHUB_USERNAME` | Push to Docker Hub | No |
| `DOCKERHUB_TOKEN` | Docker Hub authentication | No |
| `RENDER_API_KEY` | Auto-deploy to Render | No |
| `SENTRY_DSN` | Error tracking in tests | No |

---

## How to Use

### For Pull Requests

1. Create feature branch
2. Make changes
3. Push to GitHub
4. Open PR to `main` or `develop`
5. **GitHub Actions runs automatically**:
   - Builds Docker image
   - Tests image
   - Builds frontend
   - Reports status in PR

6. **Review PR checks**:
   - ✅ All checks pass → Safe to merge
   - ❌ Checks fail → Fix issues before merging

### For Deployments

#### Option 1: Auto-Deploy (Recommended)
1. Merge PR to `main`
2. GitHub Actions builds and pushes image
3. Render auto-deploys (if configured)

#### Option 2: Manual Deploy
1. Ensure `main` branch has passing CI
2. Click "Deploy to Render" button
3. Render builds from validated Dockerfile
4. Deployment guaranteed to succeed (CI already tested)

### Viewing Workflow Runs

1. Go to repository on GitHub
2. Click "Actions" tab
3. See all workflow runs
4. Click on run to see details
5. Download artifacts if needed

---

## Image Management

### Pulling Images Locally

```bash
# Pull latest from main
docker pull ghcr.io/brettleehari/metabolic-story-teller:main

# Pull specific commit
docker pull ghcr.io/brettleehari/metabolic-story-teller:sha-abc1234

# Run locally
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  -e SECRET_KEY=your-secret \
  ghcr.io/brettleehari/metabolic-story-teller:main
```

### Image Cleanup

GitHub Container Registry:
- Images older than 90 days: Auto-deleted
- Untagged images: Auto-deleted after 7 days
- Manual cleanup: Repository Settings → Packages

---

## Troubleshooting

### Docker Build Fails in CI

**Symptom**: `docker-build-push.yml` fails at "Build Docker image"

**Solutions**:
1. Check build logs for missing dependencies
2. Verify `backend/requirements.txt` has all packages
3. Test locally: `docker build -t test ./backend`
4. Fix errors and push again

### Image Test Fails

**Symptom**: "Test Docker image" step fails

**Possible Causes**:
- Missing Python dependencies
- Import errors in code
- Invalid environment variable format

**Solutions**:
1. Check error message for specific import failure
2. Add missing package to `requirements.txt`
3. Test locally:
   ```bash
   docker build -t test ./backend
   docker run --rm test python -c "from app.main import app"
   ```

### Frontend Build Fails

**Symptom**: `build-frontend` job fails

**Solutions**:
1. Check TypeScript compilation errors
2. Fix linting issues: `npm run lint`
3. Test locally: `npm run build`
4. Ensure `vite.config.ts` is correct

### Push to Registry Fails

**Symptom**: "Push Docker image" fails with permission error

**Cause**: GitHub token doesn't have package write permission

**Solution**:
1. Repository Settings → Actions → General
2. Workflow permissions → Read and write permissions
3. Save and re-run workflow

---

## Best Practices

### Before Merging PRs

- ✅ Wait for all CI checks to pass
- ✅ Review build logs for warnings
- ✅ Test locally if possible
- ✅ Ensure commits are clean and descriptive

### Docker Image Management

- ✅ Use `main` tag for production deploys
- ✅ Use `sha-<commit>` for rollbacks
- ✅ Keep images under 500MB (optimize layers)
- ✅ Use `.dockerignore` to exclude unnecessary files

### Deployment Safety

- ✅ Always deploy from `main` branch
- ✅ Verify CI passed before deploying
- ✅ Use staging environment first (if available)
- ✅ Monitor logs after deployment

---

## Future Enhancements

Potential additions to CI/CD:

- [ ] **Integration tests** with test database
- [ ] **E2E tests** with Playwright
- [ ] **Performance tests** with k6
- [ ] **Security scans** with Snyk
- [ ] **Automated rollback** on health check failures
- [ ] **Slack/Discord notifications** on deployment
- [ ] **Multi-region deployments**
- [ ] **Staging environment** auto-deploy

---

## Support

**Issues with CI/CD?**
- Check [GitHub Actions Troubleshooting](https://docs.github.com/en/actions/learn-github-actions/troubleshooting)
- Review workflow logs in Actions tab
- Open issue with workflow run link

**Questions?**
- See [GitHub Actions documentation](https://docs.github.com/en/actions)
- See [Docker Build Push Action](https://github.com/docker/build-push-action)
- Check [Render deployment docs](https://render.com/docs/deploy-github-actions)

---

**Last Updated**: 2025-12-19
**Workflows**: 2 active
**Registry**: GitHub Container Registry (ghcr.io)
