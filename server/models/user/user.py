from mongoengine import (
    Document, StringField, EmailField, DateTimeField, ObjectIdField, 
    DictField, BooleanField, MapField, EmbeddedDocumentField, ListField
)
from bson import ObjectId
from models.user.base_third_party_integration import ThirdPartyIntegration

class User(Document):
    id = ObjectIdField(required=True, primary_key=True, default=ObjectId)
    username = StringField(required=True)
    password = StringField(required=True)
    thirdPartyIntegrations = MapField(field=EmbeddedDocumentField(ThirdPartyIntegration))
    resetToken = StringField(required=False)
    resetTokenExpiration = DateTimeField(required=False)