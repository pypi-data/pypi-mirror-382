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
""" Product:  mcdutils

Implement Zope sessions using memcached as the backing store.
"""


class MemCacheError(IOError):
    pass


def initialize(context):

    from .proxy import MemCacheProxy
    from .proxy import addMemCacheProxy
    from .proxy import addMemCacheProxyForm
    context.registerClass(MemCacheProxy,
                          constructors=(addMemCacheProxyForm,
                                        addMemCacheProxy))

    from .sessiondata import MemCacheSessionDataContainer
    from .sessiondata import addMemCacheSessionDataContainer
    from .sessiondata import addMemCacheSessionDataContainerForm
    context.registerClass(MemCacheSessionDataContainer,
                          constructors=(addMemCacheSessionDataContainerForm,
                                        addMemCacheSessionDataContainer))

    from .zcache import MemCacheZCacheManager
    from .zcache import addMemCacheZCacheManager
    from .zcache import addMemCacheZCacheManagerForm
    context.registerClass(MemCacheZCacheManager,
                          constructors=(addMemCacheZCacheManagerForm,
                                        addMemCacheZCacheManager))
