from models.base import BaseModel


class CityModel(BaseModel):
    __id: int = 0
    __city: str = ''
    __country: str = ''

    @property
    def id(self):
        return self.__id

    @property
    def city(self):
        return self.__city

    @property
    def country(self):
        return self.__city
