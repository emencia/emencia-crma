# -*- coding: UTF-8 -*-

# Import from the Standard Library
import time
import os
import sys
import json

from datetime import datetime
from smtplib import SMTPRecipientsRefused, SMTPResponseException

from optparse import make_option

# Import from Django
from django.core.management.base import BaseCommand
from django.utils.timezone import utc
from django.conf import settings

# Import from dbs
from crma.models import EmailScheduler
from crma.models import ST_PENDING, ST_SENT, ST_ERROR

# EMAIL SCAN FREQUENCY
SCAN_EVERY = 30


# PostgreSQL or SQLite
def get_mails_to_send(emails, now):
    emails = emails.filter(sched_time__lt=now)
    return emails.iterator()


OPTIONS = [
    # Name       Action        Dest     Default
    ('--debug',  'store_true', 'debug', False),
]

OPTIONS = [ make_option(name, action=action, dest=dest, default=default)
                    for name, action, dest, default in OPTIONS ]

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
                if not mail.extra_context:
                    extra_context = {}
                else:
                    extra_context = mail.extra_context
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

            print '%s - Sent %d emails' % (now, i)
            # SLEEP
            time.sleep(SCAN_EVERY)
