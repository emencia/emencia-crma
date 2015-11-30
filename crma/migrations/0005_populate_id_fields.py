# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string

class Migration(DataMigration):

    def forwards(self, orm):
        for channel in orm.Channel.objects.all():
            channel.channel_id = slugify(channel.title)
            channel.save()

        for mail in orm.Email.objects.all():
            mail.email_id = get_random_string(50).lower()
            mail.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'crma.channel': {
            'Meta': {'object_name': 'Channel'},
            'channel_id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'crma.contact': {
            'Meta': {'object_name': 'Contact'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subscriptions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['crma.Channel']", 'through': u"orm['crma.Subscription']", 'symmetrical': 'False'})
        },
        u'crma.email': {
            'Meta': {'object_name': 'Email'},
            'body': ('djangocms_text_ckeditor.fields.HTMLField', [], {'blank': 'True'}),
            'body_en': ('djangocms_text_ckeditor.fields.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'body_fr': ('djangocms_text_ckeditor.fields.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['crma.Channel']"}),
            'email_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('timedelta.fields.TimedeltaField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'subject_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'crma.emailscheduler': {
            'Meta': {'object_name': 'EmailScheduler'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['crma.Contact']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['crma.Email']"}),
            'extra_context': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'sent_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'sent'", 'max_length': '20'})
        },
        u'crma.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['crma.Channel']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['crma.Contact']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'unsubscribe_key': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['crma']
    symmetrical = True
