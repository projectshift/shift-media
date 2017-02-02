import uuid


def normalize_extension(extension):
    """
    Normalize extension
    Converts given extension to canonical format for storage
    :param extension: original extension
    :return: normalized extension
    """
    extension = extension.lower()
    extensions = dict(
        jpg=[
            'jpeg',
            'jpe',
            'jif',
            'jfif',
            'jfi'
            'jp2',
            'j2k',
            'jpx',
            'jpf',
            'jpm'
        ],
        tif=[
            'tiff'
        ],
    )

    for canonical, variants in extensions.items():
        if extension in variants:
            extension = canonical
            break

    return extension


def generate_id(original_format):
    """
    Generate id
    Accepts an original file type and generates id string.
    Id will look like this:
        3c72aedc-ba25-11e6-a569-406c8f413974-jpg

    :param original_format: original file type
    :return: storage id
    """
    extension = normalize_extension(original_format)
    id = str(uuid.uuid1()) + '-' + extension
    return id