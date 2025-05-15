from models.user.user import User
from datetime import datetime

from mongoengine import (
    BooleanField,
    DateTimeField,
    DictField,
    Document,
    ListField,
    ObjectIdField,
    StringField,
)

class FileMetadata(Document):
    meta = {'allow_inheritance': True}
    
    file_name = StringField(required=True)
    relevant_user_id = ObjectIdField(required=True, reference_field=User)
    source = StringField(required=True, choices=["computer_upload", "steam_integration", "slack_integration"]) # This represents whether the file was uploaded from the user's computer or from an integration. E.g. if a user has a csv file they exported from steam then uploaded to xprod, that would be a "computer_upload". However, if they linked xprod with a third party tool like steam then pulled the file in directly through the integration, that would be a "steam_integration".
    local_metadata = DictField(required=False)
    document_type = StringField(choices=[
        "Customer Discovery Interview",
        "Review",
        "Business Objectives or Strategy Document",
        "Market Research Report",
        "Internal Meeting",
        "Internal Message"
    ])
    original_file_extension = StringField(required=True)
    video_file_extension = StringField(required=True)
    audio_file_extension = StringField(required=True)
    text_file_extension = StringField(required=True)
    individual_insights_extraction_is_complete_for_each_insight_type = DictField(
        default=dict
    )  # possible keys are "kg_nodes", "individual_pain_point", "individual_feature_request", "individual_quantitative_statement"
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())
    
    uploaded_at = DateTimeField()  # obsolete
    relevant_user_id = ObjectIdField(reference_field=User)  # obsolete
    individual_insights_extraction_is_complete = BooleanField(
        required=False
    )  # obsolete
    segments = ListField(StringField(), default=list)  # obsolete
    

    def to_dict(self):
        return {
            "id": str(self.id),
            "file_name": self.file_name,
            "source": self.source,
            "local_metadata": self.local_metadata,
            "relevant_user_id": str(self.relevant_user_id),
            "document_type": self.document_type,
            "original_file_extension": self.original_file_extension,
            "video_file_extension": self.video_file_extension,
            "audio_file_extension": self.audio_file_extension,
            "text_file_extension": self.text_file_extension,
            "individual_insights_extraction_is_complete_for_each_insight_type": self.individual_insights_extraction_is_complete_for_each_insight_type,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
