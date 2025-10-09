# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'DataLog', fields ['suid']
        db.create_index(u'data_logging', ['suid'])

        # Removing index on 'DataLog', fields ['request_token']
        db.delete_index(u'data_logging', ['request_token'])


    def backwards(self, orm):
        # Adding index on 'DataLog', fields ['request_token']
        db.create_index(u'data_logging', ['request_token'])

        # Removing index on 'DataLog', fields ['suid']
        db.delete_index(u'data_logging', ['suid'])


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
