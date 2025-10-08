import os


class FileData:
    def __init__(self):
        self._path = None
        self._name = None
        self._object = None

    def path(self):
        return self._path
    
    def set_path(self, path):
        self._path = path

    def name(self):
        return os.path.split(self.path())[1]
    
    def object(self):
        return self._object
    
    def set_object(self, object):
        self._object = object
    
    def load(self):
        raise NotImplementedError()