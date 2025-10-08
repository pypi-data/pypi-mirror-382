import os
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.data.filedata import FileData
from mosamatic2.core.data.dicomimage import DicomImage

LOG = LogManager()


class MultiDicomImage(FileData):
    def __init__(self):
        super(MultiDicomImage, self).__init__()
        self._images = []

    def images(self):
        return self._images
    
    def load(self):
        series_instance_uids = []
        if self.path():
            for f in os.listdir(self.path()):
                f_path = os.path.join(self.path(), f)
                image = DicomImage()
                image.set_path(f_path)
                if image.load():
                    series_instance_uid = image.object().SeriesInstanceUID
                    if series_instance_uid in series_instance_uids:
                        RuntimeError('Cannot load DICOM images with identical series instance UID')
                    self._images.append(image)
            return True
        return False