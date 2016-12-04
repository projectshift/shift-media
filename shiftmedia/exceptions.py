class MediaException(Exception):
    """ Generic media exception marker """
    pass


class LocalFileNotFound(MediaException, FileNotFoundError):
    """ Raised wen trying to put nonexistent file to storage """
    pass


class InvalidResizeFormat(MediaException, NameError):
    """
    Invalid resize format
    Raised when requested resize filename can't be parsed into a set
    of parameters. It means that either it is malformed or signature is wrong.
    """
    pass
