import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.main import app, Base, get_db

# 1) Créer un engine SQLite en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2) Remplacer la dépendance get_db
@pytest.fixture(scope="module")
def client():
    # Créer toutes les tables dans la DB de test
    Base.metadata.create_all(bind=engine)

    # Override get_db pour utiliser l'engine SQLite
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Fournir un client de test
    with TestClient(app) as c:
        yield c
