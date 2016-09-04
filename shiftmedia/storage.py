class Storage:

    def __init__(self, config, backend):
        self.config = config
        self.backend = backend

    def validate_file(self):
        pass

    def put(self, local_path):
        """
        Put local file to storage
        
        """
        pass

    def delete(self):
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
