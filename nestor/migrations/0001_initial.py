# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WufooRequest'
        db.create_table('nestor_wufoorequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('request_data', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('when_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.CharField')(default='2', max_length=1)),
            ('wufoo_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('nestor', ['WufooRequest'])


    def backwards(self, orm):
        
        # Deleting model 'WufooRequest'
        db.delete_table('nestor_wufoorequest')


    models = {
        'nestor.wufoorequest': {
            'Meta': {'object_name': 'WufooRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'request_data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'wufoo_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['nestor']
