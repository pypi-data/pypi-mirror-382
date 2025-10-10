###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: item.py 5670 2025-10-08 14:44:40Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

try:
    unicode
except Exception:
    unicode = str

import zope.interface
import zope.location.interfaces

import m01.mongo.item
import m01.mongo.interfaces
from m01.mongo import LOCAL
from m01.mongo.fieldproperty import MongoFieldProperty

import m01.fs.base
from m01.fs import interfaces


###############################################################################
#
# file

@zope.interface.implementer(interfaces.IFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)
class FileStorageItem(m01.fs.base.FileItemBase):
    """Simple mongo file item.

    This FileStorageItem will use the mongo ObjectId as the __name__. This
    means you can't set an own __name__ value for this object.

    Implement your own IFileStorageItem with the attributes you need and the
    relevant chunks collection.
    """

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


@zope.interface.implementer(interfaces.ISecureFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)
class SecureFileStorageItem(m01.fs.base.SecureFileItemBase):
    """Security aware IFileStorageItem."""

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


@zope.interface.implementer(interfaces.IFileContainerItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)
class FileContainerItem(m01.fs.base.FileItemBase):
    """File container item.

    Implement your own IFileContainerItem with the attributes you need and the
    relevant chunks collection.
    """

    _skipNames = []

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])


@zope.interface.implementer(interfaces.ISecureFileContainerItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)
class SecureFileContainerItem(m01.fs.base.SecureFileItemBase):
    """Security aware IFileStorageItem."""

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])


@zope.interface.implementer(interfaces.IFileObject)
class FileObject(m01.fs.base.FileBase, m01.mongo.item.MongoObject):
    """MongoObject based file"""

    _dumpNames = ['_id', '_oid', '__name__', '_type', '_version',
                  '_field',
                  'created', 'modified', 'removed',
                  'data', 'size', 'md5', 'filename', 'contentType', 'encoding',
                  'uploadDate']

    @property
    def collection(self):
        return self.getCollection(self.__parent__)


###############################################################################
#
# image

@zope.interface.implementer(interfaces.IImageStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)
class ImageStorageItem(m01.fs.base.ImageItemBase):
    """Simple mongo file item.

    This ImageStorageItem will use the mongo ObjectId as the __name__. This
    means you can't set an own __name__ value for this object.

    Implement your own IImageStorageItem with the attributes you need and the
    relevant chunks collection.
    """
    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


@zope.interface.implementer(interfaces.ISecureImageStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)
class SecureImageStorageItem(m01.fs.base.SecureImageItemBase):
    """Security aware IImageStorageItem."""

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


@zope.interface.implementer(interfaces.IImageContainerItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)
class ImageContainerItem(m01.fs.base.ImageItemBase):
    """Image container item.

    Implement your own IImageContainerItem with the attributes you need and the
    relevant chunks collection.
    """

    _skipNames = []

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])


@zope.interface.implementer(interfaces.ISecureImageContainerItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)
class SecureImageContainerItem(m01.fs.base.SecureImageItemBase):
    """Security aware IImageStorageItem."""

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])


@zope.interface.implementer(interfaces.IImageObject)
class ImageObject(m01.fs.base.ImageBase, m01.mongo.item.MongoObject):
    """MongoObject based file"""

    _dumpNames = ['_id', '_oid', '__name__', '_type', '_version',
                  '_field',
                  'created', 'modified', 'removed',
                  'data', 'size', 'md5', 'filename', 'contentType', 'encoding',
                  'uploadDate', 'width', 'height',]

    @property
    def collection(self):
        return self.getCollection(self.__parent__)
