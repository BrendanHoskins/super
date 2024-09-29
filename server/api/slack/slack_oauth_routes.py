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
from .slack_bp import slack_bp
# Initialize the SignatureVerifier with your Slack signing secret
signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

# Load environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL")



@slack_bp.route('/oauth/install')
@jwt_required()
def slack_oauth_install_route():
    """
    Start Slack OAuth process.
    """
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    auth_url = get_slack_oauth_url(user)
    return jsonify({"authUrl": auth_url})

@slack_bp.route('/oauth/callback')
def slack_oauth_callback_route():
    """
    Slack OAuth callback endpoint.
    """
    code = request.args.get("code")
    state = request.args.get("state")
    error = request.args.get("error")

    if error:
        return redirect(f"{FRONTEND_URL}/integrations/slack-oauth-callback?error={error}")

    if state:
        # Find the user with this state
        user = User.objects(thirdPartyIntegrations__slack__oauth__state=state).first()
        if user:
            # Check if state is not expired
            slack_oauth = user.thirdPartyIntegrations['slack'].oauth
            if slack_oauth.expires_at >= datetime.utcnow():
                # State is valid, proceed to exchange code for tokens
                installation, status_code = slack_oauth_callback(code)
                if status_code == 200:
                    # Save installation details to user's SlackIntegration
                    slack_integration = user.thirdPartyIntegrations.get('slack', SlackIntegration())
                    slack_integration.installation = installation
                    slack_integration.enabled = True
                    slack_integration.oauth = None  # Clear the OAuth state
                    user.thirdPartyIntegrations['slack'] = slack_integration
                    user.save()

                    # Redirect to frontend with success
                    return redirect(f"{FRONTEND_URL}/integrations/slack-oauth-callback?success=true")
                else:
                    error_message = installation.get('error', 'Unknown error')
                    return redirect(f"{FRONTEND_URL}/integrations/slack-oauth-callback?error={error_message}")
            else:
                # State is expired
                return redirect(f"{FRONTEND_URL}/integrations/slack-oauth-callback?error=State expired")
        else:
            # State not found
            return redirect(f"{FRONTEND_URL}/integrations/slack-oauth-callback?error=Invalid state")
    else:
        # State not provided in callback
        return redirect(f"{FRONTEND_URL}/integrations/slack-oauth-callback?error=State missing")

@slack_bp.route('/oauth/uninstall', methods=['POST'])
@jwt_required()
def slack_uninstall_route():
    """
    Uninstall Slack integration for the current user.
    """
    user_id = get_jwt_identity()

    if uninstall_slack(user_id):
        return jsonify({"message": "Slack integration disconnected successfully"}), 200
    else:
        return jsonify({"error": "No Slack integration found for this user"}), 404