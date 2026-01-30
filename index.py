import sys
import os

# Make parent directory visible
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app  # import your Flask app

# Vercel looks for "app"
