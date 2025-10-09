# coding: utf-8

import architect
import datetime
import uuid
from itertools import chain

from django.db import models
from m3_django_compatibility import ModelOptions
from django.utils.encoding import force_str
from json_field import JSONField
from json_field.fields import JSONEncoder

from datalogging.api import get_user_ip, get_request_token, get_request
from .helpers import get_snapshot
from .enums import EventCode
from .signals import (
    msg_for_log_signal, log_context_signal, post_snapshot_signal,
    post_system_event_signal)
import six


__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


class LogJSONEncoder(JSONEncoder):
    u""" Наследник JSONEncoder, который умеет работать с ugettext. """

    def default(self, obj):
        try:
            ret = super(LogJSONEncoder, self).default(obj)
        except (UnicodeEncodeError, TypeError, ValueError):
            ret = force_str(obj)

        return ret


architect_options = dict(
    db='datalogger',
    type='range',
    subtype='date',
    constraint='month',
    column='timestamp')


@architect.install('partition', **architect_options)
class DataLog(models.Model):
    u""" Лог активности пользователей.

    Лог предусматривает отслеживание активности пользователей в системе,
    такой, как удаление/добавление/изменение записей документов, настро
    ек, прав доступа и т.д.

    `guid`:
        Уникальный ИД записи не является primary_key в случае с
        реляционными БД. Его необходимость возникает в момент выгрузки,
        когда несколько логов выгружаются в одну систему и применение
        primary_key из реляционной БД вызвало бы ряд неудобств связанных
        с коллизиями.
        Во избежание коллизий используется uuid с солью.

    `system_type`:
        В качестве подсистемы выступают сервисы(rest, soap), фоновые
        задачи, основное приложение и т.д. Т.е. это по существу среда
        возникновения события, которое следует перехватить.

    `request_token`:
        В рамках одного запроса сущетствует токен по которому можно
        отследить всю активность пользователя в течении запроса.

    """
    guid = models.CharField(
        verbose_name=u'Уникальный идентификатор записи',
        max_length=64,
        db_index=False)

    timestamp = models.DateTimeField(
        verbose_name=u'Время совершения действия',
        auto_now_add=True,
        db_index=False)

    event_type = models.CharField(
        verbose_name=u'Тип события',
        max_length=256,
        db_index=True)

    event_code = models.CharField(
        verbose_name=u'Код события',
        max_length=32,
        db_index=True)

    object_id = models.IntegerField(
        verbose_name=u'ID изменяемого объекта',
        null=True,
        db_index=True)

    object_type = models.CharField(
        verbose_name=u'Имя модели объекта',
        max_length=96,
        null=True,
        db_index=True)

    object_snapshot = JSONField(
        verbose_name=u'Снимок состояния объекта',
        null=True,
        default='{}',
        encoder=LogJSONEncoder,
        db_index=False)

    verbose = models.TextField(
        verbose_name=u'Человекопонятное описание события',
        db_index=True)

    system_type = models.CharField(
        verbose_name=u'Подсистема',
        max_length=32,
        db_index=False)

    suid = models.IntegerField(
        verbose_name=u'Идентификатор объекта в подсистеме',
        null=True,
        db_index=True)

    ip = models.CharField(
        verbose_name=u'IP адрес',
        max_length=15,
        db_index=True)

    context_data = JSONField(
        verbose_name=u'Контекстно-зависимые данные',
        null=True,
        encoder=LogJSONEncoder,
        db_index=False)

    request_token = models.CharField(
        verbose_name=u'Токен запроса',
        max_length=64,
        db_index=False)

    context_data.encoder_kwargs.update(ensure_ascii=False)
    object_snapshot.encoder_kwargs.update(ensure_ascii=False)

    class Meta:
        verbose_name = u'Журнал событий'
        db_table = u'data_logging'

    def __init__(self, *args, **kwargs):
        u""" Инициализация записи лога.

        В момент инициализации подставляются данные из контекста,
        определенного в конкретном проекте. Для того, чтобы пере
        дать контекст необходимо подписать обработчик на сигнал
        `log_context_signal`, который должен возвращать словарь
        содержащий в качестве ключей `suid`, `system_type`,
        `event_type`.

        """
        super(DataLog, self).__init__(*args, **kwargs)

        # При формировании записи лога не передаются параметры,
        # а при вытаскивании данных из базы наоборот.
        if not (args or kwargs):
            self.context_data = {}
            self.ip = get_user_ip()
            self.guid = uuid.uuid4().hex
            self.request_token = get_request_token()

            request = get_request()
            responses = log_context_signal.send(self, request=request)
            if len(responses) > 0:
                _, log_context = responses[-1]
            else:
                raise NotImplementedError(
                    "`log_context_signal` signal receiver not implemented")

            self.suid = log_context.get('suid')
            self.timestamp = datetime.datetime.now()
            self.event_type = log_context.get('event_type')
            self.system_type = log_context.get('system_type')

    @classmethod
    def _diff_field(cls, instance, attr_name, old_value, name_map):
        u""" Выявление различий значений поля между состояниями модели.

        :param instance: Экземпляр модели
        :param str attr_name: Наименование поля
        :param old_value: Значение поля из предыдущего состояния модели
        :param dict name_map: Поля модели без *_id

        :return tuple: Имя поля, (старое значение, новое значение),
            человекопонятное наименование поля

        """
        alias = attr_name
        if attr_name.endswith('_id') and attr_name[:-3] in name_map:
            alias = attr_name[:-3]
            diff, verbose_name = cls._diff_related_field(
                instance, alias, old_value
            )
        else:
            diff, verbose_name = cls._diff_normal_field(
                instance, alias, old_value
            )

        return alias, diff, verbose_name

    @staticmethod
    def _diff_normal_field(instance, alias, old_value):
        current_value = getattr(instance, alias, None)
        field = ModelOptions(instance).get_field_by_name(alias)[0]
        diff = (old_value or u'(не указано)', current_value)
        return diff, field.verbose_name or alias

    @staticmethod
    def _diff_related_field(instance, alias, old_object_id):
        field = ModelOptions(instance).get_field_by_name(alias)[0]
        model = field.rel.to if hasattr(field, 'rel') else field.remote_field.model        
        obj = getattr(instance, alias, None)
        new_val, old_val = six.text_type(obj), u'(не указано)'

        if old_object_id:
            try:
                old_val = model.objects.get(id=old_object_id)
            except model.DoesNotExist:
                old_val = u'(не найден)'
            else:
                old_val = six.text_type(old_val)

        return (old_val, new_val), field.verbose_name or alias

    @classmethod
    def get_verbose_msg(cls, log_record, model_instance, **kwargs):
        u""" Получение человекопонятного описания события.

        Т.к. для каждого проекта формирование описания будет разным
        метод работает через сигнал `msg_for_log_signal`.

        """
        fields_dict = model_instance and model_instance.__dict__.copy() or {}
        responses = msg_for_log_signal.send(
            cls,
            log_record=log_record,
            model_instance=model_instance,
            fields_dict=fields_dict,
            **kwargs)

        if len(responses) > 0:
            _, response = responses[0]
        else:
            raise NotImplementedError(
                "`msg_for_log_signal` signal receiver not implemented")

        return response

    @classmethod
    def make_snapshot(cls, instance, event_code):
        u""" Формирование записи лога о состоянии модели.

        Перед сохранением записи лога вызывается сигнал `post_snapshot`,
        где в качестве аргумента передается не сохраненная запись лога,
        что в свою очередь позволяет воздействовать на запись.

        :param instance: Экземпляр модели
        :param event_code: Событие происшедшее с моделью

        """
        log_rec = cls()
        log_rec.object_id = instance.id
        log_rec.object_type = '{0}.{1}'.format(
            instance._meta.app_label,
            instance.__class__.__name__
        )

        log_rec.event_code = event_code

        if event_code != EventCode.DELETE:
            result_diff = {}
            verbose_names = {}
            cur_snapshot = get_snapshot(instance)
            name_map = list(set(chain.from_iterable(
                (field.name, field.attname) if hasattr(field, 'attname') else (
                field.name,)
                for field in instance._meta.get_fields()
                # For complete backwards compatibility, you may want to exclude
                # GenericForeignKey from the results.
                if not (field.many_to_one and field.related_model is None)
            )))

            # Различие в состояниях экземпляра модели
            state_diff = getattr(instance, '_snapshot', set())
            state_diff -= cur_snapshot

            for attr_name, old_value in state_diff:
                alias, field_diff, verbose = cls._diff_field(
                    instance, attr_name, old_value, name_map
                )
                result_diff[alias] = field_diff
                verbose_names[alias] = verbose

            log_rec.context_data['diff'] = result_diff
            log_rec.context_data['field_names'] = verbose_names

        snapshot = {}

        for key, val in instance.__dict__.items():
            if key.startswith('_'):
                continue

            if val is None:
                snapshot[key] = val
            else:
                str_val = force_str(val)
                if str_val.isdigit():
                    snapshot[key] = val
                else:
                    snapshot[key] = str_val

        log_rec.object_snapshot = snapshot
        log_rec.verbose = cls.get_verbose_msg(log_rec, instance)

        # Если хотя бы один обработчик вернет False, то это будет
        # означать, что запись с логом не нужно сохранять.
        signal_results = post_snapshot_signal.send(cls, log_record=log_rec)
        if False not in signal_results:
            log_rec.save()

    @classmethod
    def make_system_event(cls, event_code, context_data=None, **kwargs):
        u""" Формирование записи о событии происшедшем в системе.

        Все спецефичные данные о событии обрабатываются через сигнал
        `post_system_event` ровно так же, как в методе `make_snapshot`.

        :param event_code: Событие в системе.
        :param dict context_data: Доп. данные описывающие событие.

        """
        context_data = context_data or {}
        log_rec = cls()
        log_rec.context_data.update(context_data)
        log_rec.event_code = event_code
        log_rec.verbose = cls.get_verbose_msg(log_rec, None, **kwargs)

        # Если хотя бы один обработчик вернет False, то это будет
        # означать, что запись с логом не нужно сохранять.
        signal_results = post_system_event_signal.send(
            cls, log_record=log_rec, **kwargs)
        if False not in signal_results:
            log_rec.save()

    def __hash__(self):
        return hash(self.guid)