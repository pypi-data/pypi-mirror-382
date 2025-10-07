##############################################################################
#
# Copyright (c) 2008-2023 Tres Seaver and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################
""" Unit tests for Products.mcdutils.proxy """
import unittest


KEY = b'key1'


class FauxClientTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..proxy import FauxClient
        return FauxClient

    def _makeOne(self):
        return self._getTargetClass()()

    def test_faux_client(self):
        # Faux client only fakes out a few methods
        fc = self._makeOne()

        self.assertEqual(fc._get_server(KEY), (fc, KEY))
        fc.set(KEY, 'value1')
        self.assertEqual(fc._get_server(KEY), (fc, KEY))


class MemCacheProxyTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..proxy import MemCacheProxy
        return MemCacheProxy

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeOneWithMemcache(self, *args, **kw):
        from .helpers import DummyMemcache
        proxy = self._getTargetClass()(*args, **kw)
        proxy._v_client = DummyMemcache()
        return proxy

    def test_conforms_to_IMemCacheProxy(self):
        from zope.interface.verify import verifyClass

        from ..interfaces import IMemCacheProxy
        verifyClass(IMemCacheProxy, self._getTargetClass())

    def test__init__(self):
        proxy = self._makeOne('proxy', title='Proxy')

        self.assertEqual(proxy.getId(), 'proxy')
        self.assertEqual(proxy.servers, ())
        self.assertEqual(proxy.getProperty('servers'), ())
        self.assertEqual(proxy.title, 'Proxy')
        self.assertEqual(proxy.getProperty('title'), 'Proxy')

    def test__cached(self):
        proxy = self._makeOne('proxy')

        self.assertEqual(proxy._cached, {})

        proxy._v_cached = {'foo': 'bar'}
        self.assertEqual(proxy._cached, {'foo': 'bar'})

    def test_client(self):
        from memcache import Client
        proxy = self._makeOne('proxy')

        self.assertIsNotNone(proxy.client)

        proxy._v_client = 'x'
        self.assertEqual(proxy.client, 'x')

        # Set a server, which should create a real client instance
        proxy.servers = ('127.0.0.1:9999',)
        self.assertIsInstance(proxy.client, Client)

    def test__servers(self):
        proxy = self._makeOne('proxy')

        self.assertEqual(proxy.servers, ())
        proxy.servers = ('srv',)
        self.assertEqual(proxy.servers, ('srv',))

        # make sure all caches are cleared
        proxy._v_client = 'client'
        proxy._v_cache = 'cache'
        self.assertIsNotNone(getattr(proxy, '_v_client'))
        self.assertIsNotNone(getattr(proxy, '_v_cache'))
        proxy.servers = ('srv',)
        self.assertIsNone(getattr(proxy, '_v_client', None))
        self.assertIsNone(getattr(proxy, '_v_cache', None))

    def test_create(self):
        from ..mapping import MemCacheMapping
        proxy = self._makeOne('proxy')

        created = proxy.create(KEY)
        self.assertIsInstance(created, MemCacheMapping)

    def test_get_set(self):
        proxy = self._makeOneWithMemcache('proxy')

        self.assertIsNone(proxy.get(KEY))
        self.assertTrue(proxy.set(KEY, proxy.create(KEY)))
        self.assertEqual(proxy.get(KEY), {})

        # This should also work when setting values that are
        # not MemCacheMapping instances
        KEY2 = b'key2'
        self.assertIsNone(proxy.get(KEY2))
        self.assertTrue(proxy.set(KEY2, {'foo': 'bar'}))
        self.assertEqual(proxy.get(KEY2), {'foo': 'bar'})

    def test_get_multi(self):
        proxy = self._makeOneWithMemcache('proxy')

        self.assertEqual(proxy.get_multi([KEY, b'key2']),
                         {KEY: None, b'key2': None})

    def test_add(self):
        proxy = self._makeOneWithMemcache('proxy')

        self.assertTrue(proxy.add(KEY, proxy.create(KEY)))
        self.assertEqual(proxy.get(KEY), {})

    def test_replace(self):
        proxy = self._makeOneWithMemcache('proxy')

        self.assertIsNone(proxy.replace(KEY, proxy.create(KEY)))
        self.assertIsNone(proxy.get(KEY))

        self.assertTrue(proxy.set(KEY, proxy.create(KEY)))
        self.assertEqual(proxy.get(KEY), {})

    def test_delete(self):
        proxy = self._makeOneWithMemcache('proxy')

        self.assertIsNone(proxy.delete(KEY), proxy.create(KEY))

        self.assertTrue(proxy.set(KEY, proxy.create(KEY)))
        self.assertTrue(proxy.delete(KEY))
        self.assertIsNone(proxy.get(KEY))
