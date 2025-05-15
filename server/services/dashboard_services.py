from models.slack.slack_message import SlackMessage

def get_user_slack_messages(user_id, limit=50):
    messages = SlackMessage.objects(
        relevant_user_id=user_id
    ).order_by('-timestamp')[:limit]
    return [message.to_dict() for message in messages]
