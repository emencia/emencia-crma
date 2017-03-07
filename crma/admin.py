"""Admin for pilot_academy.logs"""

# Import from the Standard Library
from os.path import join

# Import from Django
from django.conf import settings
from django.contrib.admin import ModelAdmin
from django.contrib import admin
from django import forms
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
                    'ctime', 'sched_time', 'sent_time', 'status')

    search_fields = ('from_address', 'email__subject', 'contact__email')
    list_filter = ('status', 'lang', 'email__channel', 'email')
    readonly_fields = ('extra_context', 'trace_error')
    raw_id_fields = ('contact',)

    fieldsets = (
            (_("Emails"), {
                'fields': (
                    'from_address', 'contact', 'email', 'lang', 'sched_time'
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
    raw_id_fields = ('contact',)

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


class MembersInline(admin.TabularInline):
    model = models.MailingList.members.through
    extra = 0
    raw_id_fields = ('contact',)


class MailingListForm(forms.ModelForm):
    csv = forms.FileField(
        required=False,
        help_text=u'The CSV file must have a header line with two columns: '
                  u'"email" and "lang".',
    )

    class Meta:
        model = models.MailingList


class MailingListAdmin(ModelAdmin):
    list_display = ('title',)
    filter_horizontal = ['members']
    form = MailingListForm
    exclude = ('members',)

    inlines = [MembersInline]

    def save_related(self, request, form, formsets, change):
        proxy = super(MailingListAdmin, self)
        proxy.save_related(request, form, formsets, change)

        csv = form.cleaned_data['csv']
        if csv:
            obj = form.instance
            obj.import_contacts(csv)


admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.Email, EmailAdmin)
admin.site.register(models.EmailScheduler, EmailSchedulerAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.MailingList, MailingListAdmin)
