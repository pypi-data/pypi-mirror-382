"""
StringSight API package.

This package contains API endpoints and related utilities for the StringSight
metrics system.
"""

__version__ = "0.1.0"

# Import the main FastAPI app from the parent api.py file
import sys
from pathlib import Path

# Add parent directory to path to import from api.py
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from api import app
except ImportError:
    # Fallback - create a minimal app if import fails
    from fastapi import FastAPI
    app = FastAPI(title="StringSight API", version="0.1.0")

__all__ = ['app']