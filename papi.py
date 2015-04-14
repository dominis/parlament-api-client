#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import xmltodict
from functools import partial, update_wrapper
import logging


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

    def __init__(self, token, cache=None, debug=None):
        self.token = token
        self.logger = logging.getLogger(__name__)

        log_level = logging.INFO
        if debug is not None:
            log_level = logging.DEBUG

        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        assert isinstance(cache, (Cache, type(None))), \
            "cache should be an instance of papi.cache"

        self.cache = cache

    def __getattr__(self, key):
        self.endpoint = key
        if key in self.endpoints:
            url = self.url_template % key
            mfun = getattr(self, 'request_wrapper')
            fun = partial(mfun, url=url)
            return update_wrapper(fun, mfun)
        else:
            pass
            raise AttributeError('Invalid endpoint: %s' % key)

    __getitem__ = __getattr__

    def request_wrapper(self, url, **params):
        self.logger.debug('processing request - url: %s params: %s' % (url, params))
        params.update({'access_token': self.token})

        if self.cache:
            key = self.cache.generateKey([url, params])
            try:
                self.logger.debug('cache get: %s' % key)
                resp = self.cache.get(key)
                self.logger.debug('cache hit: %s' % key)
            except Exception:
                self.logger.debug('cache miss: %s' % key)
                resp = self.client(url, params)
                try:
                    self.cache.set(key, resp)
                    self.logger.debug('cache set: %s' % key)
                except Exception, e:
                    self.logger.error('cache store failed - key: %s error: %s' % (key, e))
        else:
            resp = self.client(url, params)


        return self.content(resp)

    def client(self, url, params):
        r = requests.get(url, params=params)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            raise Exception('%s %s' % (url, r.text.strip()))

        self.logger.debug('request: %s' % url)

        return r.text

    def content(self, xml):
        return xmltodict.parse(xml)[self.endpoint]


class Cache(object):
    def __init__(self):
        raise Exception (
            'Please override __init__() to'
            'provide a Connection object.'
            )

    def generateKey(*args):
        import hashlib
        import json

        return hashlib.md5(json.dumps(args[1])).hexdigest()

    def get(self, key):
        resp = self.client.get(key)
        if resp is None:
            raise KeyError

        return resp

    def set(self, key, value):
        return self.client.set(key, value)


class RedisCache(Cache):
    def __init__(self, host='localhost', port=6379, db=0):
        import redis
        self.client = redis.StrictRedis(host=host, port=port, db=db)
