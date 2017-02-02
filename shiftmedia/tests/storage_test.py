from unittest import mock, TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_raises

import os, shutil
from shiftmedia import Storage
from shiftmedia import exceptions as x
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('storage')
class StorageTests(TestCase, LocalStorageTestHelpers):
    """ Storage service tests """

    def setUp(self):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        self.clean()
        super().tearDown()

    # ------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------

    def test_instantiate_storage(self):
        """ Instantiating storage """
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        self.assertIsInstance(storage, Storage)

    def test_getting_tmp_creates_directory(self):
        """ Can create local temp upon getting """
        shutil.rmtree(self.tmp_path)
        storage = Storage(self.config, mock.MagicMock())
        tmp = storage.tmp
        self.assertTrue(os.path.exists(self.tmp_path))

    def test_put_file(self):
        """ Put uploaded file to storage """
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        self.prepare_uploads()
        filepath = os.path.join(self.upload_path, 'test.png')
        id = storage.put(filepath)
        self.assertFalse(os.path.exists(filepath))
        self.assertTrue(id.endswith('png'))

    def test_put_raises_on_nonexistent_src(self):
        """ Storage raises exception on nonexistent file put"""
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        with assert_raises(x.LocalFileNotFound) as exception:
            storage.put('CRAP')

    def test_delete_file_by_id(self):
        """ Deleting file from storage by id """
        id = '123'
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        storage.delete(id)
        backend.delete.assert_called_with(id)

















