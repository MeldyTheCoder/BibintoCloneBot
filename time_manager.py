import calendar
from datetime import datetime, timezone, timedelta
from typing import Union



class TimeManager:
    def __init__(self):
        self.timezone = timezone(timedelta(hours=3), name='МСК')
        self.months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        self.months_cased = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
        self.strftime_format = "%d.%m.%Y %H:%M"
        self.date_format = '%d.%m.%Y'
        self.debugger_format = "%d_%m_%Y"
        self.convert_format = ['%(hours) часов', '%(minutes) минут', '%(seconds) секунд']
        self.max_timestamp = datetime.max.replace(tzinfo=self.timezone).timestamp()

    # текущее время
    def get_now(self, *timedeltas: timedelta):
        now = datetime.now(tz=self.timezone)
        if timedeltas:
            for timedelta in timedeltas:
                now += timedelta
        return now

    # конвертер из метки времени
    def from_timestamp(self, time: Union[int, float]):
        return datetime.fromtimestamp(time, tz=self.timezone)

    # точная дата начала дня
    def day_start_time(self, time: Union[int, float, datetime] = None, timestamp: bool = False):
        if not time:
            date = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            date = self.from_timestamp(time)
        else:
            date = time
        start_date = self.minus_delta(date,
                                      timedelta(microseconds=date.microsecond),
                                      timedelta(minutes=date.minute),
                                      timedelta(hours=date.hour),
                                      timedelta(seconds=date.second))
        if timestamp:
            return start_date.timestamp()
        return start_date

    # проверка времени на указанный промежуток
    def time_in_range(self, target: Union[int, datetime, float], time_tuple: Union[list[datetime, float, int], tuple[datetime, float, int]]):
        if isinstance(target, int) or isinstance(target, float):
            target = self.from_timestamp(target)
        if (isinstance(time_tuple[0], int) or isinstance(time_tuple[0], float)) or ((isinstance(time_tuple[1], int) or isinstance(time_tuple[1], float))):
            time_tuple = (self.from_timestamp(time_tuple[0]), self.from_timestamp(time_tuple[1]))
        return bool(target >= time_tuple[0] and target <= time_tuple[1])

    # точная дата начала недели
    def week_start_time(self, time: Union[int, float, datetime] = None, timestamp: bool = False):
        if not time:
            date = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            date = self.from_timestamp(time)
        else:
            date = time
        start_date = self.day_start_time(date) - timedelta(days=date.isoweekday()-1)
        if timestamp:
            return start_date.timestamp()
        return start_date

    # промежуток недели
    def week_range(self, time: Union[int, float, datetime] = None, timestamp: bool = False):
        if not time:
            date = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            date = self.from_timestamp(time)
        else:
            date = time
        start = self.week_start_time(time, False)
        if timestamp:
            return start.timestamp(), (start + timedelta(days=7)).timestamp()
        return start, (start + timedelta(days=7))

    # промежуток дня
    def day_range(self, time: Union[int, float, datetime] = None, timestamp: bool = False):
        if not time:
            date = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            date = self.from_timestamp(time)
        else:
            date = time
        start = self.day_start_time(date, False)
        if timestamp:
            return start.timestamp(), (start + timedelta(days=1)).timestamp()
        return start, (start + timedelta(days=1))

    # точная дата начала месяца
    def month_start_time(self, time: Union[int, float, datetime] = None, timestamp: bool = False):
        if not time:
            date = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            date = self.from_timestamp(time)
        else:
            date = time
        start_date = self.day_start_time(date) - timedelta(days=date.day-1)
        if timestamp:
            return start_date.timestamp()
        return start_date

    # вычитание времени
    def minus_delta(self, time: Union[int, datetime, float] = None, *deltas: Union[timedelta, int], timestamp: bool = False):
        if not time:
            time = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            time = self.from_timestamp(time)
        for delta in deltas:
            if isinstance(delta, timedelta):
                time -= delta
            else:
                time -= timedelta(seconds=delta)
        if timestamp:
            return time.timestamp()
        return time

    # сложение времени
    def plus_delta(self, time: Union[int, datetime, float] = None, *deltas: Union[timedelta, int],
                    timestamp: bool = False):
        if not time:
            time = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            time = self.from_timestamp(time)
        for delta in deltas:
            if isinstance(delta, timedelta):
                time += delta
            else:
                time += timedelta(seconds=delta)
        if timestamp:
            return time.timestamp()
        return time

    # промежуток месяца
    def month_range_time(self, time: Union[int, datetime, float] = None, timestamp: bool = False):
        if not time:
            date = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            date = self.from_timestamp(time)
        else:
            date = time
        start_date = self.month_start_time(date, False)
        days_month = calendar.monthrange(date.year, date.month)[1]
        return self.range_time(days_month*24*60*60, start_date.timestamp(), timestamp)

    # вывод предыдущего месяца из списка
    def get_previous_month(self, time: Union[datetime, int, float] = 0, months_past: int = 1):
        if not time:
            time = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            time = self.from_timestamp(time)
        month = time.month
        return month-1-months_past, self.months[month-1-months_past]

    # промежуток предыдущего месяца
    def get_previous_month_range(self, time: Union[datetime, int, float] = 0, months_past: int = 1, timestamp: bool = False):
        if not time:
            time = self.get_now()
        elif isinstance(time, int) or isinstance(time, float):
            time = self.from_timestamp(time)
        for i in range(months_past):
            time -= timedelta(days=calendar.monthrange(time.year, self.get_previous_month(time)[0])[1])
        return self.month_range_time(time, timestamp=timestamp)

    # счет пройденного времени от одной даты к другой
    def time_past(self, date1: Union[int, datetime, float], date2: Union[int, datetime, float], seconds: bool = True):
        if isinstance(date1, int) or isinstance(date1, float):
            date1 = self.from_timestamp(date1)
        if isinstance(date2, int) or isinstance(date2, float):
            date2 = self.from_timestamp(date2)
        if seconds:
            return abs((date1 - date2).total_seconds())
        return timedelta(seconds=((date1 - date2).total_seconds()))

    # промежуток времени (основа для других промежутков)
    def range_time(self, delta: Union[int, float, timedelta], from_time: Union[int, float, datetime] = None, timestamp: bool = False):
        if not from_time:
            from_time = self.get_now()
        elif isinstance(from_time, int) or isinstance(from_time, float):
            from_time = self.from_timestamp(from_time)
        if isinstance(delta, float) or isinstance(delta, int):
            end_time = from_time + timedelta(seconds=delta)
        else:
            end_time = from_time + delta

        if timestamp:
            return (from_time.timestamp(), end_time.timestamp())
        return (from_time, end_time)

    def strptime(self, format: str, date_string: str):
        return datetime.strptime(date_string, format)

    def get_month_title(self, month: int, in_case: bool = False):
        if in_case:
            return self.months_cased[month]
        return self.months[month]

    def strftime(self, timestamp: int, format: str = ''):
        if timestamp > self.max_timestamp:
            return '??'
        if not format:
            format = self.date_format
        date = self.from_timestamp(timestamp)
        return date.strftime(format)
