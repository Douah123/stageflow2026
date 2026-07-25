# StageFlow API

API de gestion de stages (offres, candidatures, entreprises, program managers) construite avec **FastAPI**, **SQLAlchemy 2.0 (async)** et **PostgreSQL**, avec authentification JWT (access + refresh token) et permissions basées sur les rôles.

## Sommaire

- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Variables d'environnement](#variables-denvironnement)
- [Lancer le projet en local](#lancer-le-projet-en-local)
- [Lancer le projet avec Docker](#lancer-le-projet-avec-docker)
- [Lancer les tests](#lancer-les-tests)
- [Données de démonstration](#données-de-démonstration)
- [Rôles et permissions](#rôles-et-permissions)
- [Documentation de l'API](#documentation-de-lapi)
- [Structure du projet](#structure-du-projet)

## Stack technique

- **FastAPI** + **Uvicorn** / **Gunicorn** (production)
- **SQLAlchemy 2.0** en mode asynchrone + **asyncpg**
- **PostgreSQL 15**
- **Alembic** pour les migrations
- **Pydantic v2** pour la validation des schémas
- **JWT** (python-jose) pour l'authentification
- **pytest** + **pytest-cov** pour les tests (SQLite en mémoire)
- **Docker** / **docker compose** pour la conteneurisation
- **GitHub Actions** pour l'intégration continue

## Prérequis

- Python 3.11+
- PostgreSQL 15 (sauf si vous utilisez uniquement Docker)
- Docker et Docker Compose (optionnel, mais recommandé)

## Installation

```bash
git clone https://github.com/Douah123/stageflow2026.git
cd stageflow2026

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Variables d'environnement

Copiez `.env.example` vers `.env` et adaptez les valeurs :

```bash
cp .env.example .env
```

| Variable | Description | Exemple |
|---|---|---|
| `DATABASE_URL` | URL de connexion PostgreSQL (driver async `asyncpg`) | `postgresql+asyncpg://postgres:password@localhost:5432/stageflow` |
| `SECRET_KEY` | Clé secrète utilisée pour signer les JWT | une longue chaîne aléatoire |
| `DEBUG` | Active le mode debug de FastAPI | `true` / `false` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie du token d'accès (minutes) | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Durée de vie du refresh token (jours) | `7` |
| `ALLOWED_ORIGINS` | Origines autorisées pour le CORS, séparées par des virgules | `http://127.0.0.1:8000,http://localhost:8000` |
| `APP_NAME` | Nom affiché de l'application | `StageFlow API` |

⚠️ Ne jamais committer le fichier `.env` (il est déjà exclu via `.gitignore`).

## Lancer le projet en local

1. Démarrer une instance PostgreSQL locale et créer la base indiquée dans `DATABASE_URL`.
2. Appliquer les migrations :

   ```bash
   alembic upgrade head
   ```

   Cette étape crée le schéma **et** peuple la table `roles` (`student`, `company`, `program_manager`, `admin`).

3. Lancer le serveur de développement :

   ```bash
   uvicorn app.main:app --reload
   ```

4. L'API est disponible sur `http://127.0.0.1:8000`, la documentation interactive sur `http://127.0.0.1:8000/docs`.

## Lancer le projet avec Docker

```bash
docker compose up --build
```

Cette commande démarre trois services :

- `db` : PostgreSQL 15, avec healthcheck
- `migrations` : applique `alembic upgrade head` puis s'arrête
- `api` : l'API FastAPI (Gunicorn + workers Uvicorn), démarrée seulement une fois la base prête

L'API est alors disponible sur `http://localhost:8000`.

## Lancer les tests

```bash
pytest
```

La configuration (dans `pyproject.toml`) exécute automatiquement la suite avec couverture de code (seuil minimum : 80%). Les tests utilisent une base **SQLite en mémoire** dédiée, indépendante de `DATABASE_URL`.

Pour un rapport détaillé des lignes non couvertes :

```bash
pytest --cov=app --cov-report=term-missing
```

## Données de démonstration

Deux scripts permettent de peupler la base avec des données réalistes (à exécuter après `alembic upgrade head`) :

```bash
# Crée un compte administrateur (admin@gmail.com / Admin1234#)
python -m app.scripts.admin

# Crée des étudiants, entreprises, un program manager, des offres et des candidatures
python -m app.scripts.seed_data
```

## Rôles et permissions

| Rôle | Peut faire |
|---|---|
| **student** | S'inscrire/se connecter, consulter les offres publiées, postuler à une offre, consulter ses propres candidatures (`/candidatures/me`), retirer une candidature non acceptée |
| **company** | Créer une offre (brouillon), la modifier tant qu'elle est en brouillon, la soumettre pour validation, consulter les candidatures reçues sur ses propres offres |
| **program_manager** | Valider ou refuser une offre soumise, consulter les candidatures de n'importe quelle offre, accepter/refuser une candidature, consulter les statistiques globales (`/stats`) |
| **admin** | Lister les utilisateurs, modifier le rôle ou l'activation d'un compte |

Le cycle de vie d'une offre : `draft` → `submitted` → `published` / `rejected`.
Le cycle de vie d'une candidature : `pending` → `accepted` / `rejected`.

## Documentation de l'API

Une fois le serveur lancé :

- Swagger UI : `http://127.0.0.1:8000/docs`
- ReDoc : `http://127.0.0.1:8000/redoc`

Les routes sont regroupées par tag (`Authentification`, `Offres`, `Candidatures`, `Admin`, `Stats`, `Users`), avec les modèles de requête/réponse et les codes d'erreur documentés pour les routes sensibles (connexion, revue d'offre, décision sur une candidature, gestion des comptes).

## Structure du projet

```
app/
├── api/routes/       # Endpoints FastAPI (auth, offre, candidature, admin, stats)
├── core/             # Configuration, sécurité (JWT), permissions RBAC
├── db/                # Session SQLAlchemy, base déclarative, types custom
├── middlewares/       # Request ID, en-têtes de sécurité
├── models/            # Modèles SQLAlchemy
├── repositories/      # Accès aux données (CRUD générique + spécifique)
├── schemas/            # Schémas Pydantic (validation entrée/sortie)
├── scripts/            # Scripts de seed (admin, données de démo)
└── utils/              # Hashing, pagination, dates

alembic/                # Migrations de schéma et de données (seed des rôles)
tests/
├── integration/        # Tests bout en bout via l'API (httpx + ASGITransport)
└── unit/                # Tests unitaires (schémas, repositories)
```
