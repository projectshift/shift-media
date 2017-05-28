import os, shutil
from config.local import LocalConfig


class TestConfig(LocalConfig):
    """
    Test config
    This is a config file used for testing
    """
    SECRET_KEY = '123456'
    LOCAL_TEMP = os.path.join(
        os.path.realpath(os.path.dirname(__file__) + '/../../'),
        'var',
        'testing',
        'localstorage-tmp'
    )


class LocalStorageTestHelpers():

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
        if not os.path.exists(path):
            os.makedirs(path)
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
        if not os.path.exists(path):
            os.makedirs(path)

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
        dst = self.upload_path
        for path, dirs, files in os.walk(src):
            for file in files:
                file_src = os.path.join(src, file)
                file_dst = file_src.replace(src, dst)
                shutil.copyfile(file_src, file_dst)