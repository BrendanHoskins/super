from mongoengine import (
    StringField,
    BooleanField,
    EmbeddedDocument,
    DateTimeField,
    EmbeddedDocumentField, 
    ListField,
    IntField,
    DictField
)
from models.user.base_third_party_integration import ThirdPartyIntegration


class SlackInstallation(EmbeddedDocument):
    app_id = StringField()
    enterprise_id = StringField()
    enterprise_name = StringField()
    enterprise_url = StringField()
    team_id = StringField()
    team_name = StringField()
    bot_token = StringField()
    bot_id = StringField()
    bot_user_id = StringField()
    bot_scopes = StringField()
    user_id = StringField()
    user_token = StringField()
    user_scopes = ListField()
    incoming_webhook_url = StringField()
    incoming_webhook_channel = StringField()
    incoming_webhook_channel_id = StringField()
    incoming_webhook_configuration_url = StringField()
    is_enterprise_install = BooleanField()
    token_type = StringField()
    bot_refresh_token = StringField()
    bot_token_expires_at = DateTimeField()
    user_refresh_token = StringField()
    user_token_expires_at = DateTimeField()
    user_token_type = StringField()

    def to_dict(self):
        return {
            'app_id': self.app_id,
            'enterprise_id': self.enterprise_id,
            'enterprise_name': self.enterprise_name,
            'enterprise_url': self.enterprise_url,
            'team_id': self.team_id,
            'team_name': self.team_name,
            'bot_id': self.bot_id,
            'bot_user_id': self.bot_user_id,
            'bot_scopes': self.bot_scopes,
            'user_id': self.user_id,
            'user_scopes': self.user_scopes,
            'incoming_webhook_url': self.incoming_webhook_url,
            'incoming_webhook_channel': self.incoming_webhook_channel,
            'incoming_webhook_channel_id': self.incoming_webhook_channel_id,
            'incoming_webhook_configuration_url': self.incoming_webhook_configuration_url,
            'is_enterprise_install': self.is_enterprise_install,
            'token_type': self.token_type,
            'bot_token_expires_at': self.bot_token_expires_at.isoformat() if self.bot_token_expires_at else None,
            'user_token_expires_at': self.user_token_expires_at.isoformat() if self.user_token_expires_at else None,
            'user_token_type': self.user_token_type,
            'user_refresh_token': self.user_refresh_token
        }

class SlackOauth(EmbeddedDocument):
    state = StringField()
    expires_at = DateTimeField()

    def to_dict(self):
        return {
            'state': self.state,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class SlackEmojiConfiguration(EmbeddedDocument):
    id = StringField()
    keywords = ListField(StringField())
    name = StringField()
    native = StringField()
    shortcodes = ListField(StringField())
    src = StringField()
    unified = StringField()
    aliases = ListField(StringField())
    skin = IntField()

    def to_dict(self):
        return {
            'id': self.id,
            'keywords': self.keywords,
            'name': self.name,
            'native': self.native,
            'shortcodes': self.shortcodes,
            'src': self.src,
            'unified': self.unified,
            'aliases': self.aliases,
            'skin': self.skin
        }

class SlackTeamConfiguration(EmbeddedDocument):
    id = StringField()
    team_id = StringField()
    name = StringField()
    deleted = BooleanField()
    color = StringField()
    real_name = StringField()
    tz = StringField()
    tz_label = StringField()
    tz_offset = IntField()
    profile = DictField()
    is_admin = BooleanField()
    is_owner = BooleanField()
    is_primary_owner = BooleanField()
    is_restricted = BooleanField()
    is_ultra_restricted = BooleanField()
    is_bot = BooleanField()
    updated = IntField()
    is_app_user = BooleanField()
    has_2fa = BooleanField()

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'name': self.name,
            'deleted': self.deleted,
            'color': self.color,
            'real_name': self.real_name,
            'tz': self.tz,
            'tz_label': self.tz_label,
            'tz_offset': self.tz_offset,
            'profile': self.profile,
            'is_admin': self.is_admin,
            'is_owner': self.is_owner,
            'is_primary_owner': self.is_primary_owner,
            'is_restricted': self.is_restricted,
            'is_ultra_restricted': self.is_ultra_restricted,
            'is_bot': self.is_bot,
            'updated': self.updated,
            'is_app_user': self.is_app_user,
            'has_2fa': self.has_2fa
        }

class SlackIntegration(ThirdPartyIntegration):
    """
    Model representing a Slack integration.
    """
    oauth = EmbeddedDocumentField(SlackOauth)
    installation = EmbeddedDocumentField(SlackInstallation)
    user_team_configuration = ListField(EmbeddedDocumentField(SlackTeamConfiguration))
    user_emoji_configuration = ListField(EmbeddedDocumentField(SlackEmojiConfiguration))
    
    def to_dict(self):
        return {
            'enabled': self.enabled,
            'oauth': self.oauth.to_dict() if self.oauth else None,
            'installation': self.installation.to_dict() if self.installation else None,
            'user_team_configuration': [
                config.to_dict() for config in self.user_team_configuration
            ] if self.user_team_configuration else [],
            'user_emoji_configuration': [
                config.to_dict() for config in self.user_emoji_configuration
            ] if self.user_emoji_configuration else []
        }
