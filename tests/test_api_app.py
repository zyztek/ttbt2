import pytest # Using pytest for fixtures and structure
import json
from api.app import app # Import the Flask app instance

@pytest.fixture
def client():
    # app.config['TESTING'] = True # Standard practice, though might not be strictly needed for these simple GETs
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data == {"status": "TikTok Bot API running"}

def test_status_route(client):
    response = client.get('/status')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    # This will test against the current static example values
    assert data == {
        "bots_running": 3,
        "active_users": []
    }
