from unittest import mock, TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_raises

import os
from shiftmedia import BackendLocal, utils, exceptions as x
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('backend', 'local')
class BackendLocalTests(TestCase, LocalStorageTestHelpers):
    """ Local storage backend tests """

    def setUp(self, app=None):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        # self.clean()
        super().tearDown()


    # ------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------

    def test_can_instantiate_backend(self):
        """ Can instantiate backend  """
        backend = BackendLocal(self.path)
        self.assertIsInstance(backend, BackendLocal)

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
        src = os.path.join(uploads, 'test.tar.gz')
        id = utils.generate_id('test.tar.gz')
        backend.put(src, id, 'random.tar.gz')

        # assert directories created
        current = self.path
        for dir in id.split('-')[0:5]:
            current = os.path.join(current, dir)
            self.assertTrue(os.path.exists(current))

        # assert file put
        full_file_path = os.path.join(current, 'random.tar.gz')
        self.assertTrue(os.path.exists(full_file_path))

    def test_put_raises_on_nonexistent_file(self):
        """ Put raises exception if source file does not exist """
        backend = BackendLocal(self.path)
        id = utils.generate_id('test.tar.gz')
        with assert_raises(x.LocalFileNotFound):
            backend.put('nonexistent', id, 'random.tar.gz')

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

        path1 = os.path.join(self.path, *id1.split('-')[0:5], 'original.tar.gz')
        self.assertFalse(os.path.exists(path1))

        # assume only proper file deleted
        path2 = os.path.join(self.path, *id2.split('-')[0:5], 'original.tar.gz')
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
        expected_dst = os.path.join(
            self.tmp_path,
            '-'.join(id.split('-')[0:5]),
            'demo-test.tar.gz'
        )

        self.assertEquals(expected_dst, result)
        self.assertTrue(os.path.exists(expected_dst))






