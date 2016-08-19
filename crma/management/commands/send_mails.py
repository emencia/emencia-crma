# -*- coding: UTF-8 -*-

# Import from the Standard Library
from datetime import datetime
import json
from optparse import make_option
import os
from smtplib import SMTPRecipientsRefused, SMTPResponseException
import sys
import time

# Import from Django
from django.core.management.base import BaseCommand
from django.utils.timezone import utc
from django.conf import settings
from django.db.models import Q

# Import from crma
from crma.models import EmailScheduler
from crma.models import ST_PENDING, ST_SENT, ST_ERROR
from crma.signals import email_sent


# EMAIL SCAN FREQUENCY
SCAN_EVERY = 30

CRMA_KEY = settings.CRMA_KEY if hasattr(settings, 'CRMA_KEY') else ''


# PostgreSQL or SQLite
def get_mails_to_send(emails, now):
    emails = emails.filter(sched_time__lt=now)
    emails = emails.filter(Q(key=CRMA_KEY) | Q(key=''))
    return emails.iterator()


OPTIONS = [
    # Name       Action        Dest     Default
    ('--debug',  'store_true', 'debug', False),
]

OPTIONS = [make_option(name, action=action, dest=dest, default=default)
                    for name, action, dest, default in OPTIONS]


class Command(BaseCommand):
    option_list = BaseCommand.option_list + tuple(OPTIONS)

    def handle(self, *args, **options):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        debug_mode = options['debug']

        while True:
            # Emails to send
            now = datetime.utcnow().replace(tzinfo=utc)
            emails = EmailScheduler.objects.filter(status=ST_PENDING)
            mails = get_mails_to_send(emails, now)

            if not mails:
                time.sleep(SCAN_EVERY)
                continue

            i = 0
            for mail in mails:
                extra_context = mail.extra_context or {}
                try:
                    data = {
                        'id': mail.id,
                        'lang': mail.lang,
                        'from_name': '',
                        'contact': mail.contact,
                        'extra_context': json.loads(extra_context),
                    }
                except Exception, e:
                    print 'Error: ', mail.pk
                    mail.status = ST_ERROR
                    mail.trace_error = e
                    mail.save()
                    continue

                try:
                    if debug_mode:
                        data['contact'].email = settings.CRMA_DEBUG_EMAIL
                    mail.email.send(data)
                except SMTPRecipientsRefused, e:
                    print 'Error: ', mail.pk
                    mail.trace_error = e
                    mail.status = ST_ERROR
                    mail.save()
                except SMTPResponseException, e:
                    print 'Error: ', mail.pk
                    if e.smt.p_code >= 500:
                        mail.status = ST_ERROR
                        mail.trace_error = e
                        mail.save()
                except Exception, e:
                    print 'Error: ', mail.pk
                    mail.status = ST_ERROR
                    mail.trace_error = e
                    mail.save()
                else:
                    mail.status = ST_SENT
                    mail.sent_time = datetime.utcnow().replace(tzinfo=utc)
                    mail.save()
                    i += 1

                    email_sent.send(sender=mail.__class__, data=data)

            print '%s - Sent %d emails' % (now, i)
            # SLEEP
            time.sleep(SCAN_EVERY)
