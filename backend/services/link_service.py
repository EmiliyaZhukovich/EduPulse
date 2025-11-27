import secrets
import string

def generate_unique_token(length: int = 32) -> str:
    """Generate unique token for survey link"""
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token
