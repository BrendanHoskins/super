from models.base_internal_message import BaseMessage
from mongoengine import (
    StringField,
    DictField,
    ListField,
    BooleanField,
    IntField,
    EmbeddedDocumentField,
    EmbeddedDocument,
    # ObjectIdField  # Not needed if not adding user_id field
)
# from bson import ObjectId
from datetime import datetime

class Edit(EmbeddedDocument):
    user = StringField()
    ts = StringField()

class SlackMessage(BaseMessage):
    """
    Model representing a Slack message from conversations.history.
    """
    # Remove user_id field

    # Slack-specific fields
    message_id = StringField(required=True, unique_with='relevant_user_id')  # Use relevant_user_id
    type = StringField(required=True)
    subtype = StringField()
    ts = StringField(required=True)  # Unique identifier and timestamp
    user = StringField()
    text = StringField()
    team = StringField()
    event_ts = StringField()
    channel = StringField()
    
    # Thread-related fields
    thread_ts = StringField()
    parent_user_id = StringField()
    reply_count = IntField()
    reply_users_count = IntField()
    latest_reply = StringField()
    reply_users = ListField(StringField())
    
    # Message content and formatting
    blocks = ListField(DictField())
    attachments = ListField(DictField())
    
    # Reactions
    reactions = ListField(DictField())
    
    # File sharing
    files = ListField(DictField())
    upload = BooleanField()
    
    # Message editing
    edited = EmbeddedDocumentField(Edit)
    
    # Bot messages
    bot_id = StringField()
    bot_profile = DictField()
    
    # Additional fields
    client_msg_id = StringField()
    app_id = StringField()
    team_id = StringField()
    metadata = DictField()

    meta = {
        'collection': 'slack_messages',
        'indexes': [
            {'fields': ['relevant_user_id', 'message_id'], 'unique': True},  # Update index
            'ts',
            'thread_ts',
            'user',
            'team',
            ('team', 'ts'),
        ],
        'ordering': ['-ts']
    }

    def populate_from_slack_message(self, message_data):
        self.type = message_data.get('type')
        self.subtype = message_data.get('subtype')
        self.ts = message_data.get('ts')
        self.user = message_data.get('user')
        self.text = message_data.get('text')
        self.team = message_data.get('team')
        self.event_ts = message_data.get('event_ts')
        self.channel = message_data.get('channel')

        # Thread-related fields
        self.thread_ts = message_data.get('thread_ts')
        self.parent_user_id = message_data.get('parent_user_id')
        self.reply_count = message_data.get('reply_count')
        self.reply_users_count = message_data.get('reply_users_count')
        self.latest_reply = message_data.get('latest_reply')
        self.reply_users = message_data.get('reply_users')

        # Content fields
        self.blocks = message_data.get('blocks', [])
        self.attachments = message_data.get('attachments', [])

        # Reactions
        self.reactions = message_data.get('reactions', [])

        # Files
        self.files = message_data.get('files', [])
        self.upload = message_data.get('upload')

        # Edited
        if 'edited' in message_data:
            self.edited = Edit(
                user=message_data['edited'].get('user'),
                ts=message_data['edited'].get('ts')
            )

        # Bot info
        self.bot_id = message_data.get('bot_id')
        self.bot_profile = message_data.get('bot_profile')

        # Additional fields
        self.client_msg_id = message_data.get('client_msg_id')
        self.app_id = message_data.get('app_id')
        self.team_id = message_data.get('team_id')
        self.metadata = message_data.get('metadata')

        # Update timestamps from FileMetadata (inherited)
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = datetime.utcnow()