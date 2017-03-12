from unittest import mock, TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_raises

import os, shutil
from shiftmedia import Storage, BackendLocal, utils
from shiftmedia import exceptions as x
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers
from shiftmedia.testing.localstorage_testhelpers import TestConfig


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
        filepath = os.path.join(self.upload_path, 'test.tar.gz')
        id = storage.put(filepath)
        self.assertFalse(os.path.exists(filepath))
        self.assertTrue(id.endswith('-test.tar.gz'))

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

    # ------------------------------------------------------------------------
    # Integration Tests
    # ------------------------------------------------------------------------

    def test_get_original_url(self):
        """ Generating original url """
        path = self.path
        base_url = 'http://test.url'
        backend = BackendLocal(path, base_url)
        storage = Storage(TestConfig, backend)
        filename = 'example-object.tar.gz'
        id = utils.generate_id(filename)
        url = storage.get_original_url(id)
        self.assertTrue(url.startswith(base_url))
        self.assertTrue(url.endswith(filename + '/' + filename))

    def test_get_auto_crop_url(self):
        """ Generating auto crop url """
        path = self.path
        base_url = 'http://test.url'
        backend = BackendLocal(path, base_url)
        storage = Storage(TestConfig, backend)
        filename = 'example-object.tar.gz'
        id = utils.generate_id(filename)
        url = storage.get_auto_crop_url(
            id=id,
            size='100x200',
            factor='fill',
            output_format='gif',
            upscale=True,
            quality=80
        )
        self.assertTrue(url.startswith(base_url))
        url = url.replace(base_url, '').strip('/').split('/')
        self.assertEquals(filename, url[5])
        self.assertTrue(url[6].startswith('100x200-fill-80-upscale'))
        self.assertTrue(url[6].endswith('.gif'))


    def test_get_manual_crop_url(self):
        """ Generating manual crop url """
        path = self.path
        base_url = 'http://test.url'
        backend = BackendLocal(path, base_url)
        storage = Storage(TestConfig, backend)
        filename = 'example-object.tar.gz'
        id = utils.generate_id(filename)
        url = storage.get_manual_crop_url(
            id=id,
            sample_size='200x400',
            target_size='100x200',
            output_format='gif',
            upscale=True,
            quality=80
        )
        self.assertTrue(url.startswith(base_url))
        url = url.replace(base_url, '').strip('/').split('/')
        self.assertEquals(filename, url[5])
        self.assertTrue(url[6].startswith('100x200-200x400-80-upscale'))
        self.assertTrue(url[6].endswith('.gif'))

    @attr('zzz')
    def test_create_resize_from_filename(self):
        """ Creating resize from filename """
        raise Exception('Implement me')
        uploads = self.upload_path
        path = self.path
        self.prepare_uploads()
        file = os.path.join(uploads, 'original_vertical.jpg')

        backend = BackendLocal(path)
        storage = Storage(TestConfig, backend)
        paths = storage.paths

        id = storage.put(file)
        resize_filename = paths.get_auto_crop_filename(id, '100x200', 'fit')
        url = backend


        print()

        print('ID: ', id)

        self.clean()



















