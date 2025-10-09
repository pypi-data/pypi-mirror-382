# coding: utf-8

import re

from django.conf import settings
from m3.db import BaseEnumerate
import six

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


class ConfigurableEnum(type):
    u""" Метакласс автозагрузки типов перечислений.

    Автозагрузка типов осуществляется из settings.py проекта,
    причем данные должны являться словарем с кортежами в качестве
    значений. Наименование параметра должно начинаться с приставки
    "DATALOGGER". Пример:

    ::

        DATALOGGER_EVENT_TYPE = {
            'SYSTEM': ('se', u'Системное событие'),

        }

    После инициализации класса, можно вызывать как обычный аттрибут.
    И в целом класс используется как обычное перечисление. Пример:

    ::

        print EventType.SYSTEM // 'se'

    """
    def __new__(cls, name, bases, dct):
        dct['values'] = dct.get('values') or {}
        parts = re.findall(r'[A-Z][a-z]+', name)
        settings_name = u'_'.join(parts).upper()
        settings_name = u'DATALOGGER_{0}'.format(settings_name)
        constants = getattr(settings, settings_name, {})
        assert isinstance(constants, dict)
        for const_name, value in constants.items():
            assert const_name.isupper()
            assert isinstance(value, tuple) and len(value) == 2
            dct[const_name] = value[0]
            dct['values'].update([value])
        return type.__new__(cls, name, bases, dct)


@six.add_metaclass(ConfigurableEnum)
class EventType(BaseEnumerate):
    u""" Перечисление типов событий.

    Пример возможных типов:
    - (se, Системное событие)
    - (lse, Юридически важное событие)

    """


@six.add_metaclass(ConfigurableEnum)
class EventCode(BaseEnumerate):
    u""" Перечисление кодов событий.

    Пример возможных кодов:
    - (insert, Добавление)
    - (delete, Удаление)

    """

    LOGIN = 'login'
    INSERT = 'insert'
    DELETE = 'delete'
    UPDATE = 'update'
    LOGOUT = 'logout'
    WIN_OPEN = 'win_open'

    values = {
        INSERT: u'Добавление',
        DELETE: u'Удаление',
        UPDATE: u'Изменение',
        LOGIN: u'Пользователь вошел в систему',
        LOGOUT: u'Пользователь вышел из системы',
        WIN_OPEN: u'Пользователь открыл окно'
    }


@six.add_metaclass(ConfigurableEnum)
class SystemsEnum(BaseEnumerate):
    u""" Перечисление сред логирования.

    Пример возможных значений:
    - ('scheduled_task', u'Задача по расписанию')
    - ('ws', u'Web-сервис')

    """
