import sqlite3
from typing import Union, Optional

class Database:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=True)
        self.cursor = self.db.cursor()


    def get_users(self, **options: Union[int, str]):
        query = 'SELECT * FROM users'
        args = []
        args_str = []
        if options:
            for key, val in options.items():
                args.append(val)
                args_str.append(f"{key} = ?")
            query += ' WHERE ' + ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return self.cursor.fetchall()

    def get_user(self, **options: Union[int, str]):
        query = 'SELECT * FROM users WHERE '
        args = []
        args_str = []
        if not options:
            raise Exception("No arguments passed")

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")
        query += ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return self.cursor.fetchone()

    def add_user(self, **options):
        query = 'INSERT INTO users ({}) VALUES ({})'
        args_str = []
        args = []
        if not options:
            raise Exception("No arguments passed")

        for key, val in options.items():
            args_str.append(f"{key}")
            args.append(val)

        query = query.format(', '.join(args_str), ', '.join("?"*len(args_str)))
        self.cursor.execute(query, args)
        self.db.commit()
        return self.cursor.lastrowid

    def update_user(self, id: int, **options):
        query = "UPDATE users SET {} WHERE id = ?"
        args = []
        args_str = []
        if not options:
            raise Exception("No arguments passed")

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")

        args.append(id)
        query = query.format(", ".join(args_str))
        self.cursor.execute(query, args)
        self.db.commit()

    def next_user(self, current_user: int = 0, **options):
        options['status'] = 'active'
        users = self.get_users(**options)
        if not current_user:
            return users[0]

        user_ids = [user.id for user in users]
        if current_user not in user_ids:
            return users[0]

        if current_user == user_ids[-1]:
            return users[0]

        user = user_ids.index(current_user) + 1
        return self.get_user(id=user)

    def get_likes(self, **options: Union[int, str]):
        query = 'SELECT * FROM likes'
        args = []
        args_str = []
        if options:
            for key, val in options.items():
                args.append(val)
                args_str.append(f"{key} = ?")
            query += ' WHERE ' + ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return self.cursor.fetchall()

    def get_like(self, **options: Union[int, str]):
        query = 'SELECT * FROM likes WHERE '
        args = []
        args_str = []
        if not options:
            raise Exception("No arguments passed")

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")
        query += ' AND '.join(args_str)

        self.cursor.execute(query, args)
        return self.cursor.fetchone()

    def add_like(self, **options):
        query = 'INSERT INTO likes ({}) VALUES ({})'
        args_str = []
        args = []
        if not options:
            raise Exception("No arguments passed")

        for key, val in options.items():
            args_str.append(f"{key}")
            args.append(val)

        query = query.format(', '.join(args_str), ', '.join("?"*len(args_str)))
        self.cursor.execute(query, args)
        self.db.commit()
        return self.cursor.lastrowid

    def update_like(self, id: int, **options):
        query = "UPDATE likes SET {} WHERE id = ?"
        args = []
        args_str = []
        if not options:
            raise Exception("No arguments passed")

        for key, val in options.items():
            args.append(val)
            args_str.append(f"{key} = ?")

        args.append(id)
        query = query.format(", ".join(args_str))
        self.cursor.execute(query, args)
        self.db.commit()