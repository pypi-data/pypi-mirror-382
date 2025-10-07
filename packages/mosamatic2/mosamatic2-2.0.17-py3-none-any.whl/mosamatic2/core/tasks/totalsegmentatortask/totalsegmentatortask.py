import os
import shutil
import tempfile
from totalsegmentator.python_api import totalsegmentator
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager

LOG = LogManager()
TOTAL_SEGMENTATOR_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'total_segmentator_output')


class TotalSegmentatorTask(Task):
    INPUTS = ['scans']
    PARAMS = ['tasks', 'format']

    def __init__(self, inputs, params, output, overwrite):
        super(TotalSegmentatorTask, self).__init__(inputs, params, output, overwrite)
        LOG.info(f'Using temporary output directory: {TOTAL_SEGMENTATOR_OUTPUT_DIR}')

    def load_scan_dirs(self):
        scan_dirs = []
        for d in os.listdir(self.input('scans')):
            scan_dir = os.path.join(self.input('scans'), d)
            if os.path.isdir(scan_dir):
                scan_dirs.append(scan_dir)
        return scan_dirs
    
    def load_scans(self):
        scans = []
        for f in os.listdir(self.input('scans')):
            if f.endswith('.nii.gz'):
                scan = os.path.join(self.input('scans'), f)
                if os.path.isfile(scan):
                    scans.append(scan)
        return scans
    
    def extract_masks(self, scan_dir_or_file):
        os.makedirs(TOTAL_SEGMENTATOR_OUTPUT_DIR, exist_ok=True)
        tasks = self.param('tasks').split(",") if self.param('tasks') else []
        for task in tasks:
            LOG.info(f'Running task {task}...')
            totalsegmentator(input=scan_dir_or_file, output=TOTAL_SEGMENTATOR_OUTPUT_DIR, task=task)

    def delete_total_segmentator_output(self):
        if os.path.exists(TOTAL_SEGMENTATOR_OUTPUT_DIR):
            shutil.rmtree(TOTAL_SEGMENTATOR_OUTPUT_DIR)

    def run(self):
        if self.param('format') == 'dicom':
            scan_dirs_or_files = self.load_scan_dirs()
        elif self.param('format') == 'nifti':
            scan_dirs_or_files = self.load_scans()
        else:
            LOG.error('Unknown format: {}'.format(self.param('format')))
            return
        nr_steps = len(scan_dirs_or_files)
        for step in range(nr_steps):
            scan_dir_or_file = scan_dirs_or_files[step]
            scan_dir_or_file_name = os.path.split(scan_dir_or_file)[1]
            if self.param('format') == 'nifti':
                scan_dir_or_file_name = scan_dir_or_file_name[:-7]
            try:
                self.extract_masks(scan_dir_or_file)
            except Exception as e:
                LOG.error(f'{scan_dir_or_file}: Could not extract masks [{str(e)}]. Skipping scan...')
            self.set_progress(step, nr_steps)
            LOG.info(f'Copying temporary output to final output directory...')
            for f in os.listdir(TOTAL_SEGMENTATOR_OUTPUT_DIR):
                if f.endswith('.nii') or f.endswith('.nii.gz'):
                    f_path = os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, f)
                    target_file = os.path.join(self.output(), f'{scan_dir_or_file_name}_{f}')
                    shutil.copyfile(f_path, target_file)
                    LOG.info(f'Copied {f} to {target_file}')
            LOG.info('Cleaning up Total Segmentator temporary output...')
            self.delete_total_segmentator_output()