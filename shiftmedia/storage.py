import os
from pathlib import Path
from shiftmedia import Id, exceptions as x

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

    def put(self, src):
        """
        Put local file to storage
        Generates a uuid for the file, creates directory
        in storage and uploads file as original. Returns url
        of the stored file on success.
        """
        local_path = Path(src)
        extension = ''.join(local_path.suffixes)
        id = Id()
        dst = os.path.join(id.get_storage_path(), 'original' + extension)
        self.backend.put(src, dst)



    def delete(self, url):
        pass

    def resize(self):
        pass

    def clean_cache(self):
        """ Walk each directory in storage and delete resize caches """
        pass

    def get_resize_url(self, id):
        """ Return storage url of resized file """
        pass

    def get_original_url(self, id):
        """ Return storage url of the original file """
        pass
