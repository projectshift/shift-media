from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, shutil
from config.local import LocalConfig
from shiftmedia import BackendLocal
from shiftmedia import Storage
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
        storage.tmp
        self.assertTrue(os.path.exists(self.tmp_path))

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

    # ------------------------------------------------------
    # Resizer tests
    # ------------------------------------------------------

    def test_get_image_data_with_pil(self):
        """ Open a local image with PIL """
        self.prepare_uploads()
        path = os.path.join(self.upload_path, 'original_horizontal.jpg')
        from PIL import Image
        img = Image.open(path)
        img.thumbnail((1000, 1000))
        img.show()

        self.assertEquals('JPEG', img.format)
        self.assertEquals('RGB', img.mode)

    @attr('xxx')
    def test_can_Create_a_resize(self):
        """ Creating a resize"""
        self.prepare_uploads()
        src = path = os.path.join(self.upload_path, 'original_horizontal.jpg')
        storage = Storage(self.config, mock.MagicMock())
        storage.resize(src, 'dst', '100x1000', 'outbound')


