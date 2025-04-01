import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

# This ensures pytest can find the 'app' module
# The tests/conftest.py file will be imported automatically by pytest 