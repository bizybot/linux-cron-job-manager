import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db, get_cron_service
from app.database import Base
from app.cron_service import CronService
from unittest.mock import MagicMock

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Mock CronService
@pytest.fixture
def cron_service_mock():
    mock = MagicMock(spec=CronService)
    return mock

# TestClient fixture
@pytest.fixture
def client(cron_service_mock):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cron_service] = lambda: cron_service_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_create_job(client, cron_service_mock):
    cron_service_mock.add_job.return_value = True
    cron_service_mock.validate_expression.return_value = True
    response = client.post(
        "/api/jobs",
        json={"name": "testjob", "expression": "* * * * *", "command": "echo 'hello'"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["name"] == "testjob"
    assert data["expression"] == "* * * * *"
    assert data["command"] == "echo 'hello'"
    cron_service_mock.add_job.assert_called_once_with("testjob", "* * * * *", "echo 'hello'")

def test_get_jobs(client, cron_service_mock):
    # Create a job first
    cron_service_mock.add_job.return_value = True
    cron_service_mock.validate_expression.return_value = True
    client.post(
        "/api/jobs",
        json={"name": "testjob1", "expression": "* * * * *", "command": "echo 'hello'"}
    )
    client.post(
        "/api/jobs",
        json={"name": "testjob2", "expression": "0 * * * *", "command": "echo 'world'"}
    )
    
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "testjob1"
    assert data[1]["name"] == "testjob2"

def test_update_job(client, cron_service_mock):
    # Create a job first
    cron_service_mock.add_job.return_value = True
    cron_service_mock.validate_expression.return_value = True
    response = client.post(
        "/api/jobs",
        json={"name": "testjob", "expression": "* * * * *", "command": "echo 'hello'"}
    )
    job_id = response.json()["id"]

    # Update the job
    cron_service_mock.validate_expression.return_value = True
    response = client.put(
        f"/api/jobs/{job_id}",
        json={"expression": "0 * * * *"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["expression"] == "0 * * * *"

def test_delete_job(client, cron_service_mock):
    # Create a job first
    cron_service_mock.add_job.return_value = True
    cron_service_mock.validate_expression.return_value = True
    response = client.post(
        "/api/jobs",
        json={"name": "testjob", "expression": "* * * * *", "command": "echo 'hello'"}
    )
    job_id = response.json()["id"]
    job_name = response.json()["name"]

    # Delete the job
    cron_service_mock.remove_job.return_value = True
    response = client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job deleted successfully"
    cron_service_mock.remove_job.assert_called_once_with(job_name)

def test_enable_disable_job(client, cron_service_mock):
    # Create a job first
    cron_service_mock.add_job.return_value = True
    cron_service_mock.validate_expression.return_value = True
    response = client.post(
        "/api/jobs",
        json={"name": "testjob", "expression": "* * * * *", "command": "echo 'hello'"}
    )
    job_id = response.json()["id"]
    job_name = response.json()["name"]

    # Disable the job
    cron_service_mock.disable_job.return_value = True
    response = client.post(f"/api/jobs/{job_id}/disable")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job disabled successfully"
    cron_service_mock.disable_job.assert_called_once_with(job_name)

    # Enable the job
    cron_service_mock.enable_job.return_value = True
    response = client.post(f"/api/jobs/{job_id}/enable")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job enabled successfully"
    cron_service_mock.enable_job.assert_called_once_with(job_name)
