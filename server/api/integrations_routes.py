from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.integrations_services import get_user_integrations

integrations_routes = Blueprint('integrations_routes', __name__)

@integrations_routes.route('/connected-integrations', methods=['GET'])
@jwt_required()
def get_integrations():
    user_id = get_jwt_identity()
    integrations = get_user_integrations(user_id)
    return jsonify(integrations)
