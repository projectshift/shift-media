import os
from pathlib import Path

from shiftmedia import exceptions as x
from shiftmedia import utils


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

        if not os.path.exists(src):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(src))

        extension = ''.join(Path(src).suffixes)[1:]
        filename = 'original.' + extension
        id = utils.generate_id(extension)
        self.backend.put(src, id, filename)
        if delete_local:
            os.remove(src)
        return id

    def delete(self, id):
        """
        Delete
        Removes file and all its artifacts from storage by id
        """
        return self.backend.delete(id)



