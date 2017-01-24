# Import from Django
from django.dispatch import Signal


email_sent = Signal(providing_args=['data'])
