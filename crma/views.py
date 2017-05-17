# -*- coding: utf-8 -*-

# Django
from django.views.generic import View, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

# CRMA
from .models import Subscription, EmailScheduler
from .models import cancel_subscription
from .utils import decode_id


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
        token = kwargs['scheduler_token']

        item = get_object_or_404(EmailScheduler, id=scheduler_id)
        return item.render(request, token=token, template=self.template_name)
