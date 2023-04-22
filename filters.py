import json
from aiogram import types
from database import Database

class Filters:
    def __init__(self, db: Database):
        self.db = db

    def query(self, query_string: str):
        return lambda query: json.loads(query.data)['action'] == query_string

    def userRegisteredMessage(self):
        return lambda message: self.db.get_user(user_id=message.chat.id)

    def userNotRegisteredMessage(self):
        return lambda message: not self.db.get_user(user_id=message.chat.id)

    def userRegisteredQuery(self):
        return lambda query: self.db.get_user(user_id=query.message.chat.id)

    def userNotRegisteredQuery(self):
        return lambda query: not self.db.get_user(user_id=query.message.chat.id)

    def isPrivateMessage(self):
        return lambda message: message.chat.type == 'private'

    def isPrivateQuery(self):
        return lambda query: query.message.chat.type == 'private'

    def isPublicMessage(self):
        return lambda message: message.chat.type != "private"



