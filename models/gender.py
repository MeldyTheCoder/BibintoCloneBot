import models.exceptions
from models.base import BaseModel
from models.database import DatabaseAdapter
from typing import Union

class GenderModel(BaseModel):
    __id: int = 0
    __title: str = ''
    __code: str = ''

    @property
    def code(self) -> int:
        return self.__code

    @property
    def title(self) -> str:
        return self.__title

    @property
    def id(self) -> int:
        return self.__id

    @property
    def is_male(self) -> bool:
        return self.__code == 'male'

    @property
    def is_female(self) -> bool:
        return self.__code == 'female'

