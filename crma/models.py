# -*- coding: utf8 -*-

# Import from Python
import random
import sha
import json

# Import from Django
from django.db.models import Model, ForeignKey, ManyToManyField, TextField
from django.db.models import BooleanField, CharField, DateTimeField
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.utils.translation import ugettext_lazy as _, activate
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

# Import from ...
from djangocms_text_ckeditor.fields import HTMLField

# Import from Django Timedelta field
from timedelta.fields import TimedeltaField

# Import from here
from .utils import encode_id, generate_token


ST_SENT = 'sent'
ST_PENDING = 'pending'
ST_CANCELED = 'canceled'
ST_ERROR = 'error'
STATUS_CHOICES = ((ST_SENT, 'Sent'),
                  (ST_PENDING, 'Pending'),
                  (ST_CANCELED, 'Canceled'),
                  (ST_ERROR, 'Error'),)


class Channel(Model):
    """
    Contacts can subscribe to channels. Emails are attached to channels.  A
    contact will receive an email if he's subscribed to the email's channel.

    If the channel is marked as required (boolean field) then all contacts are
    implicitely subscribed to the channel. Typically there is one such channel,
    which could be called "Default", and can be used for sending administrative
    emails.
    """

    title = CharField(max_length=80)
    from_address = CharField(max_length=200,
                             help_text='"Name <email>" or "email"')
    required = BooleanField(default=False)

    def __unicode__(self):
        return self.title


class Contact(Model):

    email = CharField(max_length=200)
    lang = CharField(max_length=10, blank=True)
    subscriptions = ManyToManyField(Channel, through="Subscription")

    def __unicode__(self):
        return self.email


class Subscription(Model):

    SUBSCRIBED = 'subscribed'
    UNSUBSCRIBED = 'unsubscribed'
    STATE_CHOICES = (
        (SUBSCRIBED, 'Subscribed'),
        (UNSUBSCRIBED, 'Unsubscribed'),
    )

    channel = ForeignKey(Channel)
    contact = ForeignKey(Contact)
    state = CharField(max_length=20, choices=STATE_CHOICES)
    unsubscribe_key = CharField(_('unsubscribe key'), max_length=40)

    @classmethod
    def create_unsubscribe_key (cls, to_address):
        salt = sha.new(str(random.random())).hexdigest()[:5]
        return sha.new(salt+to_address).hexdigest()

    @classmethod
    def get_or_create(cls, contact, channel):
        """
        Read the data from ``Subscription`` model for address / channel pair.
        If not exists the subscription's info, then we create a row and
        subscribe the user.
        """
        info = Subscription.objects.filter(contact=contact, channel=channel)
        if info:
            return info[0]

        info = Subscription(contact=contact, channel=channel,
                            state=Subscription.SUBSCRIBED)
        info.unsubscribe_key = Subscription.create_unsubscribe_key(contact.email)
        info.save()
        return info


