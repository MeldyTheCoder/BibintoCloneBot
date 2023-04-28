import datetime
import sqlite3
import config
from typing import Union, Optional
import models.exceptions
from time_manager import TimeManager
from models.database import DatabaseAdapter
from models.like import LikeModel
from models.user import UserModel
from models.gender import GenderModel
from models.city import CityModel

tm = TimeManager()

class Database:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=True)
        self.cursor = self.db.cursor()
        self.adapter = DatabaseAdapter(self)
        self.cursor.row_factory = self.__dict_factory

    def __dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    def get_users(self, **options: Union[int, str]) -> list[UserModel]:
        query = 'SELECT * FROM users'
        args = []
        args_str = []
        if options:
            for key, val in options.items():
                args.append(val)
                args_str.append(f"{key} = ?")
            query += ' WHERE ' + ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return [UserModel(self.adapter, **data) for data in self.cursor.fetchall()]

    def get_user(self, **options: Union[int, str]) -> UserModel:
        query = 'SELECT * FROM users WHERE '
        args = []
        args_str = []
        if not options:
            raise models.exceptions.NoOptionsPassed()

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")
        query += ' AND '.join(args_str)

        self.cursor.execute(query, args)
        data = self.cursor.fetchone()
        if data:
            return UserModel(self.adapter, **data)
        return {}

    def add_user(self, **options) -> int:
        query = 'INSERT INTO users ({}) VALUES ({})'
        args_str = []
        args = []
        if not options:
            raise models.exceptions.NoOptionsPassed()

        if 'city' in options:
            options['city'] = self.get_city(city=options['city']).id

        options['register_date'] = tm.get_now().timestamp()

        for key, val in options.items():
            args_str.append(f"{key}")
            args.append(val)

        query = query.format(', '.join(args_str), ', '.join("?"*len(args_str)))
        self.cursor.execute(query, args)
        self.db.commit()
        return self.cursor.lastrowid

    def update_user(self, id: int, **options) -> None:
        query = "UPDATE users SET {} WHERE id = ?"
        args = []
        args_str = []
        if not options:
            raise models.exceptions.NoOptionsPassed()

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")

        args.append(id)
        query = query.format(", ".join(args_str))
        self.cursor.execute(query, args)
        self.db.commit()

    def next_user(self, from_user: int, current_user: int = 0, **options) -> Optional[UserModel]:
        options['status'] = 'active'
        users = self.get_users(**options)
        user_marks = [mark.to_user.id for mark in self.get_likes(from_user=from_user)]
        user_ids = [user.id for user in users if user.id != from_user and not user.id in user_marks]

        if not user_ids or not users:
            return None

        if (not current_user) or (current_user not in user_ids) or (current_user == user_ids[-1]):
            return self.get_user(id=user_ids[0])

        user = user_ids.index(current_user) + 1
        return self.get_user(id=user)

    def get_likes(self, **options: Union[int, str]) -> list[LikeModel]:
        query = 'SELECT * FROM likes'
        args = []
        args_str = []
        if options:
            for key, val in options.items():
                args.append(val)
                args_str.append(f"{key} = ?")
            query += ' WHERE ' + ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return [LikeModel(self.adapter, **data) for data in self.cursor.fetchall() if data]

    def get_like(self, **options: Union[int, str]) -> LikeModel:
        query = 'SELECT * FROM likes WHERE '
        args = []
        args_str = []
        if not options:
            raise models.exceptions.NoOptionsPassed()

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")
        query += ' AND '.join(args_str)

        self.cursor.execute(query, args)
        data = self.cursor.fetchone()
        if data:
            return LikeModel(self.adapter, **data)
        return {}

    def add_like(self, **options) -> int:
        query = 'INSERT INTO likes ({}) VALUES ({})'
        args_str = ['date']
        args = [tm.get_now().timestamp()]
        if not options:
            raise models.exceptions.NoOptionsPassed()

        for key, val in options.items():
            args_str.append(f"{key}")
            args.append(val)

        query = query.format(', '.join(args_str), ', '.join("?"*len(args_str)))
        self.cursor.execute(query, args)
        self.db.commit()
        return self.cursor.lastrowid

    def get_likes_by_time(self, from_time: Union[datetime.datetime, int], to_time: Union[datetime.datetime, int], **options) -> list[LikeModel]:
        likes = self.get_likes(**options)
        if isinstance(from_time, datetime.datetime):
            from_time = from_time.timestamp()

        if isinstance(to_time, datetime.datetime):
            to_time = to_time.timestamp()

        return list(filter(lambda like: from_time < like.date.timestamp() < to_time, likes))

    def update_like(self, id: int, **options) -> None:
        query = "UPDATE likes SET {} WHERE id = ?"
        args = []
        args_str = []
        if not options:
            raise models.exceptions.NoOptionsPassed()

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")

        args.append(id)
        query = query.format(", ".join(args_str))
        self.cursor.execute(query, args)
        self.db.commit()

    def get_gender(self, **options):
        query = 'SELECT * FROM genders WHERE '
        args = []
        args_str = []
        if not options:
            raise models.exceptions.NoOptionsPassed()

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")
        query += ' AND '.join(args_str)

        self.cursor.execute(query, args)
        data = self.cursor.fetchone()
        if data:
            return GenderModel(self.adapter, **data)
        return {}

    def get_city(self, **options):
        query = 'SELECT * FROM cities WHERE '
        args = []
        args_str = []
        if not options:
            raise models.exceptions.NoOptionsPassed()

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")
        query += ' AND '.join(args_str)

        self.cursor.execute(query, args)
        data = self.cursor.fetchone()
        if data:
            return CityModel(self.adapter, **data)
        return {}

    def get_cities(self, **options):
        query = 'SELECT * FROM cities'
        args = []
        args_str = []
        if options:
            for key, val in options.items():
                args.append(val)
                args_str.append(f"{key} = ?")
            query += ' WHERE ' + ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return [CityModel(self.adapter, **data) for data in self.cursor.fetchall() if data]

    def get_genders(self, **options):
        query = 'SELECT * FROM genders'
        args = []
        args_str = []
        if options:
            for key, val in options.items():
                args.append(val)
                args_str.append(f"{key} = ?")
            query += ' WHERE ' + ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return [GenderModel(self.adapter, **data) for data in self.cursor.fetchall() if data]

    def search_city(self, search_query: str):
        query = 'SELECT * FROM cities WHERE city LIKE ? OR country LIKE ?'
        args = [f"%{search_query}%", f"%{search_query}%"]
        self.cursor.execute(query, args)
        return [CityModel(self.adapter, **city) for city in self.cursor.fetchall()]

    def search_gender(self, search_query: str):
        query = 'SELECT * FROM genders WHERE code LIKE ? OR title LIKE ?'
        args = [f"%{search_query}%", f"%{search_query}%"]
        self.cursor.execute(query, args)
        return [GenderModel(self.adapter, **gender) for gender in self.cursor.fetchall()]
