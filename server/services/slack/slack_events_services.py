from models.user.user import User
from models.slack.slack_message import SlackMessage
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .slack_oauth_services import get_user_refresh_token
from bson import ObjectId

def process_slack_event(event_data):
    event = event_data.get('event')
    if not event:
        print("Invalid event data: missing event")
        return

    # Get the list of authorizations
    authorizations = event_data.get('authorizations', [])
    # For each authorization, get the user_id and team_id
    for authorization in authorizations:
        auth_user_id = authorization.get('user_id')
        team_id = authorization.get('team_id')

        if not team_id or not auth_user_id:
            print("Invalid authorization data: missing team_id or user_id")
            continue

        # Find all users in our database with matching team_id and user_id
        users = User.objects(
            thirdPartyIntegrations__slack__installation__team_id=team_id,
            thirdPartyIntegrations__slack__installation__user_id=auth_user_id
        )
        
        if not users:
            print(f"No users found with Slack integration for team {team_id} and user_id {auth_user_id}")
            continue  # Skip to the next authorization instead of returning

        # Process the event for each matching user
        for user in users:
            # Proceed to check if the event is relevant to this user
            slack_integration = user.thirdPartyIntegrations.get('slack')
            if not slack_integration:
                continue

            user_team_config = slack_integration.user_team_configuration
            user_emoji_config = slack_integration.user_emoji_configuration

            if not user_team_config or not user_emoji_config:
                continue  # User hasn't configured team members or emojis

            if is_event_relevant_to_user(event, user_team_config, user_emoji_config):
                event_type = event.get('type')
                if event_type == 'reaction_added':
                    # Fetch and save the message for this user
                    save_message_for_user(user, event)
                elif event_type == 'reaction_removed':
                    # Remove the message for this user
                    remove_message_for_user(user, event)
                elif event_type == 'message':
                    subtype = event.get('subtype')
                    if subtype == 'message_changed':
                        # Update the message for this user
                        update_message_for_user(user, event)
                    elif subtype == 'message_deleted':
                        # Remove the message for this user
                        remove_message_for_user(user, event)
                    else:
                        # Handle new messages if needed
                        pass
            # Handle other event types if necessary

def is_event_relevant_to_user(event, user_team_config, user_emoji_config):
    event_type = event.get('type')

    if event_type == 'message':
        subtype = event.get('subtype')
        if subtype == 'message_changed':
            # Message has been edited
            edited_message = event.get('message', {})
            user_id = edited_message.get('user')
            if not user_id:
                return False

            # Check if the message is from a selected team member
            is_user_selected = any(member.id == user_id for member in user_team_config)
            if not is_user_selected:
                return False

            # No emoji check needed for edits; we update if we already have the message
            return True
        elif subtype == 'message_deleted':
            # Message has been deleted
            previous_message = event.get('previous_message', {})
            user_id = previous_message.get('user')
            if not user_id:
                return False

            # Check if the deleted message is from a selected team member
            is_user_selected = any(member.id == user_id for member in user_team_config)
            return is_user_selected

    elif event_type == 'reaction_added':
        # Existing logic for reaction_added
        reactor_user_id = event.get('user')
        is_user_selected = any(member.id == reactor_user_id for member in user_team_config)
        if not is_user_selected:
            return False

        reaction = f":{event.get('reaction')}:"
        selected_emojis = [shortcode for emoji in user_emoji_config for shortcode in emoji.shortcodes]
        is_emoji_selected = reaction in selected_emojis

        return is_emoji_selected

    elif event_type == 'reaction_removed':
        # Existing logic for reaction_added
        reactor_user_id = event.get('user')
        is_user_selected = any(member.id == reactor_user_id for member in user_team_config)
        if not is_user_selected:
            return False

        reaction = f":{event.get('reaction')}:"
        selected_emojis = [shortcode for emoji in user_emoji_config for shortcode in emoji.shortcodes]
        is_emoji_selected = reaction in selected_emojis

        return is_emoji_selected

    # Handle other event types if necessary

    return False

