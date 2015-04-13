#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import xmltodict
from functools import partial, update_wrapper

class PAPI():
    endpoints = (
            'kepviselok',
            'kepviselo',
            'szavazasok',
            'szavazas',
            'iromanyok',
            'iromany',
        )

    url_template = 'http://parlament.hu/cgi-bin/web-api/%s.cgi'

    def __init__(self, token, *args, **kwargs):
        self.token = token

    def __getattr__(self, key):
        self.endpoint = key
        if key in self.endpoints:
            url = self.url_template % key
            mfun = getattr(self, 'client')
            fun = partial(mfun, url=url)
            return update_wrapper(fun, mfun)
        else:
            pass
            raise AttributeError('Invalid endpoint: %s' % key)

    __getitem__ = __getattr__

    def client(self, url, **params):
        params.update({'access_token': self.token})
        r = requests.get(url, params=params)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            raise Exception(r.text.strip())

        return self.content(r.text)

    def content(self, xml):
        return xmltodict.parse(xml)[self.endpoint]


