from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt (irréversible)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed: str) -> bool:
    """Vérifie qu'un mot de passe correspond au hash."""
    return pwd_context.verify(plain_password, hashed)