class Email(Model):

    subject = CharField(_('Subject'), max_length=200)
    body = HTMLField(blank=True)
    interval = TimedeltaField()
    enabled = BooleanField()
    channel = ForeignKey(Channel)
    tag = CharField(max_length=30, blank=True)

    unsubscribe_url = 'crma_unsubscribe'
    view_mail_url = 'crma_view_web_mail'

    def __unicode__(self):
        email = self.channel.title
        return '%s - %s' % (email, self.interval)

    def get_full_path(self, path):
        current_site = Site.objects.get_current()
        return "http://%s%s" % (current_site.domain, path)

    @staticmethod
    def get_lang_code(lang):
        default = 'en'
        if lang is None:
            return default

        languages = [x[0].lower() for x in settings.LANGUAGES]
        languages.sort(reverse=True)

        lang = lang.lower()
        for l in languages:
            if lang.startswith(l):
                return l

        return default

    def get_language(self, lang):
        lang = self.get_lang_code(lang)
        subject = getattr(self, 'subject_%s' % lang, None)
        if subject and subject.strip():
            return lang

        return 'en'

    def get_mail_html(self, contact):
        """
        contact: dict with the following data:
                - contact: Contact instance
                - unsubscribe_key: for the current channel
                - lang: lang we use to send the email
                - extra_context: dict with context fields for the template
        """
        lang = self.get_language(contact['lang'])
        activate(lang)  # activate user language

        # Generate unsubscribe url
        unsubscribe_path = reverse(self.unsubscribe_url,
                                   args=(contact['unsubscribe_key'],))
        unsubscribe_url = self.get_full_path(unsubscribe_path)

        # Generate view web email url
        params = (encode_id(contact['contact'].id), generate_token(contact))
        viewmail_path = reverse(self.view_mail_url, args=params)
        viewmail_url = self.get_full_path(viewmail_path)

        # Generate Subject and body content
        subject = getattr(self, 'subject_%s' % lang)
        body_html = getattr(self, 'body_%s' % lang)

        context = {'LANG': lang,
                   'UNSUBSCRIBE_URL': unsubscribe_url,
                   'VIEWMAIL_URL': viewmail_url,
                   }
        context.update(contact['extra_context'])
        context = Context(context)

        body = Template(body_html).render(context)
        subject = Template(subject).render(context)
        return body, subject

    def send(self, contact):
        """
        contact: dictionary
            - contact: Contact instance
            - lang: Language code
            - from_name: Name to display in the email address
            - to_address: contact email address
            - extra_context: dict with variables to add to the template context

        return False is the mail is not sent else True
        """
        to_address = contact['to_address']
        subscribed = Subscription.get_or_create(contact['contact'],
                                                self.channel)

        # If the user say he doesn't want emails, we don't send the email
        if not subscribed.status == Subscription.SUBSCRIBED:
            return False

        contact['unsubscribe_key'] = subscribed.unsubscribe_key

        # We can send the email
        addr = self.email_type.from_address
        body_html, subject = self.get_mail_html(contact)
        body_text = bleach.clean(body_html)
        email_to = [to_address]
        email_from = '%s <%s>' % (contact['from_name'], addr)

        headers = {'X-Tag': self.tag}
        msg = EmailMultiAlternatives(subject, body_text, email_from, email_to,
                                     headers=headers)
        msg.attach_alternative(body_html, "text/html")

        # Send
        msg.send()
        return True

    def __unicode__(self):
        return self.subject


class EmailScheduler(Model):

    ctime = DateTimeField(auto_now_add=True)
    sent_time = DateTimeField(null=True, blank=True)
    email = ForeignKey(Email)
    lang = CharField(max_length=10, blank=True)
    from_address = CharField(max_length=200, null=True, blank=True)
    contact = ForeignKey(Contact)
    status = CharField(max_length=20, choices=STATUS_CHOICES, default=ST_SENT)
    extra_context = TextField(blank=True)


def subscribe_to_channel(contact, channel, extra_context=''):
    if isinstance(channel, basestring):
        channel = Channel.objects.get(title=channel)

    subscription = Subscription.get_or_create(contact, channel)
    if not subscription.state == Subscription.SUBSCRIBED:
        subscription.state = Subscription.SUBSCRIBED
        subscription.save()

    # Now we Schedule the mails to send
    mails = Email.objects.filter(channel=channel, enabled=True)
    extra_ctxt = json.dumps(extra_context)
    for mail in mails:
        EmailScheduler.objects.create(email=mail,
                                      lang=contact.lang,
                                      from_address=channel.from_address,
                                      contact=contact,
                                      status=ST_PENDING,
                                      extra_context=extra_ctxt)


def cancel_pending_mails(filters):
    pending_mails = EmailScheduler.objects.filter(status==ST_PENDING)
    pending_mails.filter(**filters).update(status=ST_CANCELED)


def cancel_subscription(subscription):
    cancel_pending_mails({'contact': subscription.contact,
                          'email__channel': subscription.channel})
    subscription.state = Subscription.UNSUBSCRIBED
    subscription.save()


def unsubscribe_from_channel(contact, channel):
    subs = Subscription.objects.filter(contact=contact, channel=channel)

    # If the user is not subscribed then we exit
    if not subs or subs.state == Subscription.UNSUBSCRIBED:
        return

    cancel_subscription(subs)


def disable_email(email):
    cancel_pending_mails({'email': email})
    email.enabled = False
    email.save()
