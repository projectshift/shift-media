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
        # self.clean()
        super().tearDown()


    # ------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------

    def test_instantiate_storage(self):
        """ Instantiating storage """
        backend = BackendLocal(self.path)
        storage = Storage(self.config, backend)
        self.assertIsInstance(storage, Storage)

    @attr('xxx')
    def test_put_file(self):
        """ Put uploaded file to storage """
        self.prepare_uploads()
        backend = BackendLocal(self.path)
        storage = Storage(self.config, backend)
        uploads = self.upload_path
        src = os.path.join(uploads, 'test.tar.gz')
        storage.put(src)





