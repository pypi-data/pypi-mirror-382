# coding: utf-8
u"""Вспомогательные средства для работы с датами."""
from __future__ import absolute_import

import datetime

from dateutil import rrule


# явно задаются имена дней, чтобы не возиться с настройками локали в питоне
MON_IDX = 0
TUE_IDX = 1
WED_IDX = 2
THU_IDX = 3
FRI_IDX = 4
SAT_IDX = 5
SUN_IDX = 6

WEEKDAYS = (
    (MON_IDX, u'Понедельник'),
    (TUE_IDX, u'Вторник'),
    (WED_IDX, u'Среда'),
    (THU_IDX, u'Четверг'),
    (FRI_IDX, u'Пятница'),
    (SAT_IDX, u'Суббота'),
    (SUN_IDX, u'Воскресенье')
)
WEEKDAYS_DICT = dict(WEEKDAYS)


def date_range_to_str(date_from, date_to, can_be_one_day_long=False):
    u"""
    Возвращает строку формата "с дд.мм.гггг [по дд.мм.гггг]",
    или дд.мм.гггг, если даты совпадают.

    Если указана только одна из дат то будет только
    "с ..." или "по ...", но если can_be_one_day_long=True,
    результат будет "дд.мм.гггг", для той даты, что указана.

    (None, None)                         -> "∞ — ∞"
    (<2001.01.01>, <2001.01.01>)         -> "01.01.2001"
    (<2001.01.01>, <2002.02.02>)         -> "с 01.01.2001 по 02.02.2002"
    (<2001.01.01>, None        )         -> "с 01.01.2001"
    (None,         <2002.02.02>)         -> "по 02.02.2002"
    (<2001.01.01>, None,       , True)   -> "01.01.2001"
    (None,         <2002.02.02>, True)   -> "02.02.2002"
    """
    def fmt(date):
        return date.strftime('%d.%m.%Y') if date else ''

    def validate_year(date):
        return (date if 1900 < date.year < 2100 else None) if date else None

    result = ''
    date_from = validate_year(date_from)
    date_to = validate_year(date_to)
    if date_from and date_to:
        assert date_from <= date_to
        if date_from == date_to:
            result = fmt(date_from)
        else:
            result = u'с %s по %s' % (fmt(date_from), fmt(date_to))
    elif not date_from and not date_to:
        result = '∞ — ∞'
    else:
        if can_be_one_day_long:
            result = fmt(date_from or date_to or None)
        elif date_from:
            result = u'с %s' % fmt(date_from)
        elif date_to:
            result = u'по %s' % fmt(date_to)
    return result


def iter_days_between(date_from, date_to, odd_weeks_only=False):
    u"""
    Генератор дат в промежутке между указанными (включая границы).

    :param datetime.date: date_from - дата с
    :param datetime.date: date_to - дата по
    :param boolean: odd_weeks_only - только четные недели отн-но начала года

    :rtype: generator
    """
    if date_from > date_to:
        raise ValueError('date_from must be lower or equal date_to!')

    for dt in rrule.rrule(
        rrule.DAILY, dtstart=date_from, until=date_to
    ):
        if odd_weeks_only and dt.isocalendar()[1] % 2 != 0:
            # если требуются четные недели относительно начала года
            continue
        yield dt.date()


def get_week_start(date=None):
    u"""Возвращает дату первого дня недели (понедельника).

    :param date: Дата, определяющая неделю. Значение по умолчанию - текущая
        дата.
    :type date: datetime.date or None

    :rtype: datetime.date
    """
    if date is None:
        date = datetime.date.today()

    result = date - datetime.timedelta(days=date.weekday())

    return result


def get_week_end(date=None):
    u"""Возвращает дату последнего дня недели (воскресенья).

    :param date: Дата, определяющая неделю. Значение по умолчанию - текущая
        дата.
    :type date: datetime.date or None

    :rtype: datetime.date
    """
    if date is None:
        date = datetime.date.today()

    result = date + datetime.timedelta(days=SUN_IDX - date.weekday())

    return result


def get_week_dates(date=None):
    u"""Возвращает даты дней недели.

    :param date: Дата, определяющая неделю. Значение по умолчанию - текущая
        дата.
    :type date: datetime.date

    :rtype: dateutli.rrule.rrule
    """
    if date is None:
        date = datetime.date.today()

    monday = get_week_start(date)

    return (
        day.date()
        for day in rrule.rrule(rrule.DAILY, dtstart=monday,
                               count=len(WEEKDAYS))
    )


def get_weekdays_for_date(date=None, weekday_names=None):
    u"""Возвращает названия и даты дней недели.

    :param date: Дата, определяющая неделю. Значение по умолчанию - текущая
        дата.
    :type date: datetime.date or None

    :param weekday_names: Список или словарь наименований дней недели.
    :type weekday_names: dict, list

    :return: Кортеж из кортежей вида (u'Название дня недели', дата).
    :rtype: tuple
    """
    weekday_names = weekday_names or WEEKDAYS_DICT

    return tuple(
        (weekday_names[day.weekday()], day)
        for day in get_week_dates(date)
    )
