from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlencode
import requests

from core.config import settings
from services.auth_service import get_current_user, keycloak_auth

router = APIRouter()


@router.get("/login")
async def keycloak_login(request: Request, redirect: str = "/"):
    """Redirect the browser to Keycloak authorization endpoint.

    Query param `redirect` is the frontend path to redirect after successful login.
    """
    # For browser requests, use the external URL
    auth_endpoint = f"{settings.keycloak_external_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/auth"

    # Use the frontend URL for redirects
    callback_url = f"http://localhost:3000/auth/callback"

    params = {
        "client_id": settings.keycloak_client_id,
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": f"{callback_url}?{urlencode({'redirect': redirect})}",
    }

    url = f"{auth_endpoint}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/callback")
async def keycloak_callback(request: Request):
    """Handle Keycloak callback: exchange code for tokens and set access_token cookie."""
    code = request.query_params.get("code")
    redirect_after = request.query_params.get("redirect") or "/"

    # Ensure redirect path starts with /
    if not redirect_after.startswith("/"):
        redirect_after = "/" + redirect_after

    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)

    # For internal token requests between containers, use the internal Keycloak URL with /auth path
    token_url = f"{settings.keycloak_url}/auth/realms/{settings.keycloak_realm}/protocol/openid-connect/token"

    # For callback URL sent to keycloak, use the frontend URL with /auth/callback path
    callback_url = "http://localhost:3000/auth/callback"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{callback_url}?{urlencode({'redirect': redirect_after})}",
        "client_id": settings.keycloak_client_id
    }

    if settings.keycloak_client_secret:
        data["client_secret"] = settings.keycloak_client_secret

    # Exchange code for token
    # Log token exchange details to help debugging in container logs
    try:
        print("[auth] Exchanging code for token:", token_url, data.get("redirect_uri"))
    except Exception:
        pass
    resp = requests.post(token_url, data=data)
    if resp.status_code != 200:
        return JSONResponse({"error": "Token exchange failed", "details": resp.text}, status_code=400)

    token_data = resp.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return JSONResponse({"error": "No access token in response"}, status_code=400)

    # Set HttpOnly cookie and redirect to frontend page
    response = RedirectResponse(redirect_after)
    # Cookie options: in production set secure=True and proper domain
    response.set_cookie("access_token", access_token, httponly=True, samesite="lax")
    return response


@router.get("/user")
async def current_user(user: dict = Depends(get_current_user)):
    """Return current authenticated user info (uses cookie or Authorization header)."""
    # Extract roles/groups for frontend
    roles = []
    try:
        if keycloak_auth and user:
            roles = keycloak_auth.get_user_roles(user)
    except Exception:
        roles = []
    try:
        print("[auth:user] resolved roles:", roles)
    except Exception:
        pass

    return {
        "user": {
            "id": user.get("sub") or user.get("id"),
            "username": user.get("preferred_username") or user.get("username") or user.get("email"),
            "name": user.get("name") or user.get("preferred_username"),
            "roles": roles,
            "raw": user
        }
    }


@router.get("/logout")
async def logout(redirect: str = "http://localhost:3000/"):
    """Clear session cookie and redirect to Keycloak logout to end single sign-on session."""
    # Keycloak uses the '/auth' relative path inside the container
    logout_url = f"{settings.keycloak_url}/auth/realms/{settings.keycloak_realm}/protocol/openid-connect/logout"
    # After logout, redirect to frontend
    params = {"redirect_uri": redirect}
    response = RedirectResponse(f"{logout_url}?{urlencode(params)}")
    # Clear cookie
    response.delete_cookie("access_token")
    return response
