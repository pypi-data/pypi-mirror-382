from mosamatic2.core.data.filedata import FileData
from mosamatic2.core.utils import (
    is_nifti,
    load_nifti,
)

class NiftiImage(FileData):
    def load(self):
        if self.path():
            if is_nifti(self.path()):
                self.set_object(load_nifti(self.path()))
                return True
        return False