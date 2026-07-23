from httpx import AsyncClient


class TestAuth:
    async def test_register_puis_login(self, client: AsyncClient):
        register_resp = await client.post(
            "/auth/register",
            json={
                "username": "nouveau",
                "email": "nouveau@test.com",
                "password": "pass1234",
                "role": "student",
            },
        )
        assert register_resp.status_code == 201

        login_resp = await client.post(
            "/auth/login",
            data={"username": "nouveau", "password": "pass1234"},
        )
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()
        assert "refresh_token" in login_resp.json()

    async def test_login_mauvais_mot_de_passe(
        self, client: AsyncClient
    ):
        await client.post(
            "/auth/register",
            json={
                "username": "victime",
                "email": "victime@test.com",
                "password": "pass1234",
                "role": "student",
            },
        )
        resp = await client.post(
            "/auth/login",
            data={"username": "victime", "password": "mauvais"},
        )
        assert resp.status_code == 401

    async def test_register_refuse_role_admin(
        self, client: AsyncClient
    ):
        """UserRegister n'accepte que student/company (Literal)."""
        resp = await client.post(
            "/auth/register",
            json={
                "username": "usurpateur",
                "email": "usurpateur@test.com",
                "password": "pass1234",
                "role": "admin",
            },
        )
        assert resp.status_code == 422