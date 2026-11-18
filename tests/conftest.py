import os
os.environ['JWT_SECRET_KEY'] = 'this-is-a-test-only-secret-value-with-adequate-length'
os.environ['DATABASE_URL'] = 'sqlite+pysqlite:///:memory:'

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

@pytest.fixture
def client():
    engine = create_engine('sqlite+pysqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)  # Tests only; production uses Alembic migrations.

    def override_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
