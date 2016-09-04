import uuid, os


class Id:
    """
    Media item id
    Used to generate unique object id whithin the sorage
    """

    def __init__(self):
        """ initialize the item """
        self.id = uuid.uuid1()

    def __str__(self):
        """ Returns string representation of id """
        return str(self.id)

    def get_storage_path(self, as_list=False):
        """ Returns storage path """
        path = str(self.id).split('-')
        if as_list:
            return path
        return os.path.join(*path)




