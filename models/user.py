from time_manager import TimeManager
from models.base import BaseModel
from models.age import AgeModel
from models.name import NameModel
from models.gender import GenderModel
from models.city import CityModel
tm = TimeManager()

class UserModel(BaseModel):
    __age: int = 0
    __city: int = 0
    __name: str = ""
    __gender: int = 0
    __photo: str = ""
    __user_id: int = 0
    __status: str = ""
    __register_date: int = 0
    __id: int = 0

    @property
    def age(self) -> AgeModel:
        return AgeModel(self._database_adapter, age=self.__age)

    @property
    def city(self) -> CityModel:
        data = self._database_adapter.get_city(id=self.__city)
        if isinstance(data, CityModel):
            return data
        return CityModel(self._database_adapter, **data)

    @property
    def name(self) -> NameModel:
        return NameModel(self._database_adapter, full_name=self.__name)

    @property
    def gender(self) -> GenderModel:
        data = self._database_adapter.get_gender(id=self.__gender)
        if isinstance(data, GenderModel):
            return data
        return GenderModel(self._database_adapter, **data)

    @property
    def photo(self) -> str:
        return self.__photo

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def status(self) -> str:
        return self.__status

    @property
    def register_date(self) -> int:
        return tm.from_timestamp(self.__register_date)

    @property
    def id(self) -> int:
        return self.__id