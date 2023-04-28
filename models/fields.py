import json
import models.exceptions
from models.repr import ReprModel
from typing import Optional, Union, Iterable
from abc import abstractproperty

class BaseTextField(ReprModel):
    TYPES = {'int': int, 'str': str, 'float': float}
    field_type: str = ''

    def __init__(self, options: Iterable[Union[int, str, float]] = None):
        self.possible_options = options if options else []

        if self.field_type not in self.TYPES:
            raise models.exceptions.NotSupportedFieldType(type=self.field_type)

    @property
    def data(self) -> dict:
        return {'field_type': self.field_type}

    def get_transformed(self, data: str):
        if self.is_valid(data):
            new_data = self.TYPES[self.field_type](data)
            return new_data

        raise models.exceptions.InvalidFieldData(type=self.field_type)

    def is_valid(self, data: str):
        try:
            data = self.TYPES[self.field_type](data)
            if self.possible_options and data not in self.possible_options:
                raise
            return True
        except:
            return False

class BaseMediaField(ReprModel):
    TYPES = ['photo', 'video', 'voice', 'audio']
    field_type: str = ''

    def __init__(self, text_field: Optional[BaseTextField] = None):
        self.text_field: BaseTextField = text_field
        if self.field_type not in self.TYPES:
            raise models.exceptions.NotSupportedFieldType(type=self.field_type)

    @property
    def data(self) -> dict:
        return {'field_type': self.field_type}

    def get_transformed(self, data: str):
        if self.text_field:
            return self.text_field.get_transformed(data)

        return data

    def is_valid(self, data: str):
        if self.text_field:
            return self.text_field.is_valid(data)

        return True

class CallbackQueryField(ReprModel):
    required_arguments: dict[str, type] = {'action': str}

    def __init__(self, returns_key: str, **options: type):
        self.options: dict[str, type] = options
        self.returns_key: str = returns_key
        self.required_arguments.update(self.options)


    def is_valid(self, query_data: dict[str, Union[int, str]]) -> bool:
        for key, val in self.required_arguments.items():
            if key not in query_data:
                return False

            if type(query_data[key]) is not val:
                return False

        return True

    def output(self, query_data: dict[str, Union[int, str]]) -> Optional[Union[str, int]]:
        if self.is_valid(query_data):
            return query_data[self.returns_key]
        return None


class PhotoField(BaseMediaField):
    field_type: str = 'photo'

class VoiceField(BaseMediaField):
    field_type: str = 'voice'

class AudioField(BaseMediaField):
    field_type: str = 'audio'

class VideoField(BaseMediaField):
    field_type: str = 'video'

class IntegerField(BaseTextField):
    field_type: str = 'int'

class FloatField(BaseTextField):
    field_type: str = 'float'

class StringField(BaseTextField):
    field_type: str = 'str'



