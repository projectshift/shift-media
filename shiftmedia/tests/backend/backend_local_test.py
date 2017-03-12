from unittest import mock, TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_raises

import os, uuid
from shiftmedia import BackendLocal, utils, PathBuilder, exceptions as x
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('backend', 'local')
class BackendLocalTests(TestCase, LocalStorageTestHelpers):
    """ Local storage backend tests """

    def setUp(self, app=None):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        self.clean()
        super().tearDown()

    # ------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------

    def test_can_instantiate_backend(self):
        """ Can instantiate backend  """
        backend = BackendLocal(self.path)
        self.assertIsInstance(backend, BackendLocal)

    def test_convert_id_to_path(self):
        """ Converting id to path """
        backend = BackendLocal(self.path)
        filename = 'demo-test.tar.gz'
        id = utils.generate_id(filename)
        parts = backend.id_to_path(id)
        self.assertEquals(6, len(parts))
        self.assertEquals(filename, parts[5])

    def test_getting_path_creates_directory(self):
        """ Can create local path upon getting """
        self.assertFalse(os.path.exists(self.path))
        backend = BackendLocal(self.path)
        path = backend.path
        self.assertTrue(os.path.exists(path))

    def test_put_original_file(self):
        """ Put original file to storage """
        self.prepare_uploads()
        backend = BackendLocal(self.path)
        uploads = self.upload_path
        src = os.path.join(uploads, 'demo-test.tar.gz')
        id = utils.generate_id('demo-test.tar.gz')
        backend.put_original(src, id)

        # assert directories created
        current = self.path
        for dir in id.split('-')[0:5]:
            current = os.path.join(current, dir)
            self.assertTrue(os.path.exists(current))

        # assert file put
        full_file_path = os.path.join(current, 'demo-test.tar.gz')
        self.assertTrue(os.path.exists(full_file_path))

    def test_put_file(self):
        """ Put file to storage by filename"""
        self.prepare_uploads()
        backend = BackendLocal(self.path)
        uploads = self.upload_path
        src = os.path.join(uploads, 'demo-test.tar.gz')
        id = utils.generate_id('demo-test.tar.gz')
        backend.put(src, id, 'demo-test.tar.gz')

        # assert directories created
        current = self.path
        for dir in backend.id_to_path(id):
            current = os.path.join(current, dir)
            self.assertTrue(os.path.exists(current))

        # assert file put
        full_file_path = os.path.join(current, 'demo-test.tar.gz')
        self.assertTrue(os.path.exists(full_file_path))

    def test_put_raises_on_nonexistent_file(self):
        """ Put raises exception if source file does not exist """
        backend = BackendLocal(self.path)
        id = utils.generate_id('test.tar.gz')
        with assert_raises(x.LocalFileNotFound):
            backend.put('nonexistent', id, 'random.tar.gz')

    def test_put_with_sequential_ids(self):
        """ Putting two items in sequence"""
        filename = 'demo-test.tar.gz'
        base_id = utils.generate_id(filename).replace('-' + filename, '')
        id1 = base_id + '1-' + filename
        id2 = base_id + '2-' + filename
        self.prepare_uploads()
        backend = BackendLocal(self.path)
        uploads = self.upload_path
        src = os.path.join(uploads, 'demo-test.tar.gz')
        backend.put(src, id1, 'demo-test.tar.gz')
        backend.put(src, id2, 'demo-test.tar.gz')
        path1 = os.path.join(backend.path, *backend.id_to_path(id1), filename)
        path2 = os.path.join(backend.path, *backend.id_to_path(id2), filename)
        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))

    def test_put_raises_on_overwriting(self):
        """ Put raises exception on attempt to overwrite existing path """
        self.prepare_uploads()
        backend = BackendLocal(self.path)
        uploads = self.upload_path
        src1 = os.path.join(uploads, 'demo-test.tar.gz')
        src2 = os.path.join(uploads, 'test.jpg')
        id = utils.generate_id('demo-test.tar.gz')
        backend.put(src1, id, 'demo-test.tar.gz')
        with assert_raises(x.FileExists):
            backend.put(src2, id, 'demo-test.tar.gz')

    def test_force_put_to_overwrite_existing(self):
        """ Using force option to overwrite existing file """
        self.prepare_uploads()
        backend = BackendLocal(self.path)
        uploads = self.upload_path
        filename = 'demo-test.tar.gz'
        src1 = os.path.join(uploads, filename)
        src2 = os.path.join(uploads, 'test.jpg')
        id = utils.generate_id(filename)
        backend.put(src1, id, filename)
        backend.put(src2, id, filename, True)
        path = os.path.join(backend.path, *backend.id_to_path(id), filename)
        # assert overwritten with src2
        self.assertEquals(os.path.getsize(path), os.path.getsize(src2))


    def test_delete_file(self):
        """ Deleting file from local storage """
        # put file
        self.prepare_uploads()
        backend = BackendLocal(self.path)
        uploads = self.upload_path
        src = os.path.join(uploads, 'test.tar.gz')
        id1 = utils.generate_id('test.tar.gz')

        # regression testing
        id2 = id1.split('-')
        id2[4] += 'ZZZ'
        id2 = '-'.join(id2)

        backend.put(src, id1, 'original.tar.gz')
        backend.put(src, id2, 'original.tar.gz')
        backend.delete(id1)

        path1 = os.path.join(self.path, *id1.split('-')[0:6], 'original.tar.gz')
        self.assertFalse(os.path.exists(path1))

        # assume only proper file deleted
        path2 = os.path.join(self.path, *id2.split('-')[0:6], 'original.tar.gz')
        self.assertTrue(os.path.exists(path2))

    def test_retrieve_original_to_temp(self):
        """ Retrieving from backend to local temp """
        # put file
        self.prepare_uploads()
        backend = BackendLocal(self.path)
        src = os.path.join(self.upload_path, 'demo-test.tar.gz')
        id = utils.generate_id('demo-test.tar.gz')
        backend.put_original(src, id)

        # retrieve file
        result = backend.retrieve_original(id, self.tmp_path)
        expected_dst = os.path.join(self.tmp_path, id, 'demo-test.tar.gz')
        self.assertEquals(expected_dst, result)
        self.assertTrue(os.path.exists(expected_dst))

    def test_parse_url(self):
        """ Parsing object url into id and filename """
        filename = 'demo-file.tar.gz'
        backend = BackendLocal(self.path)
        pb = PathBuilder('123456')
        base_url = backend.get_url()
        id = utils.generate_id(filename)
        parts = backend.id_to_path(id)
        path = '/'.join(parts)
        object_url = base_url + '/' + path + '/'
        original = object_url + filename
        crop_filename = pb.get_auto_crop_filename(id, '100x100', 'fit')
        resize = object_url + crop_filename
        result1 = backend.parse_url(original)
        result2 = backend.parse_url(resize)
        self.assertEquals(id, result1[0])
        self.assertEquals(filename, result1[1])
        self.assertEquals(id, result2[0])
        self.assertEquals(crop_filename, result2[1])

