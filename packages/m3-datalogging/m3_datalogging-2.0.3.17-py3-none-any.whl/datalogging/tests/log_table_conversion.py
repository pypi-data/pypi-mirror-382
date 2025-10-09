# coding: utf-8
# сeated on 26 дек. 2014 г.
# author: Michael Vorotyntsev

# Тут реализованы инструменты для того чтобы дамп таблицы записать
# в пустую базу средствами ORM. Если дамп таблицы большой его можно
# разбить на части по дням и записывать в несколько процессов.

import codecs
import dateutil.parser
import logging
import json
import gc
import os.path
import re
import time
from datalogging.models import DataLog
from json_field.fields import JSONDecoder
from multiprocessing import Process, Queue
from Queue import Empty


def separation_day(file_path, dir_path, sep_char=u'\t', logger_name='console'):
    """
    Распиливание дампа таблицы на части по дням.
    Вы можете сделать cvs-файл через COPY в Postgres.
    :param file_path: путь к дампу
    :param dir_path: директория где будут созданы файлы по дням
    :param sep_char: символ-разделитель полей в дампе таблицы
    :param logger_name: имя логера, для вывода информации по ходу выполнения
    """

    file_name, file_ext = os.path.basename(file_path).split('.')

    logger = logging.getLogger(logger_name)
    logger.info('конвертация...')
    start_time = time.time()
    log_step = 100000
    index = 0
    line_count = 0
    day_files = {}

    with codecs.open(file_path, 'r', encoding='utf-8') as result_file:
        line = result_file.readline()
        while line:
            line_count += 1
            index += 1
            if index >= log_step:
                index = 0
                logger.info(
                    u' обработано {} за {} дней'.format(
                        line_count, len(day_files)))
                gc.collect()

            row_data = line.split(sep_char, 3)
            # немного сжать
            row_data[3] = re.sub(
                r'\\\\', r'\\', re.sub(r'\\N', r'', row_data[3]))

            record_date = dateutil.parser.parse(row_data[2]).date()
            if record_date not in day_files:
                out_file = codecs.open(
                    os.path.join(
                        dir_path,
                        '{}_{}.{}'.format(
                            file_name,
                            record_date.isoformat().replace('-', '_'),
                            file_ext)),
                    mode='w',
                    encoding='utf-8')
                day_files[record_date] = out_file
            else:
                out_file = day_files[record_date]

            new_line = sep_char.join(row_data)
            out_file.write(new_line)

            line = result_file.readline()

        # закрыть файлы
        for done_file in day_files.values():
            done_file.close()

    logger.info((
        u'Время выполнения: {:.2f} мин. фйлов'
        u'создано {} записей обработано {}').format(
            (time.time() - start_time) / 60.0,
            len(day_files),
            line_count))


def _fill_db_worker(
        file_path,
        file_name,
        worker_num,
        free_workers,
        safe=True,
        remove_done=False,
        sep_char='\t',
        logger_name='console'):
    """
    Процесс работающий с файлом-источником записей для таблицы.
    """

    def convert_json(data):
        return json.loads(data, cls=JSONDecoder)

    fields = [
        (0, 'id', long),
        (1, 'guid', None),
        (2, 'timestamp', dateutil.parser.parse),
        (3, 'event_type', None),
        (4, 'event_code', None),
        (5, 'object_id', long),
        (6, 'object_type', None),
        (7, 'object_snapshot', convert_json),
        (8, 'verbose', None),
        (9, 'system_type', None),
        (10, 'suid', long),
        (11, 'ip', None),
        (12, 'context_data', convert_json),
        (13, 'request_token', None),
    ]

    logger = logging.getLogger(logger_name)
    start_time = time.time()

    log_step = 50000
    created = 0
    i = 0
    insert_time = 0.001

    with codecs.open(file_path, 'r', encoding='utf-8') as result_file:
        line = result_file.readline()
        while line:
            created += 1
            i += 1
            if i > log_step:
                i = 0
                logger.info(
                    u"{}: обработано: {}".format(file_name, created))
                gc.collect()

            row_date = line.split(sep_char)
            new_record = DataLog()
            for index, field, convertor in fields:
                data = row_date[index]
                if data:
                    if convertor:
                        try:
                            data = convertor(data)
                        except (ValueError, TypeError):
                            data = None
                else:
                    data = None

                if data:
                    setattr(new_record, field, data)

            created += 1
            insert_time_start = time.time()
            if not safe:
                new_record.save()
            insert_time = (
                insert_time + (time.time() - insert_time_start)) / 2.0

            line = result_file.readline()

    logger.info(
        u'{}: всего записей создано: {} за {:.2f} мин.'.format(
            file_name, created, (time.time() - start_time) / 60.0))
    logger.info(
        u'{} среднее время записи: {:.12f}'.format(
            file_name, insert_time))

    # отправить информацию о завершении
    free_workers.put(worker_num)
    # удалить обработанный файл
    if not safe and remove_done:
        os.remove(file_path)


