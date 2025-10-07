import os
import zipfile
import tempfile
import numpy as np

import models

from mosamatic2.core.tasks.task import Task
from mosamatic2.core.tasks.segmentmusclefatl3tensorflowtask.paramloader import ParamLoader
from mosamatic2.core.data.multidicomimage import MultiDicomImage
from mosamatic2.core.data.dicomimage import DicomImage
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import (
    normalize_between,
    get_pixels_from_dicom_object,
    convert_labels_to_157,
)

DEVICE = 'cpu'
L3_INDEX = 167
LOG = LogManager()


class SegmentMuscleFatL3TensorFlowTask(Task):
    INPUTS = [
        'images', 
        'model_files'
    ]
    PARAMS = ['model_version']

    def __init__(self, inputs, params, output, overwrite=True):
        super(SegmentMuscleFatL3TensorFlowTask, self).__init__(inputs, params, output, overwrite)

    def load_images(self):        
        image_data = MultiDicomImage()
        image_data.set_path(self.input('images'))
        if image_data.load():
            return image_data
        raise RuntimeError('Could not load images')

    def load_model_files(self):
        model_files = []
        for f in os.listdir(self.input('model_files')):
            f_path = os.path.join(self.input('model_files'), f)
            if f_path.endswith('.zip') or f_path.endswith('.json'):
                model_files.append(f_path)
        if len(model_files) != 3:
            raise RuntimeError(f'Found {len(model_files)} model files. This should be 3!')
        return model_files

    def load_models_and_params(self, model_files, model_version):
        tfLoaded = False
        model, contour_model, params = None, None, None
        for f_path in model_files:
            f_name = os.path.split(f_path)[1]
            if f_name == f'model-{str(model_version)}.zip':
                if not tfLoaded:
                    import tensorflow as tf
                    tfLoaded = True
                with tempfile.TemporaryDirectory() as model_dir_unzipped:
                    os.makedirs(model_dir_unzipped, exist_ok=True)
                    with zipfile.ZipFile(f_path) as zipObj:
                        zipObj.extractall(path=model_dir_unzipped)
                    model = tf.keras.models.load_model(model_dir_unzipped, compile=False)
            elif f_name == f'contour_model-{str(model_version)}.zip':
                if not tfLoaded:
                    import tensorflow as tf
                    tfLoaded = True
                with tempfile.TemporaryDirectory() as contour_model_dir_unzipped:
                    os.makedirs(contour_model_dir_unzipped, exist_ok=True)
                    with zipfile.ZipFile(f_path) as zipObj:
                        zipObj.extractall(path=contour_model_dir_unzipped)
                    contour_model = tf.keras.models.load_model(contour_model_dir_unzipped, compile=False)
            elif f_name == f'params-{model_version}.json':
                params = ParamLoader(f_path)
            else:
                pass
        return model, contour_model, params

    def extract_contour(self, image, contour_model, params):
        ct = np.copy(image)
        ct = normalize_between(ct, params.dict['min_bound_contour'], params.dict['max_bound_contour'])
        img2 = np.expand_dims(ct, 0)
        img2 = np.expand_dims(img2, -1)
        pred = contour_model.predict([img2])
        pred_squeeze = np.squeeze(pred)
        pred_max = pred_squeeze.argmax(axis=-1)
        mask = np.uint8(pred_max)
        return mask

    def segment_muscle_and_fat(self, image, model):
        img2 = np.expand_dims(image, 0)
        img2 = np.expand_dims(img2, -1)
        pred = model.predict([img2])
        pred_squeeze = np.squeeze(pred)
        pred_max = pred_squeeze.argmax(axis=-1)
        return pred_max
        
    def process_file(self, image, output_dir, model, contour_model, params):
        assert isinstance(image, DicomImage)
        pixels = get_pixels_from_dicom_object(image.object(), normalize=True)
        if contour_model:
            mask = self.extract_contour(pixels, contour_model, params)
            pixels = normalize_between(pixels, params.dict['min_bound'], params.dict['max_bound'])
            pixels = pixels * mask
        pixels = pixels.astype(np.float32)
        segmentation = self.segment_muscle_and_fat(pixels, model)
        segmentation = convert_labels_to_157(segmentation)
        segmentation_file_name = os.path.split(image.path())[1]
        segmentation_file_path = os.path.join(output_dir, f'{segmentation_file_name}.seg.npy')
        np.save(segmentation_file_path, segmentation)

    def run(self):
        image_data = self.load_images()
        model_files = self.load_model_files()
        model_version = self.param('model_version')
        model, contour_model, params = self.load_models_and_params(model_files, model_version)
        images = image_data.images()
        nr_steps = len(images)
        for step in range(nr_steps):
            self.process_file(images[step], self.output(), model, contour_model, params)
            self.set_progress(step, nr_steps)