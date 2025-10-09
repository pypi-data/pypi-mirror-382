# coding: utf-8
from django.conf import settings

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


class DataLoggerRouter(object):
    u""" Роутер не позволяет создавать связи с моделью лога.
    """

    def db_for_read(self, model, **hints):
        u""" Выбор БД для чтения. В данном методе происходит проверка
        на заданное имя модели и в случаем если модель принадлежит
        данному модулю, для нее используются отдельные настройки
        """
        model_name = getattr(model, '__name__', model.__class__.__name__)
        if model_name == 'DataLog':
            return settings.DATALOGGER_DATABASE
        return None

    def db_for_write(self, model, **hints):
        u""" Выбор БД для записи. Применяются те же правила, что и при
        чтения из базы.
        """
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        u""" Метод контролируюий факт создания связи между обектами. Отсекаются
        связи создаваемые с моделяи данного модуля.
        """
        if 'DataLog' in [obj1.__class__.__name__, obj2.__class__.__name__]:
            return False
        return None

    def allow_syncdb(self, db, model):
        u""" Метод регулирующий возможность инициализации моделей.
        """
        model_name = getattr(model, '__name__', model.__class__.__name__)
        if db == settings.DATALOGGER_DATABASE and model_name == 'DataLog':
            return True
        return None


class NotUseDataLoggerDBRouter(object):
    u""" Роутер запрещает создание таблиц в базе для логгера.
    """

    def allow_syncdb(self, db, model):
        u""" Запрет создания таблиц в базе логгера
        """
        if db == settings.DATALOGGER_DATABASE:
            if model._meta.app_label == 'south':
                return True
            return False
