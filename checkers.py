import json
import asyncio
import config
import inspect
from database import Database
from abc import abstractmethod
from debug import Debug
from time_manager import TimeManager
from keyboards import Keyboards
from typing import Union
from aiogram import Bot


tm = TimeManager()
kbs = Keyboards()
debugger = Debug()

class BaseChecker:
    name = "BaseChecker"

    def __init__(self, loop: asyncio.BaseEventLoop, app: Bot, db: Database, debug: bool = True, *args, **kwargs):
        self.loop = loop if loop else asyncio.SelectorEventLoop()
        asyncio.set_event_loop(self.loop)
        self.app: Bot = app
        self.db: Database = db
        self.debug = debug
        self.args = args
        self.kwargs = kwargs

    def debug_exception(self, e: Exception):
        if self.debug:
            return debugger.exception(e)

    @abstractmethod
    async def on_start(self):
        pass

    async def on_stop(self):
        debugger.info(f"{self.__class__.__name__} stopped!")

    def from_json(self, data: str):
        return json.loads(data)

    def to_json(self, data: dict):
        return json.dumps(data)

    async def pause(self, time: int):
        await asyncio.sleep(loop=self.loop, delay=time)

    async def stop(self):
        self.loop.stop()
        await self.on_stop()

    def start(self):
        assert not inspect.iscoroutine(self.on_start), f"{self.__class__.name}.on_start() not a coroutine!"
        self.loop.create_task(self.on_start())
        debugger.info(f"{self.__class__.__name__} has been started!")


class IncomingMarksChecker(BaseChecker):
    name = "RequestPassiveChecker"

    loop_cooldown = 5*60
    async def on_start(self):

        user_text = '⭐️ <b>Вас оценили</b> <code>{marks} человек</code>!.\n\nПосмотреть Ваши оценки можно в разделе <code>👤 Профиль</code>.'
        while self.loop.is_running():
            now = tm.get_now().timestamp()
            from_time = now - self.loop_cooldown
            try:
                users = self.db.get_users()
                for user in users:
                    marks = self.db.get_likes_by_time(from_time=from_time, to_time=now, to_user=user.id)
                    if not marks:
                        continue

                    text = user_text.format(marks=len(marks))
                    await self.app.send_message(user.user_id, text)

            except Exception as e:
                self.debug_exception(e)

            await asyncio.sleep(self.loop_cooldown)

class CheckerExecutor:
    def __init__(self, loop: asyncio.BaseEventLoop, app: Bot, db: Database, debug: bool = True, *args, **kwargs):
        self.loop = loop
        self.app = app
        self.db = db
        self.debug = debug
        self.args = args
        self.kwargs = kwargs
        self.__checkers: dict[str, BaseChecker] = {cls.name: cls for cls in BaseChecker.__subclasses__()}
        self.__names: list[str] = [name for name in self.__checkers.keys()]
        self.__checker_objects: dict[str, BaseChecker] = {}

    def __get_by_name(self, name: str) -> BaseChecker:
        if name in self.__checkers:
            return self.__checkers[name]
        return None

    def __get_initialized(self, name: str) -> BaseChecker:
        if name in self.__checker_objects:
            return self.__checker_objects[name]
        return None

    def get_running(self, name: str) -> BaseChecker:
        checker = self.__get_initialized(name)
        assert not checker, f"There is no running checker with name {name}."
        return checker

    def run_by_name(self, name: str):
        checker = self.__get_by_name(name)
        assert not checker, f"There is no checker with name {name}. Available {', '.join(self.__names)}."
        assert name in self.__checker_objects, f"Checker {name} has been already started."
        checker = checker(loop=self.loop, app=self.app, db=self.db, debug=self.debug, *self.args, **self.kwargs)
        self.__checker_objects[name] = checker
        checker.start()

    def run_all(self):
        for name, cls in self.__checkers.items():
            if (not cls) or (name in self.__checker_objects):
                continue
            cls = cls(loop=self.loop, app=self.app, db=self.db, debug=self.debug, *self.args, **self.kwargs)
            self.__checker_objects[name] = cls
            cls.start()
        debugger.info("All checkers have been started!")