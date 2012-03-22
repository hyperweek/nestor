# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'WufooRequest', fields ['wufoo_id']
        db.create_unique('nestor_wufoorequest', ['wufoo_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'WufooRequest', fields ['wufoo_id']
        db.delete_unique('nestor_wufoorequest', ['wufoo_id'])


    models = {
        'nestor.wufoorequest': {
            'Meta': {'object_name': 'WufooRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'request_data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'wufoo_id': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['nestor']
