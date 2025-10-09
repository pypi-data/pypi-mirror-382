# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ParanoidLog'
        db.create_table(u'data_logging', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('event_type', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('event_code', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('object_type', self.gf('django.db.models.fields.CharField')(max_length=96, null=True)),
            ('object_snapshot', self.gf('django.db.models.fields.TextField')(default='{}', null=True)),
            ('verbose', self.gf('django.db.models.fields.TextField')()),
            ('system_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('suid', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('context_data', self.gf('django.db.models.fields.TextField')(default='{}', null=True)),
            ('request_token', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
        ))
        db.send_create_signal('datalogging', ['DataLog'])


    def backwards(self, orm):
        # Deleting model 'ParanoidLog'
        db.delete_table(u'm3_paranoid_log')


    models = {
        'datalogging.datalog': {
            'Meta': {'object_name': 'DataLog', 'db_table': "u'data_logging'"},
            'context_data': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True'}),
            'event_code': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'object_snapshot': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True'}),
            'object_type': ('django.db.models.fields.CharField', [], {'max_length': '96', 'null': 'True'}),
            'request_token': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'suid': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'system_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'verbose': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['datalogging']
