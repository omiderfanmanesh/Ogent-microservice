"""
API Gateway service for Ogent application.

This service acts as a central entry point for all client requests,
routing them to the appropriate backend services.
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api-gateway")

# Load environment variables
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:80")
MAIN_APP_URL = os.getenv("MAIN_APP_URL", "http://app:8000")
SOCKET_SERVICE_URL = os.getenv("SOCKET_SERVICE_URL", "http://socket-service:8000")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"

# Initialize API clients
auth_client = httpx.AsyncClient(base_url=AUTH_SERVICE_URL, timeout=30.0)
app_client = httpx.AsyncClient(base_url=MAIN_APP_URL, timeout=30.0)
socket_client = httpx.AsyncClient(base_url=SOCKET_SERVICE_URL, timeout=30.0)

# Create FastAPI application
app = FastAPI(
    title="Ogent API Gateway",
    description="API Gateway for Ogent application",
    version="1.0.0",
)

# Configure CORS
origins = os.getenv("ALLOW_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Models
class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None


# Helper functions
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify and decode JWT token to get current user information."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, user_id=user_id)
        return token_data
    except JWTError:
        raise credentials_exception


# Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Routes
@app.get("/", status_code=200)
async def root():
    """API Gateway root endpoint."""
    return {"message": "Welcome to Ogent API Gateway"}


@app.get("/health", status_code=200)
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


# Auth routes
@app.post("/auth/login")
async def login(request: Request):
    """Forward login request to auth service."""
    try:
        body = await request.json()
        response = await auth_client.post("/api/login", json=body)
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except httpx.RequestError as exc:
        logger.error(f"Auth service error: {exc}")
        raise HTTPException(status_code=503, detail="Auth service unavailable")


@app.post("/auth/register")
async def register(request: Request):
    """Forward registration request to auth service."""
    try:
        body = await request.json()
        response = await auth_client.post("/api/register", json=body)
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except httpx.RequestError as exc:
        logger.error(f"Auth service error: {exc}")
        raise HTTPException(status_code=503, detail="Auth service unavailable")


# Forward API requests to main app
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def api_gateway(path: str, request: Request):
    """Forward any request to the appropriate backend service."""
    # Determine target service based on path
    client = app_client
    target_path = path
    
    if path.startswith("auth/"):
        client = auth_client
        # Rewrite path for auth service
        target_path = "api/" + path[5:]  # Remove 'auth/' prefix and add 'api/'
    elif path.startswith("socket/"):
        client = socket_client

    # Get request details
    method = request.method
    url = f"/{target_path}"
    headers = dict(request.headers)
    
    # Remove hop-by-hop headers
    hop_by_hop_headers = [
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "transfer-encoding", "upgrade"
    ]
    for header in hop_by_hop_headers:
        if header.lower() in headers:
            del headers[header.lower()]
    
    # Forward request with parameters, headers and body
    body = await request.body()
    try:
        response = await client.request(
            method=method,
            url=url,
            content=body,
            headers=headers,
            cookies=request.cookies,
            follow_redirects=True,
        )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except httpx.RequestError as exc:
        service_name = "Main app"
        if client == auth_client:
            service_name = "Auth service"
        elif client == socket_client:
            service_name = "Socket service"
        logger.error(f"{service_name} error: {exc}")
        raise HTTPException(status_code=503, detail=f"{service_name} unavailable")


# Shutdown event handlers
@app.on_event("shutdown")
async def shutdown_event():
    """Close HTTP clients on shutdown."""
    await auth_client.aclose()
    await app_client.aclose()
    await socket_client.aclose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 