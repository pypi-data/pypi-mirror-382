# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'DataLog', fields ['object_snapshot']
        db.create_index(u'data_logging', ['object_snapshot'])

        # Adding index on 'DataLog', fields ['event_type']
        db.create_index(u'data_logging', ['event_type'])

        # Adding index on 'DataLog', fields ['context_data']
        db.create_index(u'data_logging', ['context_data'])

        # Adding index on 'DataLog', fields ['object_type']
        db.create_index(u'data_logging', ['object_type'])

        # Adding index on 'DataLog', fields ['object_id']
        db.create_index(u'data_logging', ['object_id'])

        # Adding index on 'DataLog', fields ['event_code']
        db.create_index(u'data_logging', ['event_code'])

        # Adding index on 'DataLog', fields ['ip']
        db.create_index(u'data_logging', ['ip'])

        # Adding index on 'DataLog', fields ['verbose']
        db.create_index(u'data_logging', ['verbose'])

    
    def backwards(self, orm):
        # Removing index on 'DataLog', fields ['verbose']
        db.delete_index(u'data_logging', ['verbose'])

        # Removing index on 'DataLog', fields ['ip']
        db.delete_index(u'data_logging', ['ip'])

        # Removing index on 'DataLog', fields ['event_code']
        db.delete_index(u'data_logging', ['event_code'])

        # Removing index on 'DataLog', fields ['object_id']
        db.delete_index(u'data_logging', ['object_id'])

        # Removing index on 'DataLog', fields ['object_type']
        db.delete_index(u'data_logging', ['object_type'])

        # Removing index on 'DataLog', fields ['context_data']
        db.delete_index(u'data_logging', ['context_data'])

        # Removing index on 'DataLog', fields ['event_type']
        db.delete_index(u'data_logging', ['event_type'])

        # Removing index on 'DataLog', fields ['object_snapshot']
        db.delete_index(u'data_logging', ['object_snapshot'])


    models = {
        'datalogging.datalog': {
            'Meta': {'object_name': 'DataLog', 'db_table': "u'data_logging'"},
            'context_data': ('json_field.fields.JSONField', [], {'default': "'{}'", 'null': 'True', 'db_index': 'True'}),
            'event_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'object_snapshot': ('json_field.fields.JSONField', [], {'default': "'{}'", 'null': 'True', 'db_index': 'True'}),
            'object_type': ('django.db.models.fields.CharField', [], {'max_length': '96', 'null': 'True', 'db_index': 'True'}),
            'request_token': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'suid': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'system_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'verbose': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['datalogging']
