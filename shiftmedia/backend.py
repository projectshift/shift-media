from abc import ABCMeta, abstractmethod


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
    pass


class BackendS3(Backend):
    pass