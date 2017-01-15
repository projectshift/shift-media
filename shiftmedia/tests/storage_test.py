from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, shutil
from config.local import LocalConfig
from shiftmedia import BackendLocal
from shiftmedia import Storage
from shiftmedia.resizer import Resizer
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

    def test_generate_id(self):
        """ Generating unique id"""
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        id1 = storage.generate_id('JPEG')
        id2 = storage.generate_id('JPEG')
        self.assertNotEqual(id1, id2)
        self.assertTrue(id1.endswith('-jpg'))

    def test_put_file(self):
        """ Put uploaded file to storage """
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        self.prepare_uploads()
        filepath = os.path.join(self.upload_path, 'test.png')
        id = storage.put(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_delete_file_by_id(self):
        """ Deleting file from storage by id """
        id = '123'
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        storage.delete(id)
        backend.delete.assert_called_with(id)

    @attr('xxx')
    def test_parse_autocrop_filename(self):
        """ Parsing autocrop filename """
        pass

    @attr('xxx')
    def test_parse_manual_crop_filename(self):
        """ Parsing manual crop filename """
        pass

















