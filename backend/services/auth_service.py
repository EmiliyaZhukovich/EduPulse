from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import requests
import urllib.parse

from core.config import settings

security = HTTPBearer(auto_error=False)

class KeycloakAuth:
    def __init__(self, keycloak_url: str, realm: str, client_id: str):
        self.keycloak_url = keycloak_url
        self.realm = realm
        self.client_id = client_id
        # Use the standard OpenID Connect discovery URL (note the hyphen)
        self.well_known_url = f"{keycloak_url}/auth/realms/{realm}/.well-known/openid-configuration"

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token with Keycloak"""
        try:
            response = requests.get(self.well_known_url)
            if response.status_code != 200:
                print(f"Failed to fetch well-known config: {response.status_code}")
                return None

            headers = {"Authorization": f"Bearer {token}"}
            userinfo_url = f"{self.keycloak_url}/auth/realms/{self.realm}/protocol/openid-connect/userinfo"

            try:
                external_netloc = urllib.parse.urlparse(settings.keycloak_external_url).netloc
            except Exception:
                external_netloc = None

            if external_netloc:
                headers['Host'] = external_netloc
                headers['X-Forwarded-Host'] = external_netloc
                headers['X-Forwarded-Proto'] = urllib.parse.urlparse(settings.keycloak_external_url).scheme or 'http'

            user_response = requests.get(userinfo_url, headers=headers)
            if user_response.status_code == 200:
                return user_response.json()

            print(f"Userinfo request failed: {user_response.status_code} {user_response.text}")
            return None

        except Exception as e:
            print(f"Token verification error: {e}")
            return None

    def get_user_roles(self, user_info: dict) -> list:
        """Extract roles from user info"""
        roles = []

        # Check realm roles
        if "realm_access" in user_info and "roles" in user_info["realm_access"]:
            roles.extend(user_info["realm_access"]["roles"])

        # Check client roles
        if "resource_access" in user_info and self.client_id in user_info["resource_access"]:
            client_roles = user_info["resource_access"][self.client_id].get("roles", [])
            roles.extend(client_roles)

        # Also include groups as roles (Keycloak may provide groups in 'groups' claim)
        if "groups" in user_info and isinstance(user_info["groups"], list):
            # groups may look like ['/администраторы', '/кураторы']
            for g in user_info["groups"]:
                if isinstance(g, str):
                    grp = g.strip().split('/')[-1]
                    if grp:
                        roles.append(grp)

        return roles

# Global instance
keycloak_auth = None

def init_keycloak_auth(keycloak_url: str, realm: str, client_id: str):
    """Initialize Keycloak authentication"""
    global keycloak_auth
    keycloak_auth = KeycloakAuth(keycloak_url, realm, client_id)

def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user.

    Support both Authorization: Bearer <token> and cookie 'access_token'.
    """
    if not keycloak_auth:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keycloak not configured"
        )

    token = None

    # First try Authorization header (HTTPBearer)
    if credentials and credentials.credentials:
        token = credentials.credentials

    # If no header token, try cookie
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user_info = keycloak_auth.verify_token(token)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return user_info

def require_role(required_role: str):
    """Decorator to require specific role or group name."""
    def role_checker(user: dict = Depends(get_current_user)):
        roles = keycloak_auth.get_user_roles(user)

        def _normalize(name: str) -> set:
            if not isinstance(name, str):
                return set()
            n = name.lower().strip()
            if '/' in n:
                n = n.split('/')[-1]
            variants = {n}
            if n.endswith('s'):
                variants.add(n[:-1])
            else:
                variants.add(n + 's')
            return variants

        normalized_roles = set()
        for r in roles or []:
            normalized_roles.update(_normalize(r))

        if required_role not in normalized_roles and not (_normalize(required_role) & normalized_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role or group: {required_role}"
            )
        return user
    return role_checker

def get_admin_user(user: dict = Depends(require_role("admins"))):
    """Get admin user (accepts Keycloak group 'admins')."""
    return user

def get_curator_user(user: dict = Depends(require_role("curators"))):
    """Get curator user (accepts Keycloak group 'curators')."""
    return user
