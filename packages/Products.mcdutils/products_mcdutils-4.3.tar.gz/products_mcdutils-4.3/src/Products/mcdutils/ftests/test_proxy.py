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
""" Functional tests for Products.mcdutils.proxy """
import unittest


class MemCacheSDCFuncTests(unittest.TestCase):

    def _makeOne(self):
        from ..proxy import MemCacheProxy
        from ..sessiondata import MemCacheSessionDataContainer
        sdc = MemCacheSessionDataContainer()
        sdc.mcproxy = MemCacheProxy()
        sdc.proxy_path = 'mcproxy'

        return sdc

    def test_writing_to_mapping_no_memcache(self):
        from ..mapping import MemCacheMapping

        sdc = self._makeOne()
        mapping = sdc.new_or_existing('foobar')
        self.assertIsInstance(mapping, MemCacheMapping)
        self.assertFalse(mapping._p_changed)
        self.assertFalse(mapping._p_joined)
        mapping['abc'] = 1345
        self.assertTrue(mapping._p_changed)
        self.assertTrue(mapping._p_joined)
        import transaction
        transaction.commit()

    def test_writing_to_mapping_with_memcache(self):
        from ..mapping import MemCacheMapping

        sdc = self._makeOne()
        sdc._get_proxy().servers = ('localhost:11211',)
        mapping = sdc.new_or_existing('foobar')
        self.assertIsInstance(mapping, MemCacheMapping)
        self.assertFalse(mapping._p_changed)
        self.assertTrue(mapping._p_joined)
        mapping['abc'] = 1345
        self.assertTrue(mapping._p_changed)
        self.assertTrue(mapping._p_joined)
        import transaction
        transaction.commit()

    def test_writing_to_mapping_with_invalid_memcache_raises(self):
        from .. import MemCacheError

        sdc = self._makeOne()
        sdc._get_proxy().servers = ('nonesuch:999999',)
        mapping = sdc.new_or_existing('foobar')
        mapping['abc'] = 1345
        import transaction
        self.assertRaises(MemCacheError, transaction.commit)
        transaction.abort()
