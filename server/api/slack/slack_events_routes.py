import os
from dotenv import load_dotenv
load_dotenv()

from flask import request, redirect, jsonify
from models.user.user import User
from models.user.slack_integration import SlackIntegration, SlackOauth
from services.slack.slack_oauth_services import (
    get_slack_oauth_url,
    slack_oauth_callback,
    uninstall_slack
)
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from slack_sdk.signature import SignatureVerifier
import os
from services.slack.slack_events_services import process_slack_event
from .slack_bp import slack_bp
# Initialize the SignatureVerifier with your Slack signing secret
signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

# Load environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL")

@slack_bp.route('/events/webhooks', methods=['POST'])
def slack_events():
    # Verify the request is coming from Slack
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return jsonify({"error": "Invalid request"}), 403

    # Parse the incoming event data
    event_data = request.json

    # Handle URL verification challenge
    if event_data['type'] == 'url_verification':
        return jsonify({"challenge": event_data['challenge']})

    # Process the event
    if event_data['type'] == 'event_callback':
        process_slack_event(event_data)

    # Acknowledge receipt of the event
    return '', 200