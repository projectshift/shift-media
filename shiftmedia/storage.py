import os
from pathlib import Path
import uuid
from shiftmedia import exceptions as x
from shiftmedia.resizer import Resizer


class Storage:

    def __init__(self, config, backend):
        self.config = config
        self.backend = backend
        self._tmp_path = config.LOCAL_TEMP

    @property
    def tmp(self):
        """
        Get temp path
        Returns path to local temp and creates one if necessary
        """
        if not os.path.exists(self._tmp_path):
            os.makedirs(self._tmp_path)
        return self._tmp_path

    def validate_file(self):
        """
        Validate file
        Checks whether the file is indeed what it pretends to be.
        """
        pass

    def put(self, src, delete_local=True):
        """
        Put local file to storage
        Generates a uuid for the file, tells backend ti put
        local file to storage by that id and removes original.
        """
        id = str(uuid.uuid1())
        self.backend.put(src, id)
        if delete_local:
            os.remove(src)

        return id

    def delete(self, id):
        """
        Delete
        Removes file and all its artifacts from storage by id
        """
        return self.backend.delete(id)


    def clean_cache(self):
        """ Walk each directory in storage and delete resize caches """
        pass

    def resize(self, *args, **kwargs):
        resizer = Resizer
        resizer.resize(*args, **kwargs)



        pass

    def get_resize_url(self, id):
        """ Return storage url of resized file """
        pass

    def get_original_url(self, id):
        """ Return storage url of the original file """
        # get path to original
        # combine with storage url from config
        pass
