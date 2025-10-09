# coding: utf-8
import datetime

from django.db import models

from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Reason'
        db.create_table('edureception_reason', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True)),
        ))
        db.send_create_signal('edureception', ['Reason'])


    def backwards(self, orm):
        # Deleting model 'Reason'
        db.delete_table('edureception_reason')


    models = {
        'edureception.reason': {
            'Meta': {'object_name': 'Reason'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'})
        }
    }

    complete_apps = ['edureception']
