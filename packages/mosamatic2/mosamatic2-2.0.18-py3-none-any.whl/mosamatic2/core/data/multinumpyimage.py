import os
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.data.filedata import FileData
from mosamatic2.core.data.numpyimage import NumpyImage

LOG = LogManager()


class MultiNumpyImage(FileData):
    def __init__(self):
        super(MultiNumpyImage, self).__init__()
        self._images = []

    def images(self):
        return self._images
    
    def load(self):
        if self.path():
            for f in os.listdir(self.path()):
                f_path = os.path.join(self.path(), f)
                image = NumpyImage()
                image.set_path(f_path)
                if image.load():
                    self._images.append(image)
            return True
        return False