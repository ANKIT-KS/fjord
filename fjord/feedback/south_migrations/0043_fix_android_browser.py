# -*- coding: utf-8 -*-
import os
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.conf import settings


class Migration(DataMigration):

    def forwards(self, orm):
        rows = (
            orm.Response.objects
            .filter(browser='Firefox', browser_platform='Android')
            .update(browser='Firefox for Android')
        )

        if not getattr(settings, 'TEST'):
            print (os.path.basename(__file__), 'Updated {0} rows'.format(rows))

    def backwards(self, orm):
        rows = (
            orm.Response.objects
            .filter(browser='Firefox for Android', browser_platform='Android')
            .update(browser='Firefox')
        )

        if not getattr(settings, 'TEST'):
            print (os.path.basename(__file__), 'Updated {0} rows'.format(rows))

    models = {
        u'feedback.product': {
            'Meta': {'object_name': 'Product'},
            'browser_data_browser': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'db_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_file': ('django.db.models.fields.CharField', [], {'default': "u'noimage.png'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'on_dashboard': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'on_picker': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'translation_system': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'feedback.response': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Response'},
            'api': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'browser': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'browser_platform': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'browser_version': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'campaign': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'happy': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'platform': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'rating': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'translated_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'url': ('fjord.base.models.EnhancedURLField', [], {'max_length': '200', 'blank': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'feedback.responsecontext': {
            'Meta': {'object_name': 'ResponseContext'},
            'data': ('fjord.base.models.JSONObjectField', [], {'default': '{}'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opinion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedback.Response']"})
        },
        u'feedback.responseemail': {
            'Meta': {'object_name': 'ResponseEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opinion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedback.Response']"})
        },
        u'feedback.responsepi': {
            'Meta': {'object_name': 'ResponsePI'},
            'data': ('fjord.base.models.JSONObjectField', [], {'default': '{}'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opinion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedback.Response']"})
        }
    }

    complete_apps = ['feedback']
    symmetrical = True
