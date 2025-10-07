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
""" Unit tests for Products.mcdutils.sessiondata """
import unittest


class DummyClient:
    def _get_server(self, key):
        return self, key


class DummyProxy:
    def __init__(self):
        self._cached = {}

    def set(self, key, value):
        pass

    def _get(self, key, default=None):
        return self._cached.get(key, default)

    get = _get


class MemCacheSessionDataTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..sessiondata import MemCacheSessionDataContainer
        return MemCacheSessionDataContainer

    def _makeOne(self, id, title='', with_proxy=True):
        sdc = self._getTargetClass()(id, title=title)
        if with_proxy:
            sdc.dummy_proxy = DummyProxy()
            sdc.proxy_path = 'dummy_proxy'
        return sdc

    def test_conforms_to_ISessionDataContainer(self):
        from zope.interface.verify import verifyClass

        from ..interfaces import ISessionDataContainer
        verifyClass(ISessionDataContainer, self._getTargetClass())

    def test_conforms_to_IMemCacheSessionDataContainer(self):
        from zope.interface.verify import verifyClass

        from ..interfaces import IMemCacheSessionDataContainer
        verifyClass(IMemCacheSessionDataContainer, self._getTargetClass())

    def test_empty(self):
        sdc = self._makeOne('mcsdc')
        self.assertFalse(sdc.has_key('foobar'))  # NOQA: W601
        self.assertIsNone(sdc.get('foobar'))

    def test_invalid_proxy_raises_MemCacheError(self):
        from .. import MemCacheError
        sdc = self._makeOne('mcsdc', with_proxy=False)
        self.assertRaises(MemCacheError,
                          sdc.has_key, 'foobar')  # NOQA: W601
        self.assertRaises(MemCacheError, sdc.get, 'foobar')
        self.assertRaises(MemCacheError, sdc.new_or_existing, 'foobar')

    def test_new_or_existing_returns_txn_aware_mapping(self):
        from persistent.mapping import PersistentMapping
        from transaction.interfaces import IDataManager
        sdc = self._makeOne('mcsdc')
        created = sdc.new_or_existing('foobar')
        self.assertIsInstance(created, PersistentMapping)
        jar = created._p_jar
        self.assertIsNotNone(jar)
        self.assertTrue(IDataManager.providedBy(jar))

    def test_has_key_after_new_or_existing_returns_True(self):
        sdc = self._makeOne('mcsdc')
        sdc.new_or_existing('foobar')
        self.assertTrue(sdc.has_key('foobar'))  # NOQA: W601

    def test_get_after_new_or_existing_returns_same(self):
        sdc = self._makeOne('mcsdc')
        created = sdc.new_or_existing('foobar')
        self.assertIs(sdc.get('foobar'), created)
