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
$Id: error.py 5564 2025-07-29 15:42:31Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component

import m01.fs.exceptions

import z3c.form.error


@zope.component.adapter(m01.fs.exceptions.FileError, None,
        None, None, None, None)
class FileErrorViewSnippet(z3c.form.error.ErrorViewSnippet):
    """An error view for ValueError."""

    def createMessage(self):
        return self.error.args[0]