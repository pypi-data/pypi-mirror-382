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
$Id: base.py 4804 2018-03-16 04:27:22Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import m01.mongo.base
from m01.mongo.fieldproperty import MongoFieldProperty
from m01.mongo.fieldproperty import MongoBinaryProperty

from m01.fs import interfaces
import m01.fs.chunker


###############################################################################
#
# file and image shared core

class FileCore(object):
    """File base class"""

    data = MongoBinaryProperty(interfaces.IFileBaseSchema['data'])

    size = MongoFieldProperty(interfaces.IFileBaseSchema['size'])
    md5 = MongoFieldProperty(interfaces.IFileBaseSchema['md5'])
    filename = MongoFieldProperty(interfaces.IFileBaseSchema['filename'])
    contentType = MongoFieldProperty(interfaces.IFileBaseSchema['contentType'])
    encoding = MongoFieldProperty(interfaces.IFileBaseSchema['encoding'])
    uploadDate = MongoFieldProperty(interfaces.IFileBaseSchema['uploadDate'])
    encoding = MongoFieldProperty(interfaces.IFileBaseSchema['encoding'])

    removed = MongoFieldProperty(interfaces.IFileBaseSchema['removed'])

    def getFileWriter(self):
        """Returns a IChunkWriter"""
        raise NotImplementedError(
            "Subclass must implement getFileWriter method")

    def getFileReader(self):
        """Returns a IChunkReader"""
        raise NotImplementedError(
            "Subclass must implement getFileReader method")

    def applyFileUpload(self, fileUpload):
        """Apply FileUpload given from request publisher"""
        if not fileUpload or not fileUpload.filename:
            # empty string or None means no upload
            raise ValueError("Missing file upload data")
        elif self.removed:
            raise ValueError("Can't store data for removed files")
        writer = self.getFileWriter()
        writer.add(fileUpload)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.__name__)


###############################################################################
#
# file

class FileBase(FileCore):
    """File base class"""

    def getFileWriter(self):
        """Returns a IChunkReader"""
        return m01.fs.chunker.FileChunkWriter(self)

    def getFileReader(self):
        """Returns a IChunkReader"""
        return m01.fs.chunker.FileChunkReader(self)


class FileItemBase(FileBase, m01.mongo.base.MongoItemBase):
    """Mongo file item base class."""

    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified', 'removed',
                  'data', 'size', 'md5', 'filename', 'contentType', 'encoding',
                  'uploadDate',
                  ]


class SecureFileItemBase(FileBase, m01.mongo.base.SecureMongoItemBase):
    """Secure mongo file item base class."""

    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified', 'removed',
                  '_ppmrow', '_ppmcol',
                  '_prmrow', '_prmcol',
                  '_rpmrow', '_rpmcol',
                  'data', 'size', 'md5', 'filename', 'contentType', 'encoding',
                  'uploadDate',
                  ]


###############################################################################
#
# image

class ImageBase(FileCore):
    """File base class"""

    width = MongoFieldProperty(interfaces.IImageSchema['width'])
    height = MongoFieldProperty(interfaces.IImageSchema['height'])

    def getFileWriter(self):
        """Returns a IChunkReader"""
        return m01.fs.chunker.ImageChunkWriter(self)

    def getFileReader(self):
        """Returns a IChunkReader"""
        return m01.fs.chunker.ImageChunkReader(self)


class ImageItemBase(ImageBase, m01.mongo.base.MongoItemBase):
    """Mongo image item base class."""

    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified', 'removed',
                  'data', 'size', 'md5', 'filename', 'contentType', 'encoding',
                  'uploadDate', 'width', 'height',
                  ]


class SecureImageItemBase(ImageBase, m01.mongo.base.SecureMongoItemBase):
    """Secure mongo image item base class."""

    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified', 'removed',
                  '_ppmrow', '_ppmcol',
                  '_prmrow', '_prmcol',
                  '_rpmrow', '_rpmcol',
                  'data', 'size', 'md5', 'filename', 'contentType', 'encoding',
                  'uploadDate', 'width', 'height',
                  ]
