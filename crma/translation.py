# -*- coding: utf-8 -*-

# Import from Model translation
from modeltranslation.translator import translator, TranslationOptions

# Import from Parrot CRMA
from .models import Email


class EmailTranslationOptions(TranslationOptions):
    fields = ('body','subject',)

translator.register(Email, EmailTranslationOptions)
