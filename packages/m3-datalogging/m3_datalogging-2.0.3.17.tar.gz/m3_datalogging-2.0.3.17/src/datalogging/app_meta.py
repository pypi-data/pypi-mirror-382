# coding: utf-8
from django.conf import settings

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'

from django.contrib.auth.models import AnonymousUser

from m3.actions import ActionPack, ActionController

from .helpers import remember_user, memorize_user
from .models import DataLog
from .enums import EventCode

EXCLUDED_ACTIONS = getattr(settings, 'DATALOGGER_EXCLUDE_ACTIONS', ())
DATALOGGER_OFF = getattr(settings, 'DATALOGGER_SHUTUP', False)
FORGET_SYS_EVENTS = getattr(settings, 'DATALOGGER_FORGET_SYS_EVENTS', False)
HOOKED_ACTIONS = getattr(settings, 'DATALOGGER_HOOKED_ACTIONS', {})

orig_invoke = ActionController._invoke


class InvaderLogPack(ActionPack):
    u""" Инжектируемый пак
    """

    def pre_run(self, request, context):
        u""" Перед выполнением экшена у инжектируемого пака
        необходимо запоминить пользователя
        """
        memorize_user(request.user)

    def post_run(self, request, context, response):
        u""" Некоторые косвенные методы определения поведения пользователя.
        Если в ответе на запрос упоминается заголовок, то считается, что
        вернули окно.
        Если запомненный ранее пользователь был аутентифицирован, а после
        формирования ответа - нет, то считается, что произошел выход из
        системы. И наоборот.
        """
        user = remember_user()
        if hasattr(response, 'data') and hasattr(response.data, 'title'):
            win = response.data
            DataLog.make_system_event(EventCode.WIN_OPEN, {
                'title': win.title
            })
        elif isinstance(request.user, AnonymousUser) and user != request.user:
            DataLog.make_system_event(EventCode.LOGOUT)
        elif isinstance(user, AnonymousUser) and user != request.user:
            DataLog.make_system_event(EventCode.LOGIN)


# Подмена оригинального метода, на метод который осуществляет инъекцию
# в InvaderLogPack в stack.

_invader = InvaderLogPack()


def is_loggable(obj):
    u"""Данная функция использоуется для опредения нуждается ли данный объект
    в логировании. Проводится проверка объекта на вхождение имени его класса,
    либо имени класса его предка в список-исключение `EXCLUDED_ACTIONS`. Если
    переданный экземпляр найден в списке, то объект счтается подходящим для
    создания записи.

    :param obj: Экземпляр Action'a.
    :type obj: Action
    :returns:  bool -- результат проверки.

    """
    return not (obj.__class__.__name__ in EXCLUDED_ACTIONS or
                obj.parent.__class__.__name__ in EXCLUDED_ACTIONS)


def invader_invoke(self, request, action, stack, *args, **kwargs):
    u"""
    :param request: Экземпляр Action'a.
    :type request: request
    :param action: Экземпляр Action'a.
    :type action: Action
    :param stack: Экземпляр Action'a.
    :type stack: list
    """
    if is_loggable(action) and _invader not in stack:
        stack.append(_invader)

    if action.__class__.__name__ in HOOKED_ACTIONS:
        event_key = HOOKED_ACTIONS[action.__class__.__name__]
        event_code = getattr(EventCode, event_key)
        DataLog.make_system_event(event_code, {}, action=action,
            request=request)

    return orig_invoke(self, request, action, stack, *args, **kwargs)

# Проверка на частичное или полное отключение логирования
if not (DATALOGGER_OFF or FORGET_SYS_EVENTS):
    ActionController._invoke = invader_invoke
