from models.base import BaseModel
from time_manager import TimeManager
from datetime import timedelta, datetime

tm = TimeManager()

class AgeModel(BaseModel):
    __age: int = 0

    @property
    def date_of_birth(self) -> datetime:
        return tm.get_now(-timedelta(days=365 * self.__age))

    @property
    def years(self):
        return self.__age
