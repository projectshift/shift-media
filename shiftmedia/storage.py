import os
from pathlib import Path
import uuid
from shiftmedia import exceptions as x


class Storage:

    def __init__(self, config, backend):
        self.config = config
        self.backend = backend

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
        pass

    def clean_cache(self):
        """ Walk each directory in storage and delete resize caches """
        pass

    def resize(self):
        """
        Resize
        Creates resize from the given parameters
        """
        # todo: create resize definition schema
        pass

    def get_resize_url(self, id):
        """ Return storage url of resized file """
        pass

    def get_original_url(self, id):
        """ Return storage url of the original file """
        # get path to original
        # combine with storage url from config
        pass
