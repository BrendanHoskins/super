from models.file_metadata import FileMetadata

class BaseMessage(FileMetadata):
    """
    Base class for internal messages, inheriting from FileMetadata.
    This class serves as an intermediary between FileMetadata and specific message types like SlackMessage.
    """
    
    meta = {
        'allow_inheritance': True
    }