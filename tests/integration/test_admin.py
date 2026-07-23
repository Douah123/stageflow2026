from httpx import AsyncClient


class TestAdminPermissions:
    async def test_student_ne_peut_pas_lister_users(
        self, student_client: AsyncClient
    ):
        resp = await student_client.get("/admin/users")
        assert resp.status_code == 403

    async def test_admin_peut_lister_users(
        self, admin_client: AsyncClient
    ):
        resp = await admin_client.get("/admin/users")
        assert resp.status_code == 200

    async def test_admin_change_role_utilisateur(
        self,
        admin_client: AsyncClient,
        student_client: AsyncClient,
        db_session_with_roles,
    ):
        from app.repositories.role import RoleRepository

        # récupère l'id de l'étudiant via /users/me
        me_resp = await student_client.get("/users/me")
        user_id = me_resp.json()["id"]

        role_repo = RoleRepository(db_session_with_roles)
        role_company = await role_repo.get_by_name("company")

        resp = await admin_client.patch(
            f"/admin/users/{user_id}",
            json={"role_id": role_company.id},
        )
        assert resp.status_code == 200
        assert resp.json()["role"]["nom"] == "company"