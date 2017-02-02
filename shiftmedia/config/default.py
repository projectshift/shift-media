
class DefaultConfig():
    """
    Default media storage config
    This contains all possible configuration values and sensible defaults.
    Extend this class with your own local config class and override required
    settings, for example security credentials.
    """
    AWS_IAM_KEY_ID = None
    AWS_IAM_ACCESS_SECRET = None
    AWS_S3_BUCKET = None
    BASE_STORAGE_URL = None
    LOCAL_TEMP = None

    SECRET_KEY = 'PleaseDefineSecretKey'