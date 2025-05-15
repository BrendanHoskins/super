import os
from dotenv import load_dotenv
load_dotenv()

from flask import request, jsonify
from slack_sdk.signature import SignatureVerifier
import os
from services.slack.slack_events_services import process_slack_event
from .slack_bp import slack_bp

signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])


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