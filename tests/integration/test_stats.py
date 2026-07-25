from httpx import AsyncClient


class TestStats:
    async def test_stats_program_manager_reussi(
        self, manager_client: AsyncClient
    ):
        resp = await manager_client.get("/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert "offres_par_statut" in body
        assert "candidatures_par_statut" in body

    async def test_stats_refuse_student(
        self, student_client: AsyncClient
    ):
        resp = await student_client.get("/stats")
        assert resp.status_code == 403
