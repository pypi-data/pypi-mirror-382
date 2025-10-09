# coding: utf-8
import warnings
from copy import copy

from django.conf import settings
from django.db.models.signals import class_prepared
from django.dispatch import Signal

from .managers import DataLoggingManager, MANAGER_NAME


suspects = set(getattr(settings, 'DATALOGGER_SUSPECTS_MODEL', []))

if not suspects:
    msg = 'Список моделей DATALOGGER_SUSPECTS_MODEL пуст'
    warnings.warn(msg.encode('utf-8'))
    
elif len(suspects) != len(settings.DATALOGGER_SUSPECTS_MODEL):
    # Проверка на дубликаты, в случае их наличия выкидывается warning
    duplicates = list(copy(settings.DATALOGGER_SUSPECTS_MODEL))
    for model_name in suspects:
        duplicates.remove(model_name)
    msg = (u'Дублированное вхождение в DATALOGGER_SUSPECTS_MODEL '
           u'модели(ей):{0}').format(duplicates)
    warnings.warn(msg.encode('utf-8'))


# Сигналы определяющие поведение методов логгера
# =====================================================================

post_snapshot_signal = Signal(providing_args=['log_record'])
post_system_event_signal = Signal(providing_args=['log_record'])
log_context_signal = Signal(providing_args=['request'])
msg_for_log_signal = Signal(
    providing_args=['log_record', 'model_instance', 'fields_dict'])


def add_datalogger_manager(sender, **kw):
    u""" Обработчик сигнала class_prepared.

    Если модель указана в списке ``DATALOGGER_SUSPECTS_MODEL``, то
    обработчик добавляет в класс модели ``DataLoggingManager``.

    """
    cls = sender
    full_path = '{0}.{1}'.format(cls.__module__, cls.__name__)
    short_path = '{0}.{1}'.format(cls._meta.app_label, cls.__name__)
    if suspects.intersection((short_path, full_path)):
        cls.add_to_class(MANAGER_NAME, DataLoggingManager())

if not getattr(settings, 'DATALOGGER_SHUTUP', False):
    class_prepared.connect(add_datalogger_manager, weak=False)
