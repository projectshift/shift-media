from abc import ABCMeta, abstractmethod
import os


class Backend(metaclass=ABCMeta):
    """
    Abstract backend
    This defines methods your backend must implement in order to
    work with media storage
    """

    @abstractmethod
    def put(self, local_path, id):
        """
        Put file
        Save local file in storage under given id
        """
        pass

    @abstractmethod
    def retrieve(self, id, local_path):
        """
        Retrieve
        Download file from storage and put to local path
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

    def put(self, local_path, id):
        pass

    def retrieve(self, id, local_path):
        pass

    def delete(self, id):
        pass

    def list(self, path=None):
        pass



class BackendS3(Backend):
    pass