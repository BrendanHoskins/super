from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.dashboard_services import get_user_slack_messages

messages_bp = Blueprint('messages_bp', __name__)

@messages_bp.route('/get-messages', methods=['GET'])
@jwt_required()
def get_messages_data():
    user_id = get_jwt_identity()
    messages = get_user_slack_messages(user_id)
    return jsonify(messages), 200
