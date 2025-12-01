from unittest.mock import patch
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    @patch("src.services.storage._get_db")
    def test_health_returns_ok(self, mock_db):
        from src.web.app import app
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert "timestamp" in response.json()


class TestIndexEndpoint:
    @patch("src.services.storage._get_db")
    def test_index_without_login_shows_login_page(self, mock_db):
        from src.web.app import app
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "Logga in" in response.text


class TestLogoutEndpoint:
    @patch("src.services.storage._get_db")
    def test_logout_redirects(self, mock_db):
        from src.web.app import app
        client = TestClient(app)
        response = client.get("/logout", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/"


class TestLoginEndpoint:
    @patch("src.services.storage._get_db")
    def test_login_redirects_to_google(self, mock_db):
        from src.web.app import app
        client = TestClient(app)
        response = client.get("/auth/login", follow_redirects=False)
        
        assert response.status_code == 307
        assert "accounts.google.com" in response.headers["location"]
