
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