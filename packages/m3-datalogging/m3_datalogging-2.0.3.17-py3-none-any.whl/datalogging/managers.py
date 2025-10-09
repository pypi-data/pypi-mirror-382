# coding: utf-8
import uuid
from django.db import models
from django.db.models.signals import class_prepared
from m3_django_compatibility import get_model

from .helpers import get_snapshot

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


MANAGER_NAME = '_datalogger_manager'


class DataLoggingManager(object):

    #: Серия UID для обработчиков сигналов, устанавливается в качестве
    #: значения для ``dispatch_uid``. Дополнительную информацию о
    #: ``dispatch_uid`` см. ``django.db.models.signals.Signal.connect``.
    POST_INIT_UID = uuid.uuid4().hex
    POST_SAVE_UID = uuid.uuid4().hex
    POST_DELETE_UID = uuid.uuid4().hex

    def contribute_to_class(self, cls, name):
        u""" Привязка к модели.

        Если `name` является DATALOGGER_MANAGER_NAME, то привязка
        к модели добавлена через settings.py и сигнал class_prepared
        уже возник, соответственно вешать на него `finalize`
        бессмысленно.

        """
        if name != 'DataLog':
            if name == MANAGER_NAME:
                self.finalize(cls)
            else:
                class_prepared.connect(self.finalize)
            setattr(cls, name, True)

    def finalize(self, sender, **kw):
        u""" Подключение к модели. """
        models.signals.post_init.connect(
            self.post_init, sender=sender, weak=False,
            dispatch_uid=self.POST_INIT_UID)
        models.signals.post_save.connect(
            self.post_save, sender=sender, weak=False,
            dispatch_uid=self.POST_SAVE_UID)
        models.signals.post_delete.connect(
            self.post_delete, sender=sender, weak=False,
            dispatch_uid=self.POST_DELETE_UID)

    def post_init(self, instance, **kw):
        u""" Сохранение начального состояния модели. """
        state = get_snapshot(instance)
        instance._snapshot = state

    def post_save(self, instance, created, **kw):
        u""" Сохранение состояния модели в лог при сохранении. """
        from .enums import EventCode

        DataLog = get_model('datalogging', 'DataLog')
        changed = get_snapshot(instance)
        if changed != instance._snapshot:
            event_code = created and EventCode.INSERT or EventCode.UPDATE
            DataLog.make_snapshot(instance, event_code)
            instance._snapshot = get_snapshot(instance)

    def post_delete(self, instance, **kw):
        u""" Сохранение состояния модели в лог перед удалением. """
        from .enums import EventCode

        DataLog = get_model('datalogging', 'DataLog')
        DataLog.make_snapshot(instance, EventCode.DELETE)
