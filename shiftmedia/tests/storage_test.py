from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, shutil
from config.local import LocalConfig
from shiftmedia import BackendLocal
from shiftmedia import Storage


@attr('storage')
class StorageTests(TestCase):
    """ Storage service tests """

    def setUp(self, app=None):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        # self.clean()
        super().tearDown()

    @property
    def config(self):
        """ Patches config with test pat hfor temp files """
        config = LocalConfig
        config.LOCAL_TEMP = self.tmp_path
        return config

    @property
    def path(self):
        """
        Get path to local storage
        This represents actual file storage
        """
        root = os.path.realpath(os.path.dirname(__file__) + '/../../')
        path = os.path.join(root, 'var', 'testing', 'localstorage')
        return path

    @property
    def upload_path(self):
        """
        Get path to upload directory
        This is where you put files to be moved to storage
        """
        root = os.path.realpath(os.path.dirname(__file__) + '/../../')
        path = os.path.join(root, 'var', 'testing', 'localstorage-uploaded')
        return path

    @property
    def tmp_path(self):
        """
        Get path to temp downloads directory
        This will be used to temporarily retrieve files in order to create
        resizes.
        """
        root = os.path.realpath(os.path.dirname(__file__) + '/../../')
        path = os.path.join(root, 'var', 'testing', 'localstorage-tmp')
        return path

    def clean(self):
        """ Deletes test directories """
        paths = [self.path, self.upload_path, self.tmp_path]
        for path in paths:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)

    def prepare_uploads(self):
        """
        Prepare uploads
        Simulates files being uploaded to the server by copying test assets
        to upload_pah
        """
        root = os.path.realpath(os.path.dirname(__file__) + '/../../')
        src = os.path.join(root, 'shiftmedia', 'tests', 'test_assets')
        dst = self.tmp_path
        if not os.path.exists(dst):
            os.makedirs(dst)
        for path, dirs, files in os.walk(src):
            for file in files:
                file_src = os.path.join(src, file)
                file_dst = file_src.replace(src, dst)
                shutil.copyfile(file_src, file_dst)

    # ------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------

    def test_instantiate_service(self):
        """ Instantiating storage """
        backend = BackendLocal(self.path)
        storage = Storage(self.config, backend)
        self.assertIsInstance(storage, Storage)

    @attr('uploads')
    def test_uploads(self):
        """ Preparing uploads """
        self.prepare_uploads()

