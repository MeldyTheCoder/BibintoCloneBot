import datetime
from time_manager import TimeManager
from models.base import BaseModel
from models.user import UserModel
from models.database import DatabaseAdapter

tm = TimeManager()

class LikeModel(BaseModel):
    __id: int = 0
    __mark: int = 0
    __to_user: int = 0
    __from_user: int = 0
    __date: int = 0

    @property
    def id(self) -> int:
        return self.__id

    @property
    def mark(self) -> int:
        return self.__mark

    @property
    def to_user(self) -> UserModel:
        data = self._database_adapter.get_user(id=self.__to_user)
        if isinstance(data, UserModel):
            return data
        return UserModel(self._database_adapter, **data)

    @property
    def from_user(self) -> UserModel:
        data = self._database_adapter.get_user(id=self.__from_user)
        if isinstance(data, UserModel):
            return data
        return UserModel(self._database_adapter, **data)

    @property
    def date(self) -> datetime.datetime:
        if self.__date:
            return tm.from_timestamp(self.__date)
        self.__date = tm.get_now().timestamp()
        return tm.get_now()




