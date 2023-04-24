from abc import abstractproperty

class BaseBotException(Exception):
    def __init__(self, **options):
        self.options = options

    @abstractproperty
    def message(self) -> str:
        return 'BaseBotException raised!'


    def __str__(self):
        return self.message.format(**self.options) if self.options else self.message


class NoOptionsPassed(BaseBotException):
    def message(self) -> str:
        return 'No options passed!'

class NoSuchOption(BaseBotException):
    def message(self) -> str:
        return 'No such option %{option}!'

class NoSuchGender(BaseBotException):
    def message(self) -> str:
        return "No such gender %{gender}!"

class NotSupportedFieldType(BaseBotException):
    def message(self) -> str:
        return 'Not supported field type %{type}'

class InvalidFieldData(BaseBotException):
    def message(self) -> str:
        return 'Invalid data for field type %{type}'

class DatabaseNoargumentsPassed(BaseBotException):
    def message(self) -> str:
        return 'No arguments passed!'
