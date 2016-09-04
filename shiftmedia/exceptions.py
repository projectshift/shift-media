class MediaException(Exception):
    """ Generic media exception marker """
    pass

class LocalFileNotFound(MediaException, FileNotFoundError):
    """ Raised wen trying to put nonexistent file to storage """
    pass
