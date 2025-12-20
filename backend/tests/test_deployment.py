"""
Deployment Tests for GlucoLens
Tests to validate deployment readiness and catch configuration issues

Run with: pytest backend/tests/test_deployment.py -v
"""

import importlib
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


class TestImports:
    """Test that all critical modules can be imported without errors"""

    def test_import_main_app(self):
        """Test importing the main FastAPI application"""
        from app.main import app
        assert app is not None
        assert app.title == "GlucoLens API"

    def test_import_database(self):
        """Test importing database configuration"""
        from app.database import async_session_maker, engine
        assert async_session_maker is not None
        assert engine is not None

    def test_import_config(self):
        """Test importing configuration"""
        from app.config import settings
        assert settings is not None
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'SECRET_KEY')

    def test_import_models(self):
        """Test importing all database models"""
        modules = [
            'app.models.user',
            'app.models.glucose',
            'app.models.sleep',
            'app.models.meal',
            'app.models.activity',
            'app.models.medication',
            'app.models.correlation',
            'app.models.pattern',
        ]
        for module in modules:
            try:
                importlib.import_module(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")

    def test_import_schemas(self):
        """Test importing all Pydantic schemas"""
        modules = [
            'app.schemas.user',
            'app.schemas.glucose',
            'app.schemas.sleep',
            'app.schemas.meal',
            'app.schemas.activity',
            'app.schemas.auth',
        ]
        for module in modules:
            try:
                importlib.import_module(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")

    def test_import_routes(self):
        """Test importing all API routes"""
        modules = [
            'app.routes.auth',
            'app.routes.glucose',
            'app.routes.sleep',
            'app.routes.meals',
            'app.routes.activities',
            'app.routes.insights',
            'app.routes.health',
        ]
        for module in modules:
            try:
                importlib.import_module(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")

    def test_import_ml_services(self):
        """Test importing ML services"""
        try:
            from app.services.pcmci_service import PCMCIService
            from app.services.stumpy_service import StumpyService
            from app.services.association_rules import AssociationRulesService
            assert PCMCIService is not None
            assert StumpyService is not None
            assert AssociationRulesService is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ML services: {e}")


class TestEnvironmentConfiguration:
    """Test environment variables and configuration"""

    def test_required_env_vars(self):
        """Test that critical environment variables are set"""
        from app.config import settings

        # Check critical settings exist and are not default/empty
        assert settings.SECRET_KEY, "SECRET_KEY must be set"
        assert settings.DATABASE_URL, "DATABASE_URL must be set"
        assert 'postgresql' in settings.DATABASE_URL, "DATABASE_URL must be PostgreSQL"

    def test_database_url_format(self):
        """Test DATABASE_URL has correct format for async operations"""
        from app.config import settings

        db_url = settings.DATABASE_URL
        # Should use asyncpg for async operations
        assert 'postgresql+asyncpg://' in db_url or 'postgresql://' in db_url

    def test_cors_configuration(self):
        """Test CORS settings are configured"""
        from app.config import settings

        assert hasattr(settings, 'CORS_ORIGINS')

    def test_jwt_configuration(self):
        """Test JWT settings are configured"""
        from app.config import settings

        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'ALGORITHM')
        assert settings.ALGORITHM == 'HS256'


@pytest.mark.asyncio
class TestDatabaseConnectivity:
    """Test database connection and basic operations"""

    async def test_database_connection(self):
        """Test that we can connect to the database"""
        from app.config import settings
        from sqlalchemy.ext.asyncio import create_async_engine

        # Create engine with proper async URL
        db_url = settings.DATABASE_URL
        if not db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')

        engine = create_async_engine(db_url)

        try:
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            await engine.dispose()

    async def test_database_tables_exist(self):
        """Test that required tables exist in the database"""
        from app.config import settings
        from sqlalchemy.ext.asyncio import create_async_engine

        db_url = settings.DATABASE_URL
        if not db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')

        engine = create_async_engine(db_url)

        required_tables = [
            'users',
            'glucose_readings',
            'sleep_data',
            'meals',
            'activities',
        ]

        try:
            async with engine.connect() as conn:
                for table in required_tables:
                    result = await conn.execute(
                        text(
                            f"SELECT EXISTS (SELECT FROM information_schema.tables "
                            f"WHERE table_schema = 'public' AND table_name = '{table}')"
                        )
                    )
                    exists = result.scalar()
                    assert exists, f"Table '{table}' does not exist in database"
        finally:
            await engine.dispose()


class TestRedisConnectivity:
    """Test Redis connection"""

    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test that we can connect to Redis"""
        from app.config import settings
        import redis.asyncio as redis

        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            await redis_client.close()
        except Exception as e:
            pytest.fail(f"Failed to connect to Redis: {e}")


class TestAPIEndpoints:
    """Test API endpoint registration and basic functionality"""

    def test_health_endpoint_registered(self):
        """Test that health check endpoint is registered"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert "/health" in routes or "/api/v1/health" in routes

    def test_auth_endpoints_registered(self):
        """Test that authentication endpoints are registered"""
        from app.main import app

        routes = [route.path for route in app.routes]
        auth_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]

        for endpoint in auth_endpoints:
            assert endpoint in routes, f"Endpoint {endpoint} not registered"

    def test_data_endpoints_registered(self):
        """Test that data ingestion endpoints are registered"""
        from app.main import app

        routes = [route.path for route in app.routes]
        data_endpoints = [
            "/api/v1/glucose/readings",
            "/api/v1/sleep",
            "/api/v1/meals",
            "/api/v1/activities",
        ]

        for endpoint in data_endpoints:
            assert endpoint in routes, f"Endpoint {endpoint} not registered"

    def test_insights_endpoints_registered(self):
        """Test that insights endpoints are registered"""
        from app.main import app

        routes = [route.path for route in app.routes]
        insights_endpoints = [
            "/api/v1/insights/correlations",
            "/api/v1/insights/patterns",
            "/api/v1/insights/dashboard",
        ]

        for endpoint in insights_endpoints:
            assert endpoint in routes, f"Endpoint {endpoint} not registered"


class TestSecurityConfiguration:
    """Test security-related configuration"""

    def test_password_hashing_available(self):
        """Test that password hashing utilities work"""
        from app.utils.auth import get_password_hash, verify_password

        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password, "Password should be hashed"
        assert verify_password(password, hashed), "Password verification failed"
        assert not verify_password("wrong_password", hashed), "Wrong password should not verify"

    def test_jwt_token_creation(self):
        """Test that JWT tokens can be created"""
        from app.utils.auth import create_access_token
        from datetime import timedelta

        test_data = {"sub": "test@example.com"}
        token = create_access_token(data=test_data, expires_delta=timedelta(minutes=15))

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0


class TestCeleryConfiguration:
    """Test Celery task queue configuration"""

    def test_celery_app_configured(self):
        """Test that Celery app is properly configured"""
        try:
            from app.tasks import celery_app
            assert celery_app is not None
            assert celery_app.conf.broker_url is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Celery app: {e}")

    def test_celery_tasks_registered(self):
        """Test that Celery tasks are registered"""
        from app.tasks import celery_app

        # Check that tasks are registered
        task_names = list(celery_app.tasks.keys())
        assert len(task_names) > 0, "No Celery tasks registered"


class TestStaticAnalysis:
    """Tests for running static analysis tools"""

    def test_python_syntax_valid(self):
        """Test that all Python files have valid syntax"""
        import py_compile

        app_dir = Path(__file__).parent.parent / "app"
        python_files = list(app_dir.rglob("*.py"))

        errors = []
        for py_file in python_files:
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(f"{py_file}: {e}")

        assert not errors, f"Syntax errors found:\n" + "\n".join(errors)


# Pytest configuration
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    # Add backend directory to Python path
    backend_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_dir))

    # Ensure .env file is loaded for tests
    from dotenv import load_dotenv
    env_file = backend_dir.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    yield

    # Cleanup after tests
    pass
