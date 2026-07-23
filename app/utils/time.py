import datetime


def utcnow() -> datetime.datetime:
    """Heure UTC courante, centralisée pour tout le projet."""
    return datetime.datetime.utcnow()