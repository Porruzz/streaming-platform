# libs/common-py/common/auth/jwt.py
from typing import Optional
import jwt
from jwt import PyJWKClient

class JWTError(Exception):
    pass

def decode_jwt_rs256(token: str, jwks_url: Optional[str] = None, public_key_pem: Optional[str] = None, audience: Optional[str] = None) -> dict:
    try:
        if public_key_pem:
            return jwt.decode(token, public_key_pem, algorithms=["RS256"], audience=audience)
        if not jwks_url:
            raise JWTError("Provide jwks_url or public_key_pem")
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        return jwt.decode(token, signing_key, algorithms=["RS256"], audience=audience)
    except Exception as e:
        raise JWTError(str(e))
