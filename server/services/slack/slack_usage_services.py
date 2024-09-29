from models.user.user import User
from models.user.slack_integration import SlackIntegration, SlackEmojiConfiguration, SlackTeamConfiguration
from models.slack.slack_message import SlackMessage
import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .slack_oauth_services import get_bot_refresh_token, get_user_refresh_token
import requests
import base64
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
import threading
import re
from services.s3.s3_services import upload_file_to_s3, delete_file_from_s3
import io
from bson import ObjectId

FILES_TO_EXTRACT_INSIGHTS_FROM_S3_BUCKET_NAME = os.getenv("FILES_TO_EXTRACT_INSIGHTS_FROM_S3_BUCKET_NAME")
S3_USER_ACCESS_KEY = os.getenv("S3_USER_ACCESS_KEY")
S3_USER_SECRET_ACCESS_KEY = os.getenv("S3_USER_SECRET_ACCESS_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_FOLDER_WITH_TXT_VERSIONS_OF_EVERY_USER_UPLOADED_FILE = os.getenv("S3_FOLDER_WITH_TXT_VERSIONS_OF_EVERY_USER_UPLOADED_FILE")

def get_slack_emojis(user_id):
    QUESTION_MARK_BASE64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKAAAACgCAYAAACLz2ctAAAACXBIWXMAAAsTAAALEwEAmpwYAAAFIGlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDAgNzkuMTYwNDUxLCAyMDE3LzA1LzA2LTAxOjA4OjIxICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoTWFjaW50b3NoKSIgeG1wOkNyZWF0ZURhdGU9IjIwMTYtMDktMjlUMTA6NTM6MDQtMDc6MDAiIHhtcDpNb2RpZnlEYXRlPSIyMDE4LTA3LTI2VDE0OjQ0OjU2LTA3OjAwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDE4LTA3LTI2VDE0OjQ0OjU2LTA3OjAwIiBkYzpmb3JtYXQ9ImltYWdlL3BuZyIgcGhvdG9zaG9wOkNvbG9yTW9kZT0iMyIgcGhvdG9zaG9wOklDQ1Byb2ZpbGU9InNSR0IgSUVDNjE5NjYtMi4xIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjI4ZjA3OWU2LTc4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'
    slack_token = get_user_refresh_token(user_id)
    client = WebClient(token=slack_token)

    try:
        response = client.emoji_list(include_categories=True)
        # Convert the SlackResponse to a dictionary
        response_dict = response.data

        # Get the set of emoji names from response_dict['categories']
        emoji_names_in_categories = set()
        for category in response_dict['categories']:
            emoji_names_in_categories.update(category['emoji_names'])

        # Fetch CDN data (assuming CDN_URL is known)
        CDN_URL = 'https://cdn.jsdelivr.net/npm/@emoji-mart/data'  # Replace with actual CDN URL
        cdn_response = requests.get(CDN_URL)
        cdn_data = cdn_response.json()

        # Filter cdn_data to remove emojis not in emoji_names_in_categories
        # Filter emojis
        filtered_emojis = {}
        for emoji_id, emoji_data in cdn_data['emojis'].items():
            if emoji_id in emoji_names_in_categories:
                filtered_emojis[emoji_id] = emoji_data

        # Filter categories
        filtered_categories = []
        for category in cdn_data['categories']:
            filtered_emoji_ids = [emoji_id for emoji_id in category['emojis'] if emoji_id in emoji_names_in_categories]
            if filtered_emoji_ids:
                filtered_categories.append({
                    'id': category['id'],
                    'emojis': filtered_emoji_ids
                })

        # Prepare slack_default_emojis
        slack_default_emojis = {
            'categories': filtered_categories,
            'emojis': filtered_emojis
        }

        # Now process custom emojis
        custom_emojis = []
        for emoji_key, emoji_value in response_dict['emoji'].items():
            if emoji_value.startswith('alias:'):
                alias_name = emoji_value[6:]  # Get the alias name

                # Check if alias_name exists in cdn_data['emojis']
                if alias_name in cdn_data['emojis']:
                    # Copy relevant data from CDN
                    emoji_data = cdn_data['emojis'][alias_name]
                    custom_emojis.append({
                        'id': emoji_key,
                        'name': emoji_data['name'],
                        'keywords': emoji_data.get('keywords', []),
                        'skins': emoji_data.get('skins', [])
                    })
                else:
                    # Alias not found in CDN data, use question mark emoji
                    custom_emojis.append({
                        'id': emoji_key,
                        'name': alias_name,
                        'keywords': [],
                        'skins': [{'src': f'{QUESTION_MARK_BASE64}'}]
                    })
            elif emoji_value.startswith('http://') or emoji_value.startswith('https://'):
                # Value is a URL to custom emoji image
                # Download the image using requests with authentication
                headers = {'Authorization': f'Bearer {slack_token}'}
                image_response = requests.get(emoji_value, headers=headers)
                if image_response.status_code == 200:
                    image_content = image_response.content

                    # Encode image to base64
                    encoded_image = base64.b64encode(image_content).decode('utf-8')
                    mime_type = image_response.headers.get('Content-Type', 'image/png')
                    image_src = f'data:{mime_type};base64,{encoded_image}'

                    # Add to custom emojis
                    custom_emojis.append({
                        'id': emoji_key,
                        'name': emoji_key,
                        'keywords': ['slack', emoji_key],
                        'skins': [{'src': image_src}]
                    })
                else:
                    print(f"Failed to download emoji image {emoji_key}: {image_response.status_code}")
                    # Handle error, perhaps use default image
                    custom_emojis.append({
                        'id': emoji_key,
                        'name': emoji_key,
                        'keywords': ['slack', emoji_key],
                        'skins': [{'src': f'{QUESTION_MARK_BASE64}'}]
                    })
            else:
                # Unknown format, use question mark emoji
                print(f"Unknown format for emoji {emoji_key}: {emoji_value}")
                custom_emojis.append({
                    'id': emoji_key,
                    'name': emoji_key,
                    'keywords': ['slack', emoji_key],
                    'skins': [{'src': f'{QUESTION_MARK_BASE64}'}]
                })

        # Wrap custom emojis in the desired format
        slack_custom_emojis = [{
            "id": "slack",
            "name": "Slack",
            "emojis": custom_emojis
        }]

        # Write slack_default_emojis to a file
        with open('slack_default_emojis.txt', 'w') as f:
            json.dump(slack_default_emojis, f, indent=2)

        # Write slack_custom_emojis to a file
        with open('slack_custom_emojis.txt', 'w') as f:
            json.dump(slack_custom_emojis, f, indent=2)
        # Return the results
        return {
            'slack_default_emojis': slack_default_emojis,
            'slack_custom_emojis': slack_custom_emojis
        }

    except SlackApiError as e:
        print(f"Error fetching custom emojis: {e}")
        response_dict = {"error": str(e)}
        return response_dict

def get_slack_users(user_id):
    # Get the refreshed user token
    user_token = get_user_refresh_token(user_id)
    if not user_token:
        print(f"Unable to get a valid user token for user {user_id}")
        return None

    # Initialize the Slack client with the refreshed user token
    client = WebClient(token=user_token)

    try:
        # Fetch all users with pagination
        all_users = []
        cursor = None
        while True:
            users_response = client.users_list(limit=200, cursor=cursor)
            all_users.extend(users_response['members'])
            cursor = users_response.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break

        # Fetch all user groups
        usergroups_response = client.usergroups_list(include_users=True)
        user_groups = usergroups_response['usergroups']

        # Create a dictionary to store users by group
        users_by_group = {}

        # Map user IDs to user objects for quick lookup
        user_dict = {user['id']: user for user in all_users}

        # Assign users to their groups
        for group in user_groups:
            group_name = group['name']

            # Fetch user IDs for this group
            group_users_response = client.usergroups_users_list(usergroup=group['id'])
            group_user_ids = group_users_response['users']

            # Get full user objects for the group members
            group_users = [user_dict[user_id] for user_id in group_user_ids if user_id in user_dict]

            users_by_group[group_name] = group_users

        # Add users who are not in any group to a special "No Group" category
        users_in_groups = set(user_id for group_users in users_by_group.values() for user_id in [user['id'] for user in group_users])
        users_not_in_groups = [user for user_id, user in user_dict.items() if user_id not in users_in_groups]

        if users_not_in_groups:
            users_by_group['No Group'] = users_not_in_groups
        # Write users_by_group to a text file with indentation
        output_file = f"slack_users_by_group_{user_id}.txt"
        with open(output_file, 'w') as f:
            f.write(json.dumps(users_by_group, indent=2))
        
        print(f"Users by group information written to {output_file}")
        return users_by_group

    except SlackApiError as e:
        print(f"Error fetching Slack users: {e}")
        return None

def submit_slack_configuration(user_id, emojis, members):
    user = User.objects(id=user_id).first()
    if not user:
        print(f"User with id {user_id} not found")
        return False

    # Retrieve the SlackIntegration from thirdPartyIntegrations
    slack_integration = user.thirdPartyIntegrations.get('slack')
    if not slack_integration:
        print(f"No Slack integration found for user {user_id}")
        return False

    print(emojis)
    # Update emoji configuration
    if emojis:
        slack_integration.user_emoji_configuration = []
        for emoji in emojis:
            # Wrap each shortcode in colons
            shortcodes = [f":{code}:" for code in emoji.get('shortcodes', [])]
            print(shortcodes)
            emoji_config = SlackEmojiConfiguration(
                id=emoji.get('id'),
                keywords=emoji.get('keywords'),
                name=emoji.get('name'),
                native=emoji.get('native'),
                shortcodes=shortcodes,  # Use the modified shortcodes
                src=emoji.get('src'),
                unified=emoji.get('unified'),
                aliases=emoji.get('aliases'),
                skin=emoji.get('skin')
            )
            slack_integration.user_emoji_configuration.append(emoji_config)
    print(members)
    # Update team configuration
    if members:
        slack_integration.user_team_configuration = []
        for member in members:
            team_config = SlackTeamConfiguration(
                id=member.get('id'),
                team_id=member.get('team_id'),
                name=member.get('name'),
                deleted=member.get('deleted'),
                color=member.get('color'),
                real_name=member.get('real_name'),
                tz=member.get('tz'),
                tz_label=member.get('tz_label'),
                tz_offset=member.get('tz_offset'),
                profile=member.get('profile'),
                is_admin=member.get('is_admin'),
                is_owner=member.get('is_owner'),
                is_primary_owner=member.get('is_primary_owner'),
                is_restricted=member.get('is_restricted'),
                is_ultra_restricted=member.get('is_ultra_restricted'),
                is_bot=member.get('is_bot'),
                updated=member.get('updated'),
                is_app_user=member.get('is_app_user'),
                has_2fa=member.get('has_2fa')
            )
            slack_integration.user_team_configuration.append(team_config)

    try:
        # Save the updated SlackIntegration back into thirdPartyIntegrations
        user.thirdPartyIntegrations['slack'] = slack_integration
        user.save()
        return True
    except Exception as e:
        print(f"Error saving Slack configuration: {e}")
        return False
    
def get_slack_configuration(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return {}

    slack_integration = user.thirdPartyIntegrations.get('slack')
    if not slack_integration or not isinstance(slack_integration, SlackIntegration) or not slack_integration.enabled:
        return {}

    configuration = {
        'slack_team_configuration': [
            config.to_dict() for config in slack_integration.user_team_configuration
        ] if slack_integration.user_team_configuration else [],
        'slack_emoji_configuration': [
            config.to_dict() for config in slack_integration.user_emoji_configuration
        ] if slack_integration.user_emoji_configuration else []
    }
    print(configuration)
    return configuration

def get_slack_data_and_configuration(user_id):
    slack_emojis = get_slack_emojis(user_id)

    slack_users = get_slack_users(user_id)

    slack_configuration = get_slack_configuration(user_id)

    return {
        'slack_emojis': slack_emojis,
        'slack_users': slack_users,
        'slack_configuration': slack_configuration
    }