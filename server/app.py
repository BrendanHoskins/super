import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, make_response
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from flask_cors import CORS
from mongoengine import connect
from bson.objectid import ObjectId
from datetime import datetime, timezone, timedelta
import logging

from models.user.user import User
from api.slack.slack_bp import slack_bp
from api.auth_routes import auth_bp
from api.integrations_routes import integrations_routes
from api.messages_routes import messages_bp

# Load environment variables
MONGO_URI = os.getenv('MONGO_URI')
MONGO_PROJECT_NAME = os.getenv('MONGO_PROJECT_NAME')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
FRONTEND_URL = os.getenv('FRONTEND_URL')
BACKEND_URL = os.getenv('BACKEND_URL')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY  # Set the secret key from .env
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token_cookie'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # For simplicity; consider enabling in production
app.config['JWT_COOKIE_SECURE'] = False  # True in production with HTTPS
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # 30-day refresh token expiration

# Initialize MongoDB connection using mongoengine
connect(
    db=MONGO_PROJECT_NAME,
    host=MONGO_URI
)

jwt = JWTManager(app)

# Updated CORS configuration
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])

# Token blacklist set
jwt_blocklist = set()

# Configure logging
logging.basicConfig(level=logging.INFO)  # Changed from DEBUG to INFO

# Disable MongoDB logging
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
    app.run(
        debug=True,
        host='{BACKEND_URL}',
        port=5000
    )