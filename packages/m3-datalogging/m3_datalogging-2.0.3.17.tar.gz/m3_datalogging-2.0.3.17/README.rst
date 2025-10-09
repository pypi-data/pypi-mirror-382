.. data-logging documentation master file, created by
   sphinx-quickstart on Tue Jan 14 09:31:41 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Data Logging
===============

:Version: 1.2.2

**Data Logging** - логгер действий пользователя в системе. Отслеживаются 
такие события, как вход, выход пользователя, открытие окон, удаление, 
редактирование, создание записей в БД.

.. Note :: 
    Не реализована поддержка NoSQL решений.

.. Attention ::
    Массовые операции (Model.objects.delete() и т.д.) над моделями не отслеживаются.


Зависимости
===========

M3 1.5

Django 1.3

Django JSON Field 

South

Architect


Настройки
=========

В ``settings.DATABASE_ROUTERS`` необходимо добавить ``datalogging.dbrouters.DataLoggerRouter``.
Если используется отдельная БД так же необходимо добавить ``datalogging.dbrouters.NotUseDataLoggerDBRouter``.

В ``settings.MIDDLEWARE_CLASSES`` необходимо добавить  ``datalogging.middleware.CaptureRequestMiddleware`` и
``datalogging.middleware.RequestTokenMiddleware``.


``DATALOGGER_EVENT_TYPE``
    Разделение событий по типу (системные, юридически важные и т.д.).
    В дальнейшем, к перечислению можно обратиться через ``EventType``.

    Пример:

    ::

        DATALOGGER_EVENT_TYPE = {
            'SYSTEM': ('se', u'Системное событие'),
        }


``DATALOGGER_EVENT_CODE``
    Коды событий, изначально имеются 6 событий: insert, update, delete, login,
    logout, win_open.
    В дальнейшем, к перечислению можно обратиться через ``EventCode``.

    Пример:

    ::

        DATALOGGER_EVENT_CODE = {
            'CUSTOM_EVENT_CODE': ('cec', 'Собственный код события'),
        }


``DATALOGGER_SYSTEMS_ENUM``
    Перечисление подсистем, в которых возникает событие:
    В дальнейшем, к перечислению можно обратиться через ``SystemEnum``.

    Пример:

    ::

        DATALOGGER_SYSTEMS_ENUM = {
            'APPICATION': ('app', u'Основное приложение'),
        }


``DATALOGGER_SUSPECTS_MODEL``
    Список моделей, состояние которых необходимо отслеживать.
    Причем, в качестве элемента списка можно использовать как полный путь до
    модели, так и сокращенный.
    Как альтернатива, можно указывать DataLoggingManager прямо в классе модели.

    Пример:

    ::

        DATALOGGER_SUSPECTS_MODEL = [
            'module_name.ModelName',
            'project_name.core.module_name.models.ModelName',
        ]


``DATALOGGER_EXCLUDE_ACTIONS``
    Перечисление имен классов паков или экшенов, которые не нужно логировать.


``DATALOGGER_EXCLUDE_FIELDS``
    Перечень полей, которые не надо использовать при сравнении состояний модели.

    Пример:

    ::

        DATALOGGER_EXCLUDE_FIELDS = [
            'version', 'begin', 'end', 'modified',
        ]


``DATALOGGER_DATABASE``
    Наименование БД из  ``settings.DATABASES``, которая будет использована в
    качестве бэкенда для логгера.

    В случае, если БД отлична от основной БД приложения, то необходимо включить
    в ``settings.DATABASE_ROUTERS`` классы ``NotUseDataLoggerDBRouter`` и 
    ``DataLoggerRouter``. 
    
    Для корректной работы с миграциями требуется подключить модуль ``datalogging.south_migration``
    который перекрывает команду South - ``migrate``.

    .. Note ::
        Так же требуется предварительный запуск команды syncdb.

    Пример:

    ::
    
        INSTALLED_APPS += ('datalogging.south_migration',)

        DATALOGGER_DATABASE = 'log_db'

        DATABASE_ROUTERS = (
            'datalogging.dbrouters.DataLoggerRouter',
            'datalogging.dbrouters.NotUseDataLoggerDBRouter',
        )


``DATALOGGER_SHUTUP``
    Если необходимо отключить логгер, то значение должно быть ``True`` в ином случае ``False``.


``DATALOGGER_FORGET_SYS_EVENTS``
    Если необходимо отключить логирование системных событий, то значение должно быть ``True`` в ином случае ``False``.


``DATALOGGER_HOOKED_ACTIONS``
    Для возможности кастомного логирования вызова определенных экшенов, требуется указать их в словаре вида::
        
        DATALOGGER_EVENT_CODE = {
            'CUSTOM_EVENT_CODE': ('cec', 'description event')
        }

        DATALOGGER_HOOKED_ACTIONS = {
            'SomeActionClassName': 'CUSTOM_EVENT_CODE'
        }

    Позже, событие с экшеном можно перехватить по коду в обработчике сигнала post_system_event_signal, в kwargs будут присутствовать action и request.

``DATALOGGER_COMPRESS_FILENAME_TEMPLATE``
    Определяет формат именования файлов при архивировании логов. По умолчанию ``datalogging-dump-%d-%m-%Y-%H-%M``.

``DATALOGGER_COMPRESS_DESTINATION``
    Определяет место назначения для архивов лога. По умолчанию: текущая папка.


Использование
=============

Добавить в ``INSTALLED_APPS``.

Для использования логгера строго необходимо определить обработчики 
сигналов.

Сигналы
-------

