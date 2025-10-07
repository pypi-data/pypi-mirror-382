import os
import json
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import is_dicom, load_dicom

LOG = LogManager()


class CreateDicomSummaryTask(Task):
    INPUTS = ['directory']
    PARAMS = []

    def __init__(self, inputs, params, output, overwrite):
        super(CreateDicomSummaryTask, self).__init__(inputs, params, output, overwrite)

    def run(self):
        nr_steps = len(os.listdir(self.input('directory'))) * 2
        LOG.info('Collecting data...')
        data = {}
        step = 0
        for patient_dir_name in os.listdir(self.input('directory')):
            data[patient_dir_name] = {}
            patient_dir_path = os.path.join(self.input('directory'), patient_dir_name)
            for root, dirs, files in os.walk(patient_dir_path):
                for f in files:
                    f_path = os.path.join(root, f)
                    # if is_dicom(f_path):
                    p = load_dicom(f_path, stop_before_pixels=True)
                    if p:
                        series_instance_uid = p.SeriesInstanceUID
                        if not series_instance_uid in data[patient_dir_name].keys():
                            data[patient_dir_name][series_instance_uid] = []
                        data[patient_dir_name][series_instance_uid].append(p)
            self.set_progress(step, nr_steps)
            step += 1
        LOG.info('Building summary...')
        summary = {
            'nr_series_per_patient': {},
        }
        # Calculate nr. of series per patient
        for patient_dir_name in data.keys():
            summary['nr_series_per_patient'][patient_dir_name] = len(data[patient_dir_name].keys())
        # Summarize series data per patient
        for patient_dir_name in data.keys():
            summary[patient_dir_name] = {}
            for series_instance_uid in data[patient_dir_name].keys():
                summary[patient_dir_name][series_instance_uid] = {
                    'nr_images': len(data[patient_dir_name][series_instance_uid]),
                    'modality': data[patient_dir_name][series_instance_uid][0].Modality,
                    'image_type': str(data[patient_dir_name][series_instance_uid][0].ImageType),
                    'rows': data[patient_dir_name][series_instance_uid][0].Rows,
                    'columns': data[patient_dir_name][series_instance_uid][0].Columns,
                    'pixel_spacing': str(data[patient_dir_name][series_instance_uid][0].PixelSpacing),
                    'slice_thickness': data[patient_dir_name][series_instance_uid][0].SliceThickness,
                }
            self.set_progress(step, nr_steps)
            step += 1
        LOG.info('Exporting summary...')
        with open(os.path.join(self.output(), 'summary.txt'), 'w') as f:
            json.dump(summary, f, indent=4)