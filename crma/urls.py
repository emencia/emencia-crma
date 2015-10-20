"""pilot_academy.api.urls"""

# Import from Django
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

# Import from Pilot-Academy
from .views import ViewWebMail, UnsubscribeCompleted, UnsubscribeView


urlpatterns = patterns('',
    # View Web Email
    url(r'^viewmail/(?P<scheduler_id>[0-9A-Za-z]+)-(?P<scheduler_token>.+)/$',
        ViewWebMail.as_view(), name='crma_view_web_mail'),

    # Unsubscribe
    url(r'^unsubscribe/completed/$', UnsubscribeCompleted.as_view(),
        name='crma_unsubscribe_completed'),

    url(r'^unsubscribe/(?P<key>.+)/$', UnsubscribeView.as_view(),
        name='crma_unsubscribe'),
)
