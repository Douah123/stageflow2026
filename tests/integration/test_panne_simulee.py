from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from app.repositories.offre import OffreRepository


class TestPanneRepository:
    async def test_erreur_repository_renvoie_500(
        self, client: AsyncClient
    ):
        with patch.object(
            OffreRepository,
            "get_published",
            new_callable=AsyncMock,
            side_effect=Exception("Connexion base perdue"),
        ):
            resp = await client.get("/offres")
            assert resp.status_code == 500