def save_message_for_user(user, event):
    slack_integration = user.thirdPartyIntegrations.get('slack')
    if not slack_integration:
        print(f"No Slack integration found for user {user.id}")
        return

    # Get the refreshed user token
    user_token = get_user_refresh_token(user.id)
    if not user_token:
        print(f"No valid user token found for user {user.id}")
        return

    client = WebClient(token=user_token)

    # Handle different event types
    event_type = event.get('type')

    if event_type == 'message':
        channel_id = event.get('channel')
        message_ts = event.get('ts')
    elif event_type == 'reaction_added':
        item = event.get('item', {})
        channel_id = item.get('channel')
        message_ts = item.get('ts')
    else:
        print("Unsupported event type for saving message.")
        return

    try:
        # Fetch the message
        response = client.conversations_history(
            channel=channel_id,
            latest=message_ts,
            limit=1,
            inclusive=True
        )
        messages = response.get('messages', [])

        if not messages:
            print("No messages found.")
            return

        message = messages[0]

        # Build a unique message identifier
        message_id = f"{channel_id}-{message_ts}"

        if message_id:
            # Check if the message already exists
            existing_message = SlackMessage.objects.filter(message_id=message_id, relevant_user_id=user.id).first()
            if existing_message:
                print(f"Message {message_id} already exists for user {user.id}. Skipping.")
                return
        else:
            print("Message indexing failed: No message_id available.")

        # Generate a new ObjectId for the SlackMessage
        new_object_id = ObjectId()

        # Save the message under the user's record
        slack_message = SlackMessage(
            id=new_object_id,
            message_id=message_id,
            relevant_user_id=user.id,
            source="slack_integration",
            file_name=message_id,
            original_file_extension='txt',
            video_file_extension='',
            audio_file_extension='',
            text_file_extension='txt'
        )
        slack_user_id = message.get('user')
        user_info = get_slack_user_info(slack_user_id, client)
        # Populate fields from the fetched message
        slack_message.populate_from_slack_message(message, user_info)
        slack_message.save()
        print(f"Message saved for user {user.id} with ObjectId: {new_object_id}")

    except SlackApiError as e:
        print(f"Error fetching message: {e}")

def remove_message_for_user(user, event):
    event_type = event.get('type')

    if event_type == 'reaction_removed':
        item = event.get('item', {})
        channel_id = item.get('channel')
        message_ts = item.get('ts')
    elif event_type == 'message' and event.get('subtype') == 'message_deleted':
        channel_id = event.get('channel')
        message_ts = event.get('deleted_ts')
    else:
        print(f"Unsupported event type for removing message: {event_type}")
        return

    if not channel_id or not message_ts:
        print("Invalid event data: missing channel_id or message_ts")
        return

    # Build a unique identifier for the message based on channel and timestamp
    message_id = f"{channel_id}-{message_ts}"

    # Remove the message from the database and S3
    try:
        # Find the message in the database
        message = SlackMessage.objects(relevant_user_id=user.id, message_id=message_id).first()
        
        if message:
            
            # Delete the message from the database
            message.delete()
            print(f"Message {message_id} deleted from database for user {user.id}")
            
        else:
            print(f"No message found with id {message_id} for user {user.id}")
    except Exception as e:
        print(f"Error deleting message: {e}")

def update_message_for_user(user, event):
    # Get the message identifiers
    channel_id = event.get('channel')
    message_ts = event.get('message', {}).get('ts')

    if not channel_id or not message_ts:
        print("Invalid event data: missing channel_id or message_ts")
        return

    # Build the message identifier
    message_id = f"{channel_id}-{message_ts}"

    # Fetch the latest message content from Slack
    user_token = get_user_refresh_token(user.id)
    client = WebClient(token=user_token)

    try:
        response = client.conversations_history(
            channel=channel_id,
            latest=message_ts,
            limit=1,
            inclusive=True
        )
        messages = response.get('messages', [])
        if not messages:
            print("No messages found.")
            return
        message = messages[0]

        # Update the message in the database
        slack_message = SlackMessage.objects(relevant_user_id=user.id, message_id=message_id).first()
        if not slack_message:
            print(f"Message {message_id} not found for user {user.id}")
            return
        # Update the message content
        slack_message.populate_from_slack_message(message)
        slack_message.save()
        print(f"Message {message_id} updated for user {user.id}")

    except SlackApiError as e:
        print(f"Error updating message: {e}")

def get_slack_user_info(user_id, client):
    """
    Retrieve Slack user information given a user ID.
    
    Args:
    user_id (str): The Slack user ID.
    
    Returns:
    dict: A dictionary containing user information, or None if an error occurs.
    """
    
    try:
        # Call the users.info method
        result = client.users_info(user=user_id)
        
        # Extract relevant user information
        user = result["user"]
        user_info = {
            "id": user["id"],
            "name": user["name"],
            "real_name": user["real_name"],
            "display_name": user["profile"]["display_name"],
            "email": user["profile"].get("email"),  # Use .get() in case email is not available
            "title": user["profile"].get("title"),
            "phone": user["profile"].get("phone"),
            "is_admin": user["is_admin"],
            "is_owner": user["is_owner"],
            "is_bot": user["is_bot"],
            "timezone": user["tz"]
        }
        
        return user_info

    except SlackApiError as e:
        print(f"Error fetching user info: {e}")
        return None