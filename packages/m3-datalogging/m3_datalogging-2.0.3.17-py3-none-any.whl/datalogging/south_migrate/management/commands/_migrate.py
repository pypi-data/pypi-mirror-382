# coding: utf-8

"""
Migrate management command.
"""

import sys
from django.conf import settings
from django.utils.importlib import import_module

from south.management.commands.migrate import Command as MigrateCommand, \
    show_migration_changes, format_migration_list_item
from south import migration
from south.migration import Migrations
from south.exceptions import NoMigrations
from south.db import DEFAULT_DB_ALIAS

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


special_way = {
    'datalogging': getattr(settings, 'DATALOGGER_DATABASE', None),
}


class Command(MigrateCommand):
    u"""
    Команда является идентичной к South за тем исключением,
    что приложение datalogging обрабатывается отдельно.
    """

    def handle(self, app=None, target=None, skip=False, merge=False,
               backwards=False, fake=False, db_dry_run=False, show_list=False,
               show_changes=False, database=DEFAULT_DB_ALIAS,
               delete_ghosts=False, ignore_ghosts=False, **options):

        # NOTE: THIS IS DUPLICATED FROM django.core.management.commands.syncdb
        # This code imports any module named 'management' in INSTALLED_APPS.
        # The 'management' module is the preferred way of listening to post_syncdb
        # signals, and since we're sending those out with create_table migrations,
        # we need apps to behave correctly.
        for app_name in settings.INSTALLED_APPS:
            try:
                import_module('.management', app_name)
            except ImportError as exc:
                msg = exc.args[0]
                if not msg.startswith('No module named') or 'management' not in msg:
                    raise
            # END DJANGO DUPE CODE

        # if all_apps flag is set, shift app over to target
        if options.get('all_apps', False):
            target = app
            app = None

        # Migrate each app
        if app:
            try:
                apps = [Migrations(app)]
            except NoMigrations:
                print("The app '%s' does not appear to use migrations." % app)
                print("./manage.py migrate " + self.args)
                return
        else:
            apps = list(migration.all_migrations())

        # Do we need to show the list of migrations?
        if show_list and apps:
            list_migrations(apps, database, **options)

        if show_changes and apps:
            show_migration_changes(apps)

        if not (show_list or show_changes):

            for app in apps:
                _database = special_way.get(app.app_label(), database)
                if _database not in settings.DATABASES:
                    continue

                result = migration.migrate_app(
                    app,
                    target_name = target,
                    fake = fake,
                    db_dry_run = db_dry_run,
                    verbosity = int(options.get('verbosity', 0)),
                    interactive = options.get('interactive', True),
                    load_initial_data = not options.get('no_initial_data', False),
                    merge = merge,
                    skip = skip,
                    database = _database,
                    delete_ghosts = delete_ghosts,
                    ignore_ghosts = ignore_ghosts,)

                if result is False:
                    sys.exit(1) # Migration failed, so the command fails.


def list_migrations(apps, database=DEFAULT_DB_ALIAS, **options):
    """
    Prints a list of all available migrations (разбитых по БД), and which
    ones are currently applied.
    Accepts a list of Migrations instances.
    """
    from south.models import MigrationHistory
    applied_migrations = MigrationHistory.objects.filter(
        app_name__in=[app.app_label() for app in apps])

    databases = [database]
    for app in apps:
        _database = special_way.get(app.app_label())
        if not (_database is None or _database in databases):
            databases.append(_database)

    applied_migrations_lookup = {}
    for database in databases:
        applied_migrations = applied_migrations.using(database)
        key = '[{0}] {{0}}.{{1}}'.format(database)
        for mi in applied_migrations:
            mig_key = key.format(mi.app_name, mi.migration)
            applied_migrations_lookup[mig_key] = mi
    print()

    for app in apps:
        print(" " + app.app_label())
        name_tpl = '[{0}] {1}.{2}'
        # Get the migrations object
        for migration in app:
            app_label = migration.app_label()
            _database =  special_way.get(app_label)
            full_name = name_tpl.format(
                _database, app_label, migration.name())

            if full_name in applied_migrations_lookup:
                applied_migration = applied_migrations_lookup[full_name]

                print(format_migration_list_item(
                    migration.name(),
                    applied=applied_migration.applied,
                    **options))
            else:
                print(format_migration_list_item(
                    migration.name(),
                    applied=False,
                    **options))
        print()
