from httpx import AsyncClient


class TestCandidatureInvariants:
    async def test_parcours_nominal_candidature(
        self,
        company_client: AsyncClient,
        manager_client: AsyncClient,
        student_client: AsyncClient,
    ):
        create_resp = await company_client.post(
            "/offres",
            json={
                "titre": "Stage Data",
                "mission": "Mission suffisamment longue",
                "competences": ["python"],
            },
        )
        offre_id = create_resp.json()["id"]
        await company_client.patch(f"/offres/{offre_id}/submit")
        await manager_client.patch(
            f"/offres/{offre_id}/review",
            json={"decision": "publish"},
        )

        apply_resp = await student_client.post(
            f"/offres/{offre_id}/candidatures"
        )
        assert apply_resp.status_code == 201
        candidature_id = apply_resp.json()["id"]

        decision_resp = await manager_client.patch(
            f"/candidatures/{candidature_id}/decision",
            json={"decision": "accepted"},
        )
        assert decision_resp.json()["statut"] == "accepted"

        # une candidature acceptée ne peut plus être retirée
        delete_resp = await student_client.delete(
            f"/candidatures/{candidature_id}"
        )
        assert delete_resp.status_code == 400

    async def test_double_candidature_refusee(
        self,
        company_client: AsyncClient,
        manager_client: AsyncClient,
        student_client: AsyncClient,
    ):
        create_resp = await company_client.post(
            "/offres",
            json={
                "titre": "Stage Data 2",
                "mission": "Mission suffisamment longue",
                "competences": ["sql"],
            },
        )
        offre_id = create_resp.json()["id"]
        await company_client.patch(f"/offres/{offre_id}/submit")
        await manager_client.patch(
            f"/offres/{offre_id}/review",
            json={"decision": "publish"},
        )

        await student_client.post(
            f"/offres/{offre_id}/candidatures"
        )
        resp = await student_client.post(
            f"/offres/{offre_id}/candidatures"
        )
        assert resp.status_code == 400