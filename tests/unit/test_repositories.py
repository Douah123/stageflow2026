from app.repositories.candidature import (
    CandidatureRepository,
)


class TestCandidatureRepository:
    async def test_a_candidature_active_detecte_pending(
        self, db_session_with_roles
    ):
        from app.repositories.role import RoleRepository
        from app.repositories.user import UserRepository
        from app.schemas.user import UserCreate
        from app.utils.hashing import hash_password

        role_repo = RoleRepository(db_session_with_roles)
        role = await role_repo.get_by_name("student")

        user_repo = UserRepository(db_session_with_roles)
        etudiant = await user_repo.create(
            UserCreate(
                username="etu1",
                email="etu1@test.com",
                hashed_password=hash_password("pass1234"),
                role_id=role.id,
            )
        )

        from app.models.offre import Offre

        offre = Offre(
            titre="Test",
            mission="Mission suffisamment longue",
            competences="python",
            statut="published",
            entreprise_id=etudiant.id,  # peu importe ici
        )
        db_session_with_roles.add(offre)
        await db_session_with_roles.flush()

        candidature_repo = CandidatureRepository(
            db_session_with_roles
        )
        await candidature_repo.create_candidature(
            offre_id=offre.id, etudiant_id=etudiant.id
        )

        assert (
            await candidature_repo.a_candidature_active(
                etudiant.id, offre.id
            )
            is True
        )


class TestBaseRepository:
    async def test_get_all_renvoie_les_objets_crees(
        self, db_session_with_roles
    ):
        from app.models.offre import Offre
        from app.repositories.offre import OffreRepository
        from app.repositories.role import RoleRepository
        from app.repositories.user import UserRepository
        from app.schemas.user import UserCreate
        from app.utils.hashing import hash_password

        role_repo = RoleRepository(db_session_with_roles)
        role = await role_repo.get_by_name("company")

        user_repo = UserRepository(db_session_with_roles)
        entreprise = await user_repo.create(
            UserCreate(
                username="base_repo_entreprise",
                email="base_repo@test.com",
                hashed_password=hash_password("pass1234"),
                role_id=role.id,
            )
        )

        offre_repo = OffreRepository(db_session_with_roles)
        db_session_with_roles.add(
            Offre(
                titre="Offre base repo",
                mission="Mission suffisamment longue",
                competences=["python"],
                statut="draft",
                entreprise_id=entreprise.id,
            )
        )
        await db_session_with_roles.flush()

        toutes = await offre_repo.get_all()
        assert len(toutes) == 1
        assert toutes[0].titre == "Offre base repo"