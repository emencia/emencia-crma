# -*- coding: utf-8 -*-

# Import from Model translation
from modeltranslation.translator import translator, TranslationOptions

# Import from Parrot CRMA
from .models import Channel, Email


class ChannelTranslationOptions(TranslationOptions):
    fields = ('title',)


class EmailTranslationOptions(TranslationOptions):
    fields = ('body', 'subject',)


translator.register(Channel, ChannelTranslationOptions)
translator.register(Email, EmailTranslationOptions)
