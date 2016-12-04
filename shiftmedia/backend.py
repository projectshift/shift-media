import os, shutil
from abc import ABCMeta, abstractmethod
from shiftmedia import exceptions as x
from pathlib import Path


class Backend(metaclass=ABCMeta):
    """
    Abstract backend
    This defines methods your backend must implement in order to
    work with media storage
    """

    @abstractmethod
    def put(self, local_path, id, filename='original'):
        """
        Put file
        Save local file in storage under given id. Can put both originals
        and resizes.
        """
        pass

    @abstractmethod
    def retrieve(self, id, local_path):
        """
        Retrieve
        Download file from storage and put to local temp path
        """
        pass

    @abstractmethod
    def delete(self, id):
        """
        Delete
        Remove file from storage by id
        """
        pass

    @abstractmethod
    def list(self, path=None):
        """
        List
        Returns a list of files in storage under given path
        """
        pass


class BackendLocal(Backend):
    """
    Local backend
    Stores file locally in a directory without transferring to remote storage
    """
    def __init__(self, local_path):
        self._path = local_path

    @property
    def path(self):
        """
        Get path
        Returns path to local storage and creates one if necessary
        """
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        return self._path

    def put(self, local_path, id, filename='original'):
        """
        Save local file in storage under given id. Can put both originals
        and resizes.
        """
        if not os.path.exists(local_path):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(local_path))

        extension = ''.join(Path(local_path).suffixes)
        parts = id.split('-')
        dir = os.path.join(self.path, *parts)
        os.makedirs(dir)

        dst = os.path.join(self.path, *parts, filename + extension)
        shutil.copyfile(local_path, dst)
        return id

    def delete(self, id):
        """
        Delete
        Remove file from storage by id
        """
        id = str(id)
        path = os.path.join(self.path, id.split('-')[0])
        shutil.rmtree(path)
        return True

    def retrieve(self, id, local_path):
        """
        Retrieve
        Download file from storage and put to local temp path
        """
        id = str(id)
        path = os.path.join(self.path, *id.split('-'))

        files = [item for item in os.scandir(path) if item.is_file()]
        for file in files:
            if not file.name.startswith('original.'):
                continue

            src = file.path
            dst_dir = os.path.join(local_path, id)
            dst = os.path.join(dst_dir, file.name)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            shutil.copyfile(src, dst)
            return dst


    def list(self, path=None):
        pass



class BackendS3(Backend):

    # @attr('boto')
    # def test_can_boto(self):
    #     """ Can list S3 buckets with boto """
    #     s3 = boto3.resource('s3', **self.get_config())
    #     for bucket in s3.buckets.all():
    #         print(bucket.name)
    #
    #     print(list(s3.buckets.all()))
    #
    # @attr('boto')
    # def test_can_upload_to_s3(self):
    #     """ Can upload stuff to s3 """
    #     filename = 'test.jpg'
    #     path = os.path.realpath(os.path.dirname(__file__))
    #     path = os.path.join(path, 'test_assets', filename)
    #
    #     s3 = boto3.resource('s3', **self.get_config())
    #     bucket = s3.Bucket(LocalConfig.AWS_S3_BUCKET)
    #
    #     with open(path, 'rb') as data:
    #         result = bucket.put_object(Key='my_example_file.jpg', Body=data)
    #         print('RESULT', result)
    pass
