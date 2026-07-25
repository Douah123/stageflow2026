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

    async def test_register_email_deja_utilise(
        self, client: AsyncClient
    ):
        payload = {
            "username": "premier",
            "email": "duplique@test.com",
            "password": "pass1234",
            "role": "student",
        }
        await client.post("/auth/register", json=payload)

        resp = await client.post(
            "/auth/register",
            json={**payload, "username": "second"},
        )
        assert resp.status_code == 409

    async def test_register_username_deja_pris(
        self, client: AsyncClient
    ):
        payload = {
            "username": "meme_pseudo",
            "email": "premier@test.com",
            "password": "pass1234",
            "role": "student",
        }
        await client.post("/auth/register", json=payload)

        resp = await client.post(
            "/auth/register",
            json={**payload, "email": "second@test.com"},
        )
        assert resp.status_code == 409

    async def test_login_compte_desactive(
        self, client: AsyncClient, admin_client: AsyncClient
    ):
        await client.post(
            "/auth/register",
            json={
                "username": "a_desactiver",
                "email": "desactive@test.com",
                "password": "pass1234",
                "role": "student",
            },
        )
        me_resp = await client.post(
            "/auth/login",
            data={
                "username": "a_desactiver",
                "password": "pass1234",
            },
        )
        user_id = jwt_subject(me_resp.json()["access_token"])

        await admin_client.patch(
            f"/admin/users/{user_id}",
            json={"is_active": False},
        )

        resp = await client.post(
            "/auth/login",
            data={
                "username": "a_desactiver",
                "password": "pass1234",
            },
        )
        assert resp.status_code == 400

    async def test_refresh_token_reussi(self, client: AsyncClient):
        await client.post(
            "/auth/register",
            json={
                "username": "refresh_user",
                "email": "refresh@test.com",
                "password": "pass1234",
                "role": "student",
            },
        )
        login_resp = await client.post(
            "/auth/login",
            data={
                "username": "refresh_user",
                "password": "pass1234",
            },
        )
        refresh_token = login_resp.json()["refresh_token"]

        resp = await client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_refresh_token_invalide(self, client: AsyncClient):
        resp = await client.post(
            "/auth/refresh",
            json={"refresh_token": "token.invalide.ici"},
        )
        assert resp.status_code == 401


def jwt_subject(token: str) -> str:
    from app.core.security import decode_token

    return decode_token(token)["sub"]