``msg_for_log_signal``
    Сигнал возникает при формировании логгером человекпонятного описания 
    события. В случае, если событие системное(открытие пользователем окошка), то ``model_instance`` будет иметь ``None`` в качестве значения.
    В качестве возвращаемого значения должна быть представлена строка.

    Передаваемые аргументы:

    - ``log_record`` - экземпляр записи лога,
    - ``model_instance`` - экземпляр записи модели,
    - ``fields_dict`` - словарь полей экземпляра модели, где ключ - имя поля, а значение - значение поля в модели.


``log_context_signal``
    Если приложение запущено в режиме фоновой задачи (Celery и т.д.) или в режиме шела, то 
    ``request`` будет ``None``.

    Контекст события должен являться словарем и содержать значения:

    - ``suid`` - ID пользователя в среде, в которой произошло событие,
    - ``system_type`` - значение из ``SystemEnum`` описывающее текущую среду,
    - ``event_type`` - значение из ``EventType`` описывающее текущий тип события.

    В качестве возвращаемого значения должен быть представлен словарь.

    Передаваемые аргументы:

    - ``request`` - текущий запрос.


``post_snapshot_signal``
    Вызывается в момент формирования записи об измененном состоянии
    отслеживаемой модели. Позволяет изменить запись лога перед сохранением.

    Передаваемые аргументы:

    - ``log_record`` - не сохраненный в БД экземпляр записи лога


``post_system_event_signal``
    Вызывается в момент формирования записи о событии происшедшем в
    системе. Позволяет изменить запись лога перед сохранением.

    Передаваемые аргументы:

    - ``log_record`` - не сохраненный в БД экземпляр записи лога


Выборка записей
---------------

``filter_events`` 
    Позволяет отфильтровать записи лога. По поведению функция схожа
    с методом ``filter`` в Django ORM, с той лишь разницей, что есть
    возможность осуществлять поиск по сериализованным в JSON данным.

    Пример (поиск по загловку окна):

    ::

        filter_events(
            event_code=EventCode.WIN_OPEN,
            _context__title=u'Заголовок или его часть')


``get_events_by_token``
    Позволяет получить все записи с одинаковым токеном запроса. Т.е.
    все события возникшие в рамках одного запроса.

    Пример:

    ::

        get_events_by_token(some_log_record.request_token)


Партицирование таблицы хранения логов по месяцам
---------------

Для включения партицирования используйте manage команду $python manage.py datalogging_partition_prepare


Пример
------

**settings.py**

::

    ...

    DATALOGGER_DATABASE = 'default'
    DATALOGGER_EXCLUDE_FIELDS = ('version', 'modified')

    DATALOGGER_EVENT_CODE = {
        'CRITICAL_CHANGE': ('cc', u'Критичное изменение'),
    }

    DATALOGGER_SYSTEMS_ENUM = {
        'APPLICATION': ('app', u'Основное приложение'),
        'SCHEDULER': ('sch', u'Задачи вызыванные планировщиком'),
    }

    DATALOGGER_EVENT_TYPE = {
        'SYSTEM_EVENT': ('se', u'Системное событие'),
        'LEGALLY_EVENT': ('le', u'Юридически важное событие'),
    }

**signals.py**

::

    from datalogging.signals import custom_verbose, custom_log_context, post_snapshot


    def verbose_handler(sender, log_record, model_instance, fields_dict):
        model_mapping = {
            'module.Declaration': u'заявку (ID=%(id)s)',
            'module.DeclarationUnit': u'привязку заявки (ID=%(declaration_id)s) к учреждению (ID=%(unit_id)s)',
            'module.Children': u'ребенка (ID=%(id)s)',
            'module.Pupil': u'запись о зачислении ребенка (ID=%(children_id)s в группу (ID=%(grup_id)s)',
            'module.Deduct': u'запись об отчислении ребенка (ID=%(children_id)s) из группы (ID=%(group_id)s)',
            'module.Group': u'группу (ID=%(id)s) учреждения (ID=%(unit_id)s)',
            'module.Direct': u'направление заявки %(declaration_id)s в группу %(group_id)s'
        }

        operation_mapping = {
            EventCode.UPDATE: u'изменил(а)',
            EventCode.INSERT: u'создал(а)',
            EventCode.DELETE: u'удалил(а)'
        }
        
        if log_record.event_code == EventCode.WIN_OPEN:
            return u'Открыто окно: %s' % log_record.context_data['title']

        what = u'запись в "%s"' % model_instance._meta.verbose_name
        if log_record.object_type in model_mapping:
            what = model_mapping[log_rec.object_type] % fields_dict

        verbose = u'Пользователь (ID=%s) %s %s.' % (
            log_record.suid,
            operation_mapping.get(log_rec.event_code),
            what
        )

        return verbose


    def context_handler(sender, request):
        if request is None:
            user_id = None
            system_type = SystemsEnum.SHELL
            event_type = EventType.UNDEFINED
        else:
            user_id = getattr(request.user, 'id', None)
            url = request.get_full_path()
            if '/some_pattern' in url:
                event_type = EventType.SOME_TYPE
                system_type = SystemsEnum.APPLICATION
            elif '/some_diffierent_pattern' in url:
                event_type = EventType.SOME_DIFFERENT_TYPE
                system_type = SystemType.SCHEDULER

        return {'suid': user_id, 
                'event_type': event_type,
                'system_type': system_type}


    def post_snapshot_handler(sender, log_record):
        if log_record.object_type == 'module.SomeModelName' and log_record.event_code = EventCode.UPDATE:
            log_record.event_code = EventCode.CRITICAL_CHANGE


    msg_for_log_signal.connect(verbose_handler, weak=False)
    log_context_signal.connect(context_handler, weak=False)
    post_snapshot_signal.connect(post_snapshot_handler, weak=False)

Contents:

.. toctree::
   :maxdepth: 1

   overview
   install
   tutorial
   basic
   autodocs



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

