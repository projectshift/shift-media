from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, shutil
from config.local import LocalConfig
from shiftmedia import BackendLocal


@attr('backend', 'local')
class BackendLocalTests(TestCase):
    """ Media item entity tests """

    def setUp(self, app=None):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        self.clean()
        super().tearDown()

    @property
    def path(self):
        """ Get path to local storage """
        root = os.path.realpath(os.path.dirname(__file__) + '/../../')
        path = os.path.join(root, 'var', 'testing', 'localstorage')
        return path

    def clean(self):
        """ Deletes local storage directory """
        if os.path.exists(self.path):
            shutil.rmtree(self.path, ignore_errors=True)



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
        self.assertTrue(os.path.exists(self.path))



