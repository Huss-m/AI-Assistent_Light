from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        from src.web.app import app
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert "timestamp" in response.json()


class TestIndexEndpoint:
    def test_index_without_login_shows_login_page(self):
        from src.web.app import app
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert "Logga in" in response.text


class TestLogoutEndpoint:
    def test_logout_redirects(self):
        from src.web.app import app
        client = TestClient(app)
        response = client.get("/logout", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == "/"


class TestLoginEndpoint:
    def test_login_redirects_to_google(self):
        from src.web.app import app
        client = TestClient(app)
        response = client.get("/auth/login", follow_redirects=False)

        assert response.status_code == 307
        assert "accounts.google.com" in response.headers["location"]
