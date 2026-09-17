from flask import Flask
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv
import os

from database import db

# --------------------------------------------------
# Load .env from backend folder
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

from config import Config

# --------------------------------------------------
# Flask App
# --------------------------------------------------
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Secret Key
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
db.init_app(app)

# --------------------------------------------------
# Gemini Configuration
# --------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print(f"ENV Path : {ENV_PATH}")

if GEMINI_API_KEY:
    print("✅ Gemini API Loaded")
else:
    print("❌ Gemini API Missing")

# --------------------------------------------------
# Register Blueprints
# (Keep your existing imports)
# --------------------------------------------------
from routes.auth import auth_bp
from routes.farmers import farmers_bp
from routes.animals import animals_bp
from routes.complaints import complaints_bp
from routes.ai import ai_bp


app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(farmers_bp, url_prefix="/api")
app.register_blueprint(animals_bp, url_prefix="/api")
app.register_blueprint(complaints_bp, url_prefix="/api")
app.register_blueprint(ai_bp, url_prefix="/api/ai")


# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.route("/")
def home():
    return {
        "message": "PashuRakshak AI Backend Running",
        "gemini": bool(GEMINI_API_KEY)
    }

# --------------------------------------------------
# Run Server
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)