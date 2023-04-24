from models.repr import ReprModel
from typing import Callable
from abc import abstractmethod

class DatabaseAdapter(ReprModel):
    def __init__(self, db: Callable):
        self.__db: Callable = db

    @abstractmethod
    def get_user(self, *args, **kwargs):
        return self.__db.get_user(*args, **kwargs)

    @abstractmethod
    def get_like(self, *args, **kwargs):
        return self.__db.get_like(*args, **kwargs)

    @abstractmethod
    def get_likes(self, *args, **kwargs):
        return self.__db.get_likes(*args, **kwargs)

    @abstractmethod
    def get_users(self, *args, **kwargs):
        return self.__db.get_likes(*args, **kwargs)

    @abstractmethod
    def get_gender(self, *args, **kwargs):
        return self.__db.get_gender(*args, **kwargs)

    @abstractmethod
    def get_city(self, *args, **kwargs):
        return self.__db.get_city(*args, **kwargs)

    @abstractmethod
    def get_cities(self, *args, **kwargs):
        return self.__db.get_cities(*args, **kwargs)


