# -*- coding: utf-8 -*-

# Import from Django
from django.views.generic import View, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import Http404

# Import from here
from .models import Subscription, EmailScheduler
from .models import cancel_subscription
from .utils import decode_id, generate_token


class UnsubscribeCompleted(TemplateView):
    template_name = 'crma/unsubscribe_completed.html'


class UnsubscribeView(View):
    success_url = 'crma_unsubscribe_completed'

    def get(self, request, *args, **kwargs):
        key = kwargs['key'].lower()
        subs_info = get_object_or_404(Subscription, unsubscribe_key=key)
        cancel_subscription(subs_info)

        return redirect(reverse(self.success_url))


class ViewWebMail(View):
    template_name = 'crma/mail_viewer.html'

    def get(self, request, *args, **kwargs):
        # Read the schedule item
        scheduler_id = decode_id(kwargs['scheduler_id'])
        item = get_object_or_404(EmailScheduler, id=scheduler_id)

        # Create the related token to check that url token is valid
        contact = {
            'id': item.id,
            'contact': item.contact,
            'lang': item.lang,
            'extra_context': {},
        }
        token = generate_token(contact)

        if token != kwargs['scheduler_token']:
            raise Http404

        # Read the related unsubscribe token
        channel = item.email.channel
        subscribed = Subscription.get_or_create(item.contact, channel)
        contact['unsubscribe_key'] = subscribed.unsubscribe_key

        # Create the email body and show it
        body, subject = item.email.get_mail_html(contact)
        return render(request, self.template_name, {'body': body,
                                                    'subject': subject, })
