import pytest # Using pytest for fixtures and structure
import json
from dashboard.app import app # Import the Flask app instance

@pytest.fixture
def client():
    # app.config['TESTING'] = True # Standard practice
    with app.test_client() as client:
        yield client

def test_dashboard_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    # Basic check that it's likely HTML - could be more specific if index.html content is known
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

def test_dashboard_status_route(client):
    response = client.get('/status')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    # This will test against the current static example values
    assert data == {
        "bots": [
            {"name": "bot1", "status": "ok"},
            {"name": "bot2", "status": "running"}
        ]
    }
