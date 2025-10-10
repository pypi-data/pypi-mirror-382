======
README
======

Let's test some fake helper methods.

  >>> import re
  >>> import datetime
  >>> import bson.tz_util
  >>> import m01.fake
  >>> from m01.fake import pprint


RENormalizer
------------

The RENormalizer is able to normalize text and produce comparable output. You
can setup the RENormalizer with a list of input, output expressions. This is
usefull if you dump mongodb data which contains dates or other not so simple
reproducable data. Such a dump result can get normalized before the unit test
will compare the output. Also see zope.testing.renormalizing for the same
pattern which is useable as a doctest checker.

  >>> normalizer = m01.fake.RENormalizer([
  ...    (re.compile(r'[0-9]*[.][0-9]* seconds'), r'... seconds'),
  ...    (re.compile(r'at 0x[0-9a-f]+'), r'at ...'),
  ...    ])

  >>> text = """
  ... <object object at 0xb7f14438>
  ... completed in 1.234 seconds.
  ... ...
  ... <object object at 0xb7f14450>
  ... completed in 1.234 seconds.
  ... """

  >>> print((normalizer(text)))
  <BLANKLINE>
  <object object at ...>
  completed in ... seconds.
  ... 
  <object object at ...>
  completed in ... seconds.
  <BLANKLINE>

Now let's test some mongodb relevant stuff:

  >>> from bson.dbref import DBRef
  >>> from bson.min_key import MinKey
  >>> from bson.max_key import MaxKey
  >>> from bson.objectid import ObjectId
  >>> from bson.timestamp import Timestamp

  >>> import time
  >>> import calendar
  >>> import struct
  >>> def getObjectId(secs=0):
  ...    """Knows how to generate similar ObjectId based on integer (counter)"""
  ...    time_tuple = time.gmtime(secs)
  ...    ts = calendar.timegm(time_tuple)
  ...    oid = struct.pack(">i", int(ts)) + b"\x00" * 8
  ...    return ObjectId(oid)

  >>> oid = getObjectId(42)
  >>> oid
  ObjectId('0000002a0000000000000000')

  >>> data = {'oid': oid,
  ...         'dbref': DBRef("foo", 5, "db"),
  ...         'date': datetime.datetime(2011, 5, 7, 1, 12),
  ...         'utc': datetime.datetime(2011, 5, 7, 1, 12, tzinfo=bson.tz_util.utc),
  ...         'min': MinKey(),
  ...         'max': MaxKey(),
  ...         'timestamp': Timestamp(4, 13),
  ...         're': '<_sre.SRE_Pattern object at 0x7f399087cb70>',
  ...         'string': 'string',
  ...         'unicode': u'unicode',
  ...         'int': 42}

Now let's pretty print the data:

  >>> print((m01.fake.reNormalizer(data)))
  {'date': datetime.datetime(...),
   'dbref': DBRef('foo', 5, 'db'),
   'int': 42,
   'max': MaxKey(),
   'min': MinKey(),
   'oid': ObjectId('...'),
   're': '<_sre.SRE_Pattern object at ...>',
   'string': 'string',
   'timestamp': Timestamp('...'),
   'unicode': 'unicode',
   'utc': datetime.datetime(2011, 5, 7, 1, 12, tzinfo=UTC)}


reNormalizer
------------

As you can see our predefined reNormalizer will convert the values using our
given patterns:

  >>> import m01.fake
  >>> print((m01.fake.reNormalizer(data)))
  {'date': datetime.datetime(...),
   'dbref': DBRef('foo', 5, 'db'),
   'int': 42,
   'max': MaxKey(),
   'min': MinKey(),
   'oid': ObjectId('...'),
   're': '<_sre.SRE_Pattern object at ...>',
   'string': 'string',
   'timestamp': Timestamp('...'),
   'unicode': 'unicode',
   'utc': datetime.datetime(2011, 5, 7, 1, 12, tzinfo=UTC)}


pprint
------

  >>> m01.fake.reNormalizer.pprint(data)
  {'date': datetime.datetime(...),
   'dbref': DBRef('foo', 5, 'db'),
   'int': 42,
   'max': MaxKey(),
   'min': MinKey(),
   'oid': ObjectId('...'),
   're': '<_sre.SRE_Pattern object at ...>',
   'string': 'string',
   'timestamp': Timestamp('...'),
   'unicode': 'unicode',
   'utc': datetime.datetime(2011, 5, 7, 1, 12, tzinfo=UTC)}


dictify
-------

  >>> import bson.son
  >>> son = bson.son.SON(data)
  >>> type(son)
  <class 'bson.son.SON'>

  >>> res = m01.fake.dictify(son)
  >>> type(res) is dict
  True

  >>> m01.fake.pprint(res)
  {'date': datetime.datetime(...),
   'dbref': DBRef('foo', 5, 'db'),
   'int': 42,
   'max': MaxKey(),
   'min': MinKey(),
   'oid': ObjectId('...'),
   're': '<_sre.SRE_Pattern object at ...>',
   'string': 'string',
   'timestamp': Timestamp('...'),
   'unicode': 'unicode',
   'utc': datetime.datetime(2011, 5, 7, 1, 12, tzinfo=UTC)}


getObjectId
-----------

The mthod getObjectId knows how to generate similar ObjectId based on an
integer. This method can get used if you need to define similar ObjectId in a
non persistent environment if need to bootstrap mongo containers.

  >>> m01.fake.getObjectId(42)
  ObjectId('0000002a0000000000000000')
