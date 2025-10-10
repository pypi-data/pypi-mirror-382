======
README
======

This package provides a mongo database server testing stub. You can simply
setup such a mongodb stub server in a doctest like::

  import doctest
  import unittest

  import m01.stub.testing

  def test_suite():
      return unittest.TestSuite((
          doctest.DocFileSuite('README.txt',
              setUp=m01.stub.testing.setUpStubMongo,
              tearDown=m01.stub.testing.tearDownStubMongo,
              optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
          ))


  if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')

The m01/stub/testing.py module provides a start and stop method which will
download, install, start and stop a mongodb server. All this is done in the
m01/stub/testing/sandbox folder. Everytime a test get started the mongodb/data
folder get removed and a fresh empty database get used.

Note: Also see the zipFolder and unZipFile methods in testing.py which allows
you to setup mongodb data and before remove them store them as a zip file
for a next test run. Such a zipped data folder can get used in another test run
by set the path to the zip file as dataSource argument. Also check the
m01.mongo package for more test use cases.


Testing
-------

Let's use the pymongo package for test our mongodb server stub setup. Note we
use a different port for our stub server setup (45017 instead of 27017):

  >>> from pprint import pprint
  >>> from pymongo.periodic_executor import _shutdown_executors
  >>> import m01.stub.testing

Let's test our mongodb stub setup:

  >>> conn = m01.stub.testing.getTestClient()

  >>> pprint(conn.server_info())
  {...,
   ...'ok': 1.0,
   ...}

  >>> sorted([i for i in conn.list_database_names()])
  [...'admin', ...'local']

setup an index:

  >>> print(conn.m01_stub_testing.test.collection.create_index('dummy'))
  dummy_1

add an object:

  >>> result = conn.m01_stub_testing.test.insert_one({'__name__': 'foo', 'dummy': 'object'})
  >>> 'InsertOneResult' in str(result)
  True

  >>> _id = result.inserted_id
  >>> _id
  ObjectId('...')

remove them:

  >>> result = conn.m01_stub_testing.test.delete_one({'_id': _id})
  >>> 'DeleteResult' in str(result)
  True

  >>> result.acknowledged
  True

  >> m01.fake.pprint(result.raw_result)
  {'n': 1, 'ok': 1.0}

  >>> result.deleted_count
  1

and check the databsae names again:

  >>> sorted([i for i in list(conn.list_database_names())])
  [...'admin', ...'local', ...'m01_stub_testing']

Let's drop the database:

  >>> conn.drop_database("m01_stub_testing")
  >>> sorted([i for i in conn.list_database_names()])
  [...'admin', ...'local']


Close client:

  >>> conn.close()
  >>> _shutdown_executors()
