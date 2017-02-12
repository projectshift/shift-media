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
    def put_original(self, src, id):
        """
        Put original file to storage
        Does not require a filename as it will be extracted from provided id.
        """
        pass

    @abstractmethod
    def put(self, src, id, filename):
        """
        Put file
        Save local file in storage under given id and filename.
        """
        pass

    @abstractmethod
    def retrieve_original(self, id, local_path):
        """
        Retrieve original
        Download file original from storage and put to local temp path
        """
        pass

    @abstractmethod
    def delete(self, id):
        """
        Delete
        Remove file from storage by id
        """
        pass

    # @abstractmethod
    # def list(self, path=None):
    #     """
    #     List
    #     Returns a list of files in storage under given path
    #     """
    #     pass


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

    def put_original(self, src, id):
        """
        Put original file to storage
        Does not require a filename as it will be extracted from provided id.
        the resulting path will have following structure:
            3c72aedc/ba25/11e6/569/406c8f413974/original-filename.jpg

        :param src: string - path to source file
        :param id: string - generated id
        :return: string - generated id
        """
        filename = '-'.join(id.split('-')[5:])
        return self.put(src, id, filename)

    def put(self, src, id, filename):
        """
        Put file to storage
        Save local file in storage under given id and filename.
        """
        if not os.path.exists(src):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(src))

        parts = id.split('-')[0:5]
        dir = os.path.join(self.path, *parts)
        os.makedirs(dir)
        dst = os.path.join(self.path, *parts, filename)
        shutil.copyfile(src, dst)
        return id

    def delete(self, id):
        """
        Delete
        Remove file from storage by id
        """
        id = str(id)
        path = os.path.join(self.path, *id.split('-')[0:5])
        shutil.rmtree(path)
        return True

    def retrieve_original(self, id, local_path):
        """
        Retrieve original
        Download file from storage and put to local temp path
        """
        filename = '-'.join(id.split('-')[5:])
        src = os.path.join(self.path, *id.split('-')[0:5], filename)
        dst_dir = os.path.join(local_path, '-'.join(id.split('-')[:5]))
        dst = os.path.join(dst_dir, filename)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        shutil.copyfile(src, dst)
        return dst


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
