import os
from dotenv import load_dotenv
load_dotenv()

from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

from models.user.slack_integration import SlackInstallation, SlackOauth, SlackIntegration

from datetime import datetime, timedelta
import uuid
from models.user.user import User
from threading import Lock
import boto3
from bson import ObjectId
from models.slack.slack_message import SlackMessage
from mongoengine.queryset.visitor import Q

refresh_lock = Lock()
user_refresh_lock = Lock()

# Load environment variables
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = os.getenv("SLACK_REDIRECT_URI")
SLACK_USER_SCOPES = os.getenv("SLACK_USER_SCOPES")

# Initialize the AuthorizeUrlGenerator
authorize_url_generator = AuthorizeUrlGenerator(
    client_id=SLACK_CLIENT_ID,
    user_scopes=[SLACK_USER_SCOPES]
)

def get_slack_oauth_url(user):
    """
    Generate Slack OAuth URL using slack_sdk, save state to user's SlackIntegration.
    """
    # Generate a unique state
    state = str(uuid.uuid4())
    # Store state and expiration in user's SlackIntegration
    expires_at = datetime.utcnow() + timedelta(seconds=300)  # 5 minutes

    # Find or create the SlackIntegration for the user
    slack_integration = user.thirdPartyIntegrations.get('slack', SlackIntegration())
    slack_integration.oauth = SlackOauth(
        state=state,
        expires_at=expires_at
    )
    user.thirdPartyIntegrations['slack'] = slack_integration
    user.save()

    # Generate the auth URL
    url = authorize_url_generator.generate(state)
    return url

def slack_oauth_callback(code):
    """
    Handle Slack OAuth callback logic.
    """
    if code:
        client = WebClient()  # No prepared token needed for this
        try:
            # Complete the installation by calling oauth.v2.access API method
            oauth_response = client.oauth_v2_access(
                client_id=SLACK_CLIENT_ID,
                client_secret=SLACK_CLIENT_SECRET,
                redirect_uri=SLACK_REDIRECT_URI,
                code=code
            )
            print(oauth_response)
            installed_enterprise = oauth_response.get("enterprise") or {}
            is_enterprise_install = oauth_response.get("is_enterprise_install")
            installed_team = oauth_response.get("team") or {}
            incoming_webhook = oauth_response.get("incoming_webhook") or {}
            bot_token = oauth_response.get("access_token")
            bot_id = None
            enterprise_url = None
            if bot_token is not None:
                auth_test = client.auth_test(token=bot_token)
                bot_id = auth_test["bot_id"]
                print(auth_test)
                if is_enterprise_install is True:
                    enterprise_url = auth_test.get("url")
            # Calculate the expiration datetime
            expires_in = oauth_response.get("expires_in")
            if expires_in is not None:
                expires_at = datetime.now() + timedelta(seconds=int(expires_in))
            else:
                expires_at = None

            # Calculate user token expiration
            user_expires_in = oauth_response.get("authed_user", {}).get("expires_in")
            user_expires_at = None
            if user_expires_in is not None:
                user_expires_at = datetime.now() + timedelta(seconds=int(user_expires_in))

            installation = SlackInstallation(
                app_id=oauth_response.get("app_id"),
                enterprise_id=installed_enterprise.get("id"),
                enterprise_name=installed_enterprise.get("name"),
                enterprise_url=enterprise_url,
                team_id=installed_team.get("id"),
                team_name=installed_team.get("name"),
                bot_token=bot_token,
                bot_id=bot_id,
                bot_user_id=oauth_response.get("bot_user_id"),
                bot_scopes=oauth_response.get("scope"),
                user_id=oauth_response.get("authed_user", {}).get("id"),
                user_token=oauth_response.get("authed_user", {}).get("access_token"),
                user_scopes=oauth_response.get("authed_user", {}).get("scope", "").split(","),
                incoming_webhook_url=incoming_webhook.get("url"),
                incoming_webhook_channel=incoming_webhook.get("channel"),
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
                is_enterprise_install=is_enterprise_install,
                token_type=oauth_response.get("token_type"),
                bot_refresh_token=oauth_response.get("refresh_token"),
                bot_token_expires_at=expires_at,
                user_token_type=oauth_response.get("authed_user", {}).get("token_type"),
                user_refresh_token=oauth_response.get("authed_user", {}).get("refresh_token"),
                user_token_expires_at=user_expires_at,
            )
            return installation, 200
        except SlackApiError as e:
            return {"error": str(e)}, 400

    return {"error": "Invalid request"}, 400

