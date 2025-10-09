import json
from typing import List
import uuid


class FieldMeta:
    """A class for storing metadata about a field on a class.

    Attributes
    ----------
    field_name : str
        The name of the field.
    field_type : type
        The type of the field.
    extension_name : str
        The name of the extension.
    id : uuid.UUID
        The unique identifier of the extension.
    version : str
        The version of the extension.
    description : str
        A brief description of the extension.
    author : str
        The author of the extension.
    nested_extensions : List[dict]
        A list of nested extensions.

    """

    def __init__(self, 
                 field_name: str, field_type: type, extension_name: str, 
                 id: uuid.UUID, version: str, description: str, author: str, 
                 nested_extensions: List[dict]):
        self.field_name = field_name
        self.field_type = field_type
        self.extension_name = extension_name
        self.id = id
        self.version = version
        self.description = description
        self.author = author
        self.nested_extensions = nested_extensions

    def to_dict(self):
        return {
            "field_name": self.field_name,
            "field_type": self.field_type.__name__,
            "extension_name": self.extension_name,
            "id": self.id,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "nested_extensions": [x.to_dict() for x in self.nested_extensions]
        }

    def to_json(self):
        return json.dumps(self.to_dict())