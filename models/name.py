from models.base import BaseModel

class NameModel(BaseModel):
    __full_name: str = ''

    @property
    def first_name(self):
        if ' ' in self.__full_name:
            return self.__full_name.split(' ')[0]
        return self.__full_name

    @property
    def last_name(self):
        if ' ' in self.__full_name:
            return self.__full_name.split(' ')[1]
        return self.__full_name

    @property
    def full_name(self):
        return self.__full_name