def get_bot_refresh_token(user_id):
    """
    Get the bot token for a user, refreshing if necessary and updating the MongoDB document.
    """
    user = User.objects(id=user_id).first()
    if not user:
        print(f"User with id {user_id} not found")
        return None
    
    slack_integration = user.thirdPartyIntegrations.get('slack')
    if not slack_integration or not slack_integration.installation:
        return None

    installation = slack_integration.installation
    
    with refresh_lock:
        current_time = datetime.utcnow()
        
        # Check if token needs refreshing (if it's expired or will expire in the next 5 minutes)
        if not installation.bot_token or not installation.bot_token_expires_at or \
           installation.bot_token_expires_at <= current_time + timedelta(minutes=5):
            client = WebClient()
            try:
                refresh_response = client.oauth_v2_access(
                    client_id=SLACK_CLIENT_ID,
                    client_secret=SLACK_CLIENT_SECRET,
                    grant_type="refresh_token",
                    refresh_token=installation.bot_refresh_token
                )
                
                # Update the installation document with new token information
                installation.bot_token = refresh_response["access_token"]
                installation.bot_refresh_token = refresh_response["refresh_token"]
                expires_in = refresh_response["expires_in"]
                installation.bot_token_expires_at = current_time + timedelta(seconds=int(expires_in))
                
                # Save the updated user document
                user.save()
                
                print("Slack bot token refreshed successfully")
            except SlackApiError as e:
                print(f"Error refreshing Slack token: {e}")
                return None

    return installation.bot_token

def uninstall_slack(user_id):
    """
    Disconnect Slack integration for the user and remove associated files efficiently.
    """
    user_object_id = ObjectId(user_id)

    user = User.objects(pk=user_object_id).first()
    if not user or 'slack' not in user.thirdPartyIntegrations:
        return False

    update_result = User.objects(pk=user_object_id).update_one(
        __raw__={
            '$unset': {'thirdPartyIntegrations.slack': 1}
        }
    )

    if update_result == 0:
        return False

    slack_message_ids = SlackMessage.objects(
        Q(relevant_user_id=user_object_id) & Q(source='slack_integration')
    ).scalar('id')

    if slack_message_ids:
        SlackMessage.objects(id__in=slack_message_ids).delete()

        s3_client = boto3.client('s3')
        bucket_name = os.getenv('FILES_TO_EXTRACT_INSIGHTS_FROM_S3_BUCKET_NAME')

        s3_keys = [
            f"every_user_uploaded_file_converted_to_txt/{message_id}"
            for message_id in slack_message_ids
        ]

        try:
            for i in range(0, len(s3_keys), 1000):
                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': [{'Key': key} for key in s3_keys[i:i+1000]]}
                )
        except Exception as e:
            print(f"Error deleting S3 objects: {str(e)}")

    return True

def get_user_refresh_token(user_id):
    """
    Get the user token for a user, refreshing if necessary and updating the MongoDB document.
    """
    user = User.objects(id=user_id).first()
    if not user:
        print(f"User with id {user_id} not found")
        return None
    
    slack_integration = user.thirdPartyIntegrations.get('slack')
    if not slack_integration or not slack_integration.installation:
        return None

    installation = slack_integration.installation
    
    with user_refresh_lock:
        current_time = datetime.utcnow()
        
        # Check if token needs refreshing (if it's expired or will expire in the next 5 minutes)
        if not installation.user_token or not installation.user_token_expires_at or \
           installation.user_token_expires_at <= current_time + timedelta(minutes=5):
            client = WebClient()
            try:
                refresh_response = client.oauth_v2_access(
                    client_id=SLACK_CLIENT_ID,
                    client_secret=SLACK_CLIENT_SECRET,
                    grant_type="refresh_token",
                    refresh_token=installation.user_refresh_token
                )
                
                # Update the installation document with new token information
                installation.user_token = refresh_response["access_token"]
                installation.user_refresh_token = refresh_response["refresh_token"]
                expires_in = refresh_response["expires_in"]
                installation.user_token_expires_at = current_time + timedelta(seconds=int(expires_in))
                
                # Save the updated user document
                user.save()
                
                print("Slack user token refreshed successfully")
            except SlackApiError as e:
                print(f"Error refreshing Slack user token: {e}")
                return None

    return installation.user_token
