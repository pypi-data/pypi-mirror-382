from mosamatic2.core.data.filedata import FileData
from mosamatic2.core.utils import (
    is_numpy,
    load_numpy_array,
)

class NumpyImage(FileData):
    def load(self):
        if self.path():
            if is_numpy(self.path()):
                self.set_object(load_numpy_array(self.path()))
                return True
        return False