import sys
import os

# Add root directory to sys.path so 'app' package is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
