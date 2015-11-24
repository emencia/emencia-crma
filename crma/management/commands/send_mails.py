# -*- coding: UTF-8 -*-

# Import from the Standard Library
import time, os, sys, json
from datetime import datetime
from smtplib import SMTPRecipientsRefused, SMTPResponseException

# Import from Django
from django.core.management.base import BaseCommand
from django.utils.timezone import utc
from django.db.models import Q
from django.db.models import F

# Import from dbs
from crma.models import EmailScheduler
from crma.models import ST_PENDING, ST_SENT, ST_ERROR

# EMAIL SCAN FREQUENCY
SCAN_EVERY = 30

class Command(BaseCommand):

    def handle(self, *args, **kw):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

        while True:
            # Emails to send
            now = datetime.utcnow().replace(tzinfo=utc)
            emails = EmailScheduler.objects.filter(status=ST_PENDING)
            mails = emails.filter(Q(ctime__lt=(now - F("email__interval"))))

            if not mails.exists():
                time.sleep(SCAN_EVERY)
                continue

            i = 0
            for mail in mails.iterator():
                data = {
                    'id': mail.id,
                    'lang': mail.lang,
                    'from_name': mail.from_name,
                    'to_address': mail.to_address,
                    'extra_context': json.loads(mail.extra_context),
                }

                try:
                    mail.email.send(data)
                except SMTPRecipientsRefused, e:
                    print 'Error: ', mail.pk
                    print repr(e)
                    mail.status = ST_ERROR
                    mail.save()
                except SMTPResponseException, e:
                    print 'Error: ', mail.pk
                    print repr(e)
                    if e.smtp_code >= 500:
                        mail.status = ST_ERROR
                        mail.save()
                except Exception, e:
                    print 'Error: ', mail.pk
                    print repr(e)
                else:
                    mail.status = ST_SENT
                    mail.sent_time = datetime.utcnow().replace(tzinfo=utc)
                    mail.save()
                    i += 1

            print '%s - Sent %d emails' % (now, i)
            ## SLEEP
            time.sleep(SCAN_EVERY)
