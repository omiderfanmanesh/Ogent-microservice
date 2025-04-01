"""
Run application without migrations.

This is a temporary script to run the agent service without migrations.
"""

import uvicorn
import os

# Disable database initialization
os.environ["SKIP_DB_INIT"] = "1"

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 