import os
import dicom2nifti
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import is_dicom

LOG = LogManager()


class Dicom2NiftiTask(Task):
    INPUTS = ['scans']
    PARAMS = ['compressed']

    def __init__(self, inputs, params, output, overwrite):
        super(Dicom2NiftiTask, self).__init__(inputs, params, output, overwrite)

    def load_scan_dirs(self):
        scan_dirs = []
        for d in os.listdir(self.input('scans')):
            scan_dir = os.path.join(self.input('scans'), d)
            if os.path.isdir(scan_dir):
                scan_dirs.append(scan_dir)
        return scan_dirs

    def run(self):
        scan_dirs = self.load_scan_dirs()
        nr_steps = len(scan_dirs)
        for step in range(nr_steps):
            scan_dir = scan_dirs[step]
            scan_name = os.path.split(scan_dir)[1]
            if self.param('compressed'):
                nifti_file_name = scan_name + '.nii.gz'
            else:
                nifti_file_name = scan_name + '.nii'
            LOG.info(f'Converting DICOM series in {scan_dir} to {nifti_file_name}')
            dicom2nifti.dicom_series_to_nifti(
                scan_dir,
                os.path.join(self.output(), nifti_file_name),
                reorient_nifti=True,
            )
            self.set_progress(step, nr_steps)