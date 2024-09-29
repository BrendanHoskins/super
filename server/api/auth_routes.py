from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    set_refresh_cookies, unset_jwt_cookies
)
from services.auth.auth_services import register_user, authenticate_user
from datetime import timedelta
import logging
import traceback

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    result, status_code = register_user(data)
    return jsonify(result), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400
        user = authenticate_user(username, password)
        if user:
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            response = jsonify(access_token=access_token)
            # Set the refresh token in a secure HttpOnly cookie
            set_refresh_cookies(response, refresh_token)
            return response, 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Login error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"message": "An error occurred during login"}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=['cookies'])
def refresh():
    try:
        identity = get_jwt_identity()
        logging.info(f"Refreshing token for user: {identity}")
        access_token = create_access_token(identity=identity)
        response = jsonify(access_token=access_token)
        return response, 200
    except Exception as e:
        logging.error(f"Error refreshing token: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"message": "An error occurred while refreshing the token"}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    response = jsonify({"message": "Logged out"})
    unset_jwt_cookies(response)
    return response, 200
