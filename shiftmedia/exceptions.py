class MediaException(Exception):
    """ Generic media exception marker """
    pass


class InvalidArgumentException(MediaException, ValueError):
    """ Raised when there is an invalid argument supplied """
    pass


class ConfigurationException(MediaException, ValueError):
    """ Raised when there is something wrong with configuration """
    pass


class LocalFileNotFound(MediaException, FileNotFoundError):
    """ Raised when trying to put nonexistent file to storage """
    pass


class FileExists(MediaException, FileExistsError):
    """ Raised when trying to overwrite existing file """
    pass


class NotImplementedError(MediaException, Exception):
    """ Raised when something is not there yet """
    pass


class S3Error(MediaException, NameError):
    """
    S3 Error
    Raised when something goes wrong during S3 operation
    """
    pass

class InvalidResizeFormat(MediaException, NameError):
    """
    Invalid resize format
    Raised when requested resize filename can't be parsed into a set
    of parameters. It means that either it is malformed or signature is wrong.
    """
    pass
