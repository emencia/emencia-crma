"""Admin for pilot_academy.logs"""

# Import from the Standard Library
from os.path import join

# Import from Django
from django.conf import settings
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib import admin
from django.db.models import Max
from django.utils.translation import ugettext as _

# Import from here
from crma import models

# Import from Django Model-Translation
from modeltranslation.admin import TranslationAdmin
#
# EMAILS
#
class EmailAdmin(TranslationAdmin):
    list_display = ('channel', 'subject', 'interval', 'tag', 'enabled')
    list_filter = ('channel', 'enabled')

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            join(settings.STATIC_URL, 'js/jquery-ui.js'),
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class EmailSchedulerAdmin(ModelAdmin):
    list_display = ('from_address', 'contact', 'email', 'lang',
                    'ctime', 'sent_time', 'status')

    search_fields = ('from_address', 'email__subject')
    list_filter = ('status', 'lang', 'email')
    readonly_fields = ('extra_context', 'trace_error')

    fieldsets = (
            (_("Emails"), {
            'fields': (
                'from_address', 'contact', 'email', 'lang',
            )}),
            (_("Status"), {
            'fields': (
                ('sent_time', 'status'),
            )}),
            (_("Context"), {
            'fields': (
                ('extra_context', 'trace_error'),
            )}),
        )


class SubscriptionAdmin(ModelAdmin):
    list_display = ('channel', 'contact', 'state')
    search_fields = ('channel__title', 'contact__email')
    list_filter = ('channel', 'state')

    fieldsets = (
            (_("Emails"), {
            'fields': (
                'channel', 'contact',
            )}),
            (_("Subscribed info"), {
            'fields': (
                ('state', 'unsubscribe_key'),
            )}),
        )
    readonly_fields = ('unsubscribe_key', )


class ChannelAdmin(TranslationAdmin):
    list_display = ('title', 'from_address', 'required')
    list_filter = ('title', 'from_address', 'required')
    prepopulated_fields = {"channel_id": ("title",)}

    class Media:
        js = (
            'modeltranslation/js/force_jquery.js',
            join(settings.STATIC_URL, 'js/jquery-ui.js'),
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class ContactAdmin(ModelAdmin):
    list_display = ('email', 'lang')
    list_filter = ('lang',)
    search_fields = ('email',)


admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.Email, EmailAdmin)
admin.site.register(models.EmailScheduler, EmailSchedulerAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.Contact, ContactAdmin)
