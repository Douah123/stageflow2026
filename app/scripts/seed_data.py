import asyncio

import app.models  # noqa: F401 — force l'enregistrement de tous les modèles

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.candidature import Candidature
from app.models.offre import Offre
from app.models.role import Role
from app.models.user import User
from app.utils.hashing import hash_password

MOT_DE_PASSE_TEST = "motdepasse123"


async def get_role_id(db, nom: str) -> int:
    result = await db.execute(select(Role).where(Role.nom == nom))
    role = result.scalar_one_or_none()
    if role is None:
        raise RuntimeError(
            f"Rôle '{nom}' introuvable. "
            "As-tu bien peuplé la table roles ?"
        )
    return role.id


async def creer_user(
    db, username: str, email: str, role_id: int
) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(MOT_DE_PASSE_TEST),
        role_id=role_id,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


async def seed():
    async with AsyncSessionLocal() as db:
        role_student = await get_role_id(db, "student")
        role_company = await get_role_id(db, "company")
        role_manager = await get_role_id(db, "program_manager")

        # ---- Utilisateurs ----
        etudiant1 = await creer_user(
            db, "etudiant1", "etudiant1@test.com", role_student
        )
        etudiant2 = await creer_user(
            db, "etudiant2", "etudiant2@test.com", role_student
        )
        entreprise1 = await creer_user(
            db, "entreprise1", "entreprise1@test.com", role_company
        )
        entreprise2 = await creer_user(
            db, "entreprise2", "entreprise2@test.com", role_company
        )
        manager1 = await creer_user(
            db, "manager1", "manager1@test.com", role_manager
        )

        # ---- Offres ----
        offre_a = Offre(
            titre="Stage Data Analyst",
            mission="Analyser des jeux de données clients",
            competences="python, sql",
            statut="draft",
            entreprise_id=entreprise1.id,
        )
        offre_b = Offre(
            titre="Stage ML Engineer",
            mission="Entraîner des modèles de classification",
            competences="python, pytorch",
            statut="submitted",
            entreprise_id=entreprise1.id,
        )
        offre_c = Offre(
            titre="Stage Data Engineer",
            mission="Construire des pipelines ETL",
            competences="python, airflow, sql",
            statut="published",
            entreprise_id=entreprise1.id,
        )
        offre_d = Offre(
            titre="Stage BI",
            mission="Créer des dashboards de pilotage",
            competences="sql, powerbi",
            statut="published",
            entreprise_id=entreprise2.id,
        )
        offre_e = Offre(
            titre="Stage IA générative",
            mission="Prototyper un assistant conversationnel",
            competences="python, llm",
            statut="rejected",
            entreprise_id=entreprise2.id,
        )
        db.add_all([offre_a, offre_b, offre_c, offre_d, offre_e])
        await db.flush()

        # ---- Candidatures ----
        # etudiant1 postule sur les 2 offres publiées
        candidature_1 = Candidature(
            statut="pending",
            offre_id=offre_c.id,
            etudiant_id=etudiant1.id,
        )
        candidature_2 = Candidature(
            statut="accepted",
            offre_id=offre_d.id,
            etudiant_id=etudiant1.id,
        )
        # etudiant2 postule aussi, avec des statuts différents
        candidature_3 = Candidature(
            statut="rejected",
            offre_id=offre_c.id,
            etudiant_id=etudiant2.id,
        )
        candidature_4 = Candidature(
            statut="pending",
            offre_id=offre_d.id,
            etudiant_id=etudiant2.id,
        )
        db.add_all(
            [candidature_1, candidature_2, candidature_3, candidature_4]
        )

        await db.commit()

        print("Seed terminé avec succès.\n")
        print(f"Mot de passe commun : {MOT_DE_PASSE_TEST}\n")
        print("Utilisateurs créés :")
        print(f"  student        etudiant1@test.com  (id={etudiant1.id})")
        print(f"  student        etudiant2@test.com  (id={etudiant2.id})")
        print(f"  company        entreprise1@test.com (id={entreprise1.id})")
        print(f"  company        entreprise2@test.com (id={entreprise2.id})")
        print(f"  program_manager manager1@test.com   (id={manager1.id})\n")
        print("Offres créées :")
        print(f"  {offre_a.id} draft     -> entreprise1")
        print(f"  {offre_b.id} submitted -> entreprise1")
        print(f"  {offre_c.id} published -> entreprise1")
        print(f"  {offre_d.id} published -> entreprise2")
        print(f"  {offre_e.id} rejected  -> entreprise2\n")
        print("Candidatures créées :")
        print(f"  {candidature_1.id} pending  etudiant1 -> offre {offre_c.id}")
        print(f"  {candidature_2.id} accepted etudiant1 -> offre {offre_d.id}")
        print(f"  {candidature_3.id} rejected etudiant2 -> offre {offre_c.id}")
        print(f"  {candidature_4.id} pending  etudiant2 -> offre {offre_d.id}")


if __name__ == "__main__":
    asyncio.run(seed())