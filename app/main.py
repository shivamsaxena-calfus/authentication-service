from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
import httpx
import os

app = FastAPI()

KEYCLOAK_URL = os.getenv('KEYCLOAK_BASE_URL')
REALM = os.getenv('KEYCLOAK_REALM')
CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID')
CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET')
PUBLIC_KEY_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
ALGORITHM = "RS256"
INTROSPECT_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token/introspect"


@app.post("/token")
async def request_token(username: str, password: str):
    """Request a token from Keycloak"""
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, headers=headers, data=data)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"An error occurred while requesting the token: {str(exc)}")

    return response.json()


async def introspect_token(token: str) -> dict:
    data = {
        'token': token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(INTROSPECT_URL, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to introspect token")
        return response.json()

@app.post("/introspect-token")
async def introspect_token_endpoint(token: str):
    token_info = await introspect_token(token)
    if token_info.get('active'):
        return {"detail": "Token is active", "token_info": token_info}
    else:
        raise HTTPException(status_code=401, detail="Token is inactive")

