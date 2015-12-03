# -*- coding: utf-8 -*-

from django.utils.http import int_to_base36, base36_to_int
from django.conf import settings
from hashlib import sha1 as sha_constructor
from django.contrib.gis.geoip import GeoIP


def get_request_ip(request):
    meta = request.META
    remote_ip = meta.get('HTTP_X_FORWARDED_FOR')
    if remote_ip:
        return remote_ip.split(',', 1)[0].strip()

    return meta.get('REMOTE_ADDR')


def generate_token(data):
    contact = data['contact']
    value = '%d%s%s' % (contact.pk, settings.SECRET_KEY,
                        contact.email.encode('utf-8'))
    return sha_constructor(value).hexdigest()


def encode_id(id_to_encode):
    return int_to_base36(id_to_encode)


def decode_id(id_to_decode):
    return base36_to_int(id_to_decode)


def country_ip(ip):
    if not ip:
        return ''

    geoip = GeoIP()
    c_code = geoip.country_code(ip)
    return c_code if c_code else ''
