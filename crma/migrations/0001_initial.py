# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Channel'
        db.create_table(u'crma_channel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('from_address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'crma', ['Channel'])

        # Adding model 'Contact'
        db.create_table(u'crma_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
        ))
        db.send_create_signal(u'crma', ['Contact'])

        # Adding model 'Subscription'
        db.create_table(u'crma_subscription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['crma.Channel'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['crma.Contact'])),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('unsubscribe_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'crma', ['Subscription'])

        # Adding model 'Email'
        db.create_table(u'crma_email', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('body', self.gf('djangocms_text_ckeditor.fields.HTMLField')(blank=True)),
            ('interval', self.gf('timedelta.fields.TimedeltaField')()),
            ('enabled', self.gf('django.db.models.fields.BooleanField')()),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['crma.Channel'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'crma', ['Email'])

        # Adding model 'EmailScheduler'
        db.create_table(u'crma_emailscheduler', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sent_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['crma.Email'])),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('from_address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['crma.Contact'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='sended', max_length=20)),
        ))
        db.send_create_signal(u'crma', ['EmailScheduler'])


    def backwards(self, orm):
        # Deleting model 'Channel'
        db.delete_table(u'crma_channel')

        # Deleting model 'Contact'
        db.delete_table(u'crma_contact')

        # Deleting model 'Subscription'
        db.delete_table(u'crma_subscription')

        # Deleting model 'Email'
        db.delete_table(u'crma_email')

        # Deleting model 'EmailScheduler'
        db.delete_table(u'crma_emailscheduler')


    models = {
        u'crma.channel': {
            'Meta': {'object_name': 'Channel'},
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
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['crma.Channel']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('timedelta.fields.TimedeltaField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'crma.emailscheduler': {
            'Meta': {'object_name': 'EmailScheduler'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['crma.Contact']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['crma.Email']"}),
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'sent_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'sended'", 'max_length': '20'})
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