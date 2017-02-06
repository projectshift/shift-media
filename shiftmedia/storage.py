import os
from pathlib import Path

from shiftmedia import exceptions as x
from shiftmedia import utils

# TODO: how to force file download?
# TODO: how to serve original filename?
# TODO: files for storage as is vs. file for processing

# USE CASE: we might want file stored under its original name, i.e. cv.pdf

# TODO: make original filename part of the ID?
# TODO: 3c72aedc-ba25-11e6-a569-406c8f413974-original_filename.jpg
# TODO: how do we transform such an id to original url?




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

    def put(self, src, delete_local=True):
        """
        Put local file to storage
        Generates a uuid for the file, tells backend to accept
        it by that id and removes original on success.
        """

        # todo: validate file before put
        # todo: get real file extension to generate id with

        # todo: whos responsibility it is to get file extension?
        # todo: is it storage?

        if not os.path.exists(src):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(src))

        path = Path(src)
        extension = ''.join(path.suffixes)[1:]
        name = path.name.replace('.' + extension, '')
        extension = utils.normalize_extension(extension)
        filename = name + '.' + extension
        id = utils.generate_id(filename)
        self.backend.put(src, id)
        if delete_local: os.remove(src)
        return id

    def delete(self, id):
        """
        Delete
        Removes file and all its artifacts from storage by id
        """
        return self.backend.delete(id)



