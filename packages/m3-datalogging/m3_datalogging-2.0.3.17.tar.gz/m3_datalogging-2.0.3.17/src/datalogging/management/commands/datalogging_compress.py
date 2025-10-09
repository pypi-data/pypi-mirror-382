# coding: utf-8
"""
.. module:: datalogging.management.commands.datalogging_compress
.. moduleauthor:: Rinat Sabitov <sabitov@bars-open.ru>

"""
import os
import sys
import datetime
import tempfile
from zipfile import ZipFile
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core import management


class Command(BaseCommand):
    u"""Класс менежд-команды.
    """
    help = 'Archieve datalogging data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--destination',
            dest='destination',
            default=getattr(settings, 'DATALOGGER_COMPRESS_DESTINATION', ''),
            help='Archieving destination folder')
        parser.add_argument(
            '--reset',
            action='store_true',
            dest='reset',
            default=False,
            help='Delete all data after compress')

    def handle(self, *args, **options):
        u"""Метод обрабатыюващий команду. На входе ожидаются только именованые
        параметры переданные из командной строки, в частности
        `options['reset']` и `options['destination']`.
        """

        default_filename_template = 'datalogging-dump-%d-%m-%Y-%H-%M'
        filename_template = getattr(settings,
                'DATALOGGER_COMPRESS_FILENAME_TEMPLATE',
                default_filename_template)

        with tempfile.NamedTemporaryFile() as tf:
            #так как dumpdata сливает все в stdout, нам не остается ничего
            #другого как подменить сам stdout
            sysout = sys.stdout
            try:
                sys.stdout = tf
                management.call_command('dumpdata', 'datalogging')
            finally:
                sys.stdout = sysout

            filename = datetime.datetime.now().strftime(filename_template)
            with ZipFile(os.path.join(options['destination'],
                '%s.zip' % filename), 'w') as myzip:
                myzip.write(tf.name, filename + '.json')

        if options['reset']:
            management.call_command('reset', 'datalogging')
