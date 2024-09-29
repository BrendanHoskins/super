from models.user.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine.errors import NotUniqueError
import logging

def register_user(data):
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return {"message": "Username and password are required"}, 400
    # Check if user already exists
    existing_user = User.objects(username=username).first()
    if existing_user:
        return {"message": "User already exists"}, 400
    # Hash the password
    hashed_password = generate_password_hash(password)
    # Create user
    user = User(username=username, password=hashed_password)
    try:
        user.save()
        return {"message": "User registered successfully"}, 201
    except NotUniqueError:
        return {"message": "User already exists"}, 400

def authenticate_user(username, password):
    try:
        user = User.objects(username=username).first()
        if user and check_password_hash(user.password, password):
            return user  # Return the entire user object
        else:
            return None
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        return None
