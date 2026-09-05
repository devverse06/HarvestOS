from .conftest import auth_headers


def test_register_first_user_as_admin(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "first@example.com",
            "password": "StrongPass!123",
            "full_name": "First User",
        },
    )
    assert response.status_code == 200
    assert response.json()["role"] == "Admin"


def test_invalid_login_returns_generic_error(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "StrongPass!123",
            "full_name": "Normal User",
        },
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_token_can_read_current_user(client, admin_token):
    response = client.get("/api/auth/me", headers=auth_headers(admin_token))
    assert response.status_code == 200
    assert response.json()["role"] == "Admin"


def test_short_password_is_rejected(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "short@example.com",
            "password": "short",
            "full_name": "Short Password",
        },
    )
    assert response.status_code == 422


def test_common_password_is_rejected(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "common@example.com",
            "password": "password123",
            "full_name": "Common Password",
        },
    )
    assert response.status_code == 400


def test_non_admin_cannot_change_roles(client, admin_token):
    client.post(
        "/api/auth/register",
        json={
            "email": "operations@example.com",
            "password": "StrongOpsPass!123",
            "full_name": "Operations User",
        },
    )
    login = client.post(
        "/api/auth/login",
        data={"username": "operations@example.com", "password": "StrongOpsPass!123"},
    )
    operations_token = login.json()["access_token"]
    users = client.get("/api/admin/users", headers=auth_headers(admin_token)).json()
    target_id = next(user["id"] for user in users if user["email"] == "operations@example.com")
    response = client.patch(
        f"/api/admin/users/{target_id}/role",
        headers=auth_headers(operations_token),
        json={"role": "Operations"},
    )
    assert response.status_code == 403
