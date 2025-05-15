from .slack_bp import slack_bp
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import request, jsonify
from services.slack.slack_usage_services import submit_slack_configuration, get_slack_data_and_configuration

@slack_bp.route('/usage/get-slack-data-and-configuration', methods=['GET'])
@jwt_required()
def get_slack_data_and_configuration_route():
    user_id = get_jwt_identity()
    try:
        slack_data_and_configuration = get_slack_data_and_configuration(user_id)
        return jsonify(slack_data_and_configuration), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@slack_bp.route('/usage/submit-slack-configuration', methods=['POST'])
@jwt_required()
def submit_slack_configuration_route():
    user_id = get_jwt_identity()
    data = request.get_json()
    emojis = data.get('emojis', [])
    members = data.get('members', [])
    
    try:
        success = submit_slack_configuration(user_id, emojis, members)
        if success:
            return jsonify({"message": "Configuration saved successfully"}), 200
        else:
            return jsonify({"error": "Unable to save configuration"}), 400
    except Exception as e:
        print(f"Error in submit_slack_configuration_route: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500