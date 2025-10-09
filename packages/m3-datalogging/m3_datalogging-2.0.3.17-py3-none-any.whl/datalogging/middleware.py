# coding: utf-8
import uuid
import weakref
from django.utils.deprecation import MiddlewareMixin

from m3_legacy.middleware import get_thread_data

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


class RequestTokenMiddleware(MiddlewareMixin):
    u""" Middleware создающее токен для текущего запроса.

    Токен в последующем устаналвивается во все возникающие события
    в логгере, таким образом можно просмотреть/отследить цепочку
    событий возникших во время запроса.

    """
    def process_request(self, request):
        _thread_local = get_thread_data()
        _thread_local.request_token = str(uuid.uuid4())


class CaptureRequestMiddleware(MiddlewareMixin):
    u""" Middleware сохраняющее текущий request.

    В последующем request используется для получения ряда параметров
    необходимых для логирования действий ( например ip пользователя ).

    """
    def process_request(self, request):
        _thread_local = get_thread_data()
        _thread_local.wref_request = weakref.ref(request)
