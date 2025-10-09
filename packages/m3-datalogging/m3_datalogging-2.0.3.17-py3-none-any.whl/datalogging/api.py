# coding: utf-8
"""
.. module:: datalogging.api
.. moduleauthor:: Andrey Torsunov <torsunov@bars-open.ru>

"""
from m3_django_compatibility import get_model

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'

from django.db import models
from django.db.models import Q

from m3_legacy.middleware import get_thread_data
import six


def get_request():
    u"""Получение текущего запроса.
    """
    _thread_locals = get_thread_data()
    try:
        request = _thread_locals.wref_request()
    except AttributeError:
        request = None
    return request


def get_request_token():
    u"""Получение токена текущего запроса.
    """
    _thread_locals = get_thread_data()
    return getattr(_thread_locals, 'request_token', None)


def get_user_ip():
    u""" Получение IP текущего пользователя.

    :return str or None: Если не удалось получить IP вернет None

    """
    ip = None
    try:
        request = get_request()
        ip = request.META.get('X-Real-IP')
        ip = ip or request.META.get('HTTP_X_FORWARDED_FOR')
        ip = ip or request.META.get('REMOTE_ADDR')
        ip = ip.split(',')[-1].strip()[:15]
    finally:
        return ip


def get_events_by_token(request_token):
    u""" Получение записей лога по их общему токену """
    DataLog = get_model('datalogging', 'DataLog')
    return DataLog.objects.filter(
        request_token=request_token
    ).order_by('timestamp')


def filter_events(**kw):
    u""" Фильтрация по записям лолга.

    .. Note :: Не предусмотрена работа с NoSQL.

    Если необходимо произвести фильтрацию по данным находящимся в
    в полях ``context_data`` или ``object_snapshot``. То необходимо
    использовать префиксы ``_context`` и ``_snapshot`` соответственно.

    ::

        filter_events(
            object_type='enterprise.Enterprise',
            system_type=SystemsEnum.MAIN_APPLICATION,
            _context__diff__name='Учреждение №666',
            _context__ent='455',
        )

    """
    DataLog = get_model('datalogging', 'DataLog')
    _filter = {}
    context_filter = Q()
    snapshot_filter = Q()
    prefixes = [
        ('_context', 'context_data', context_filter),
        ('_snapshot', 'object_snapshot', snapshot_filter),
    ]

    for key, value in kw.items():
        for prefix, filter_name, prefix_filter in prefixes:
            if key.startswith(prefix):
                f = key.replace(prefix, '', 1)
                value = six.text_type(value).encode(
                    'unicode-escape').replace('\\u', '\\\\u')
                re = '{0}.*:[^:]+{1}'.format(f.replace('__', '.+'), value)
                filter_name = '{0}__iregex'.format(filter_name)
                q = Q(**{filter_name: re})
                prefix_filter.add(q, Q.AND)
                break
        else:
            _filter[key] = value

    return DataLog.objects.filter(
        context_filter & snapshot_filter, **_filter)
