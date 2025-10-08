from mosamatic2.core.data.filedata import FileData
from mosamatic2.core.utils import (
    is_dicom,
    load_dicom,
    is_jpeg2000_compressed,
)
from mosamatic2.core.managers.logmanager import LogManager

LOG = LogManager()


class DicomImage(FileData):
    def load(self):
        if self.path():
            p = load_dicom(self.path())
            if p:
                if is_jpeg2000_compressed(p):
                    p.decompress()
                self.set_object(p)
                return True
            # if is_dicom(self.path()):
            #     p = load_dicom(self.path())
            #     if is_jpeg2000_compressed(p):
            #         p.decompress()
            #     self.set_object(p)
            #     return True
        return False