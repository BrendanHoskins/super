import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root first (so local runs find it); then cwd (Docker injects env, so file optional)
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")
load_dotenv()

from flask import Flask, jsonify, make_response
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from flask_cors import CORS
from mongoengine import connect
from bson.objectid import ObjectId
from datetime import datetime, timezone, timedelta
import logging
import warnings

# Mongoengine warns when a subclass sets 'collection'; harmless here.
warnings.filterwarnings('ignore', message='.*Trying to set a collection on a subclass.*', module='mongoengine.*')

from models.user.user import User
from api.slack.slack_bp import slack_bp
from api.auth_routes import auth_bp
from api.integrations_routes import integrations_routes
from api.messages_routes import messages_bp

# Load environment variables (Docker sets MONGO_URI, FRONTEND_URL, BACKEND_URL via port scanner)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_PROJECT_NAME = os.getenv('MONGO_PROJECT_NAME', 'super')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY  # Set the secret key from .env
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token_cookie'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # For simplicity; consider enabling in production
app.config['JWT_COOKIE_SECURE'] = False  # True in production with HTTPS
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # So refresh cookie is sent when frontend (e.g. :3000) calls backend (:5000)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=90)  # Gmail-style: stay logged in across browser closes
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # 24h so leaving tab open and returning doesn't require refresh
app.config['JWT_SESSION_COOKIE'] = False  # Persist refresh cookie with max_age so it survives tab/background and isn't lost
app.config['JWT_REFRESH_COOKIE_PATH'] = '/'  # Ensure refresh cookie is sent for all backend paths

# Initialize MongoDB connection using mongoengine
connect(
    db=MONGO_PROJECT_NAME,
    host=MONGO_URI
)

jwt = JWTManager(app)

# CORS: allow FRONTEND_URL only (set by Docker or .env at repo root)
CORS(app, supports_credentials=True, origins=[FRONTEND_URL] if FRONTEND_URL else [])


# Token blacklist set
jwt_blocklist = set()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Only show errors/warnings, not every request line
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('mongoengine').setLevel(logging.WARNING)
logging.getLogger('flask_mongoengine').setLevel(logging.WARNING)


app.register_blueprint(slack_bp, url_prefix='/api/slack')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(integrations_routes, url_prefix='/api/integrations')
app.register_blueprint(messages_bp, url_prefix='/api/messages')

# Error Handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# JWT Configuration
@jwt.user_identity_loader
def user_identity_lookup(user):
    if isinstance(user, User):
        return str(user.id)
    return user  # If it's already a string, return it as is

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.objects(id=ObjectId(identity)).first()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in jwt_blocklist

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=port,
    )