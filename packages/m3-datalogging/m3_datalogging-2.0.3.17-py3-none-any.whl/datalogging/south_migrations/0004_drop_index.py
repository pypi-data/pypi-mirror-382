# -*- coding: utf-8 -*-
import itertools

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, connection


class Migration(SchemaMigration):

    def forwards(self, orm):
        self.if_exists_drop_index(u'data_logging', ['object_snapshot'])
        self.if_exists_drop_index(u'data_logging', ['context_data'])

        years = ['2014', '2015', '2016']
        months = [str(x).zfill(2) for x in range(1, 13)]

        for year, month in itertools.product(years, months):
            self.if_exists_drop_index(u'data_logging_y%sm%s' % (year, month), ['object_snapshot'], suffix='_idx')
            self.if_exists_drop_index(u'data_logging_y%sm%s' % (year, month), ['context_data'], suffix='_idx')

    def backwards(self, orm):
        pass

    def if_exists_drop_index(self, table_name, column_names, suffix=''):
        cursor = db._get_connection().cursor()
        tables = connection.introspection.get_table_list(cursor)
        if table_name in tables:
            index_name = ''.join(column_names)
            indexes = connection.introspection.get_indexes(cursor, table_name)
            if index_name in indexes:
                name = db.create_index_name(table_name, column_names, suffix=suffix)
                sql = db.drop_index_string % {
                    "index_name": db.quote_name(name),
                    "table_name": db.quote_name(table_name),
                }
                db.execute(sql)

    models = {
        'datalogging.datalog': {
            'Meta': {'object_name': 'DataLog', 'db_table': "u'data_logging'"},
            'context_data': ('json_field.fields.JSONField', [], {'default': "u'null'", 'null': 'True'}),
            'event_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'object_snapshot': ('json_field.fields.JSONField', [], {'default': "'{}'", 'null': 'True'}),
            'object_type': ('django.db.models.fields.CharField', [], {'max_length': '96', 'null': 'True', 'db_index': 'True'}),
            'request_token': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'suid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'system_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'verbose': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['datalogging']
