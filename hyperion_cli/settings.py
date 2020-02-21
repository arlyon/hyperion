import os

# settings.py
from dotenv import load_dotenv
load_dotenv()

SERVER_HOST = os.getenv("HYPERION_HOST", "0.0.0.0")
SERVER_PORT = os.getenv("HYPERION_PORT", "8080")
