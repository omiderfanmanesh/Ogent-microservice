#!/usr/bin/env python
"""
Application startup script.

This script starts the FastAPI application using Uvicorn.
"""

import os
import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Start Uvicorn server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 