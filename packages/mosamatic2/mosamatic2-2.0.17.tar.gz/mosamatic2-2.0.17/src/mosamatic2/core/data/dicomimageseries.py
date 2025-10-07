import os
from mosamatic2.core.data.filedata import FileData
from mosamatic2.core.data.dicomimage import DicomImage


class DicomImageSeries(FileData):
    def __init__(self):
        super(DicomImageSeries, self).__init__()
        self._images = []

    def images(self):
        return self._images
    
    def load(self):
        if self.path():
            images = []
            for f in os.listdir(self.path()):
                f_path = os.path.join(self.path(), f)
                image = DicomImage()
                image.set_path(f_path)
                if image.load():
                    images.append(image)
            # Sort DICOM objects by instance number
            self._images = sorted(images, key=lambda image: int(image.object().get('InstanceNumber')))
            return True
        return False