def multiworker_fill(
        day_files_path,
        pool_size=12,
        safe=True,
        remove_done=False,
        sep_char='\t',
        logger_name='console'):
    """
    Запись данных в таблицу логов в несколько процессов из файлов данных
    разбитых по индексам или по дням.

    :param day_files_path: директория с файлами
    :param pool_size: количество процессов (размер пула)
    :param safe: безопасный режим (в базу не пишется, файлы не удаляются)
    :param remove_done: удалять обработанные файлы
        (полезно если у вас мало места на диске)
    :param sep_char: символ-разделитель полей в дампе таблицы
    :param logger_name: имя логера, для вывода информации по ходу выполнения
    """
    workers = {}
    start_time = time.time()
    for index in xrange(pool_size):
        workers[index + 1] = dict(
            name=None, pid=None)

    files = {}
    for name in os.listdir(day_files_path):
        file_path = os.path.join(day_files_path, name)
        if os.path.isfile(file_path):
            files[name] = {
                'path': file_path,
                'done': False,
                'run': False,
            }

    logger = logging.getLogger(logger_name)
    if not files:
        raise Exception()

    logger.info(u"Найдено {} файлов".format(len(files)))

    iter_delay = 2.0
    free_workers = Queue()
    file_done_count = 0

    def file_not_done(_file_data):
        return not _file_data[1].get('done')

    while any(map(file_not_done, files.iteritems())):
        # если есть свободный воркер его надо занять
        try:
            now_free = free_workers.get(block=False)
        except Empty:
            now_free = None
        else:
            logger.info(' >> освободился: {}'.format(now_free))

        for worker_num, worke_data in workers.iteritems():
            file_name = worke_data.get('name')
            pid = worke_data.get('pid')

            if pid:
                # через is_alive и вообще через pid
                # не получается, залипает зомби из-за использования
                # stdout (и stderr) в главном и дочерних процессах
                # обойти через .communicate() не получилось
                # зомби-pid-ы иногда сами подыхают но не сразу, как должно быть
                # если родительский процесс игнорирует SIGCHLD (
                # а он игнорируется по умолчанию),
                # то зомби остаются до завершения родительского процесса
                is_free = now_free == worker_num

                if is_free:
                    # завершился!
                    files[file_name].update(
                        run=False, done=True)
                    worke_data.update(pid=None, name=None)
                    file_done_count += 1
                    logger.info(
                        u' файлов выполнено {}'.format(file_done_count))
            else:
                is_free = True

            # можно запустить обработку для
            if is_free:

                # найти свободный файл не выполненный
                file_name = None
                for new_file_name, file_db_data in files.iteritems():
                    if file_db_data['done'] or file_db_data['run']:
                        # готов или обрабатывается
                        continue
                    # есть
                    file_name = new_file_name
                    break

                if file_name:
                    file_path = files[file_name].get('path')
                    proc = Process(
                        target=_fill_db_worker,
                        kwargs={
                            'worker_num': worker_num,
                            'free_workers': free_workers,
                            'file_name': file_name,
                            'file_path': file_path,
                            'remove_done': remove_done,
                            'safe': safe,
                            'logger_name': logger_name,
                            'sep_char': sep_char,
                        })

                    files[file_name].update(run=True, done=False)
                    proc.start()

                    worke_data.update(pid=proc.pid, name=file_name)
                    logger.info((
                        u'Будет запущен обработчик {} PID:{} '
                        u'для файла {}').format(
                            worker_num, proc.pid, file_path))
        # задержка перед каждой попыткой найти завершенный воркер
        # и создать новый, новый содается пока весь пул не будет
        # занят
        time.sleep(iter_delay)

    logger.info(
        u"Время выполнения: {0:.2f} мин.".format(
            (time.time() - start_time) / 60.0))
