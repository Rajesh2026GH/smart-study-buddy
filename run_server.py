#!/usr/bin/env python
"""
Simple startup script for Smart Study Buddy API
Handles path setup and runs uvicorn
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Change to current directory
os.chdir(current_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
