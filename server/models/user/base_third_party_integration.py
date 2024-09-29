from mongoengine import EmbeddedDocument, BooleanField, StringField

class ThirdPartyIntegration(EmbeddedDocument):
    """
    Base class for all third-party integrations.
    """
    meta = {'allow_inheritance': True}
    
    enabled = BooleanField(default=False)

    def to_dict(self):
        """
        Convert the ThirdPartyIntegration instance to a dictionary.
        This method can be overridden by subclasses to add more fields.
        """
        return {
            'enabled': self.enabled
        }