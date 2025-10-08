import os
import math
import tempfile
import shutil
import nibabel as nib
import numpy as np
from totalsegmentator.python_api import totalsegmentator
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import load_dicom

LOG = LogManager()

TOTAL_SEGMENTATOR_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'total_segmentator_output')
TOTAL_SEGMENTATOR_TASK = 'total'
Z_DELTA_OFFSETS = {
    'vertebrae_L3': 0.333,
    'vertebrae_T4': 0.5,
}


class SelectSliceFromScansTask(Task):
    INPUTS = ['scans']
    PARAMS = ['vertebra']

    def __init__(self, inputs, params, output, overwrite):
        super(SelectSliceFromScansTask, self).__init__(inputs, params, output, overwrite)
        self._error_dir = os.path.split(self.output())[0]
        self._error_dir = os.path.join(self._error_dir, 'selectslicefromscanstask_errors')
        os.makedirs(self._error_dir, exist_ok=True)
        self._error_file = os.path.join(self._error_dir, 'errors.txt')
        with open(self._error_file, 'w') as f:
            f.write('Errors:\n\n')
        LOG.info(f'Error directory: {self._error_dir}')

    def write_error(self, message):
        LOG.error(message)
        with open(self._error_file, 'a') as f:
            f.write(message + '\n')

    def load_scan_dirs(self):
        scan_dirs = []
        for d in os.listdir(self.input('scans')):
            scan_dir = os.path.join(self.input('scans'), d)
            if os.path.isdir(scan_dir):
                scan_dirs.append(scan_dir)
        return scan_dirs
    
    def extract_masks(self, scan_dir):
        os.makedirs(TOTAL_SEGMENTATOR_OUTPUT_DIR, exist_ok=True)
        totalsegmentator(input=scan_dir, output=TOTAL_SEGMENTATOR_OUTPUT_DIR, fast=True)
        if not os.path.isfile(os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, 'vertebrae_L3.nii.gz')):
            raise Exception(f'{scan_dir}: vertebrae_L3.nii.gz does not exist')
        # os.system(f'TotalSegmentator -i {scan_dir} -o {TOTAL_SEGMENTATOR_OUTPUT_DIR} --fast')

    def delete_total_segmentator_output(self):
        if os.path.exists(TOTAL_SEGMENTATOR_OUTPUT_DIR):
            shutil.rmtree(TOTAL_SEGMENTATOR_OUTPUT_DIR)

    def get_z_delta_offset_for_mask(self, mask_name):
        if mask_name not in Z_DELTA_OFFSETS.keys():
            return None
        return Z_DELTA_OFFSETS[mask_name]

    def find_slice(self, scan_dir, vertebra):
        if vertebra == 'L3':
            vertebral_level = 'vertebrae_L3'
        elif vertebra == 'T4':
            vertebral_level = 'vertebrae_T4'
        else:
            self.write_error(f'{scan_dir}: Unknown vertbra {vertebra}. Options are "L3" and "T4"')
            return None
        # Find Z-positions DICOM images
        z_positions = {}
        for f in os.listdir(scan_dir):
            f_path = os.path.join(scan_dir, f)
            try:
                p = load_dicom(f_path, stop_before_pixels=True)
                if p is not None and hasattr(p, "ImagePositionPatient"):
                    z_positions[p.ImagePositionPatient[2]] = f_path
            except Exception as e:
                self.write_error(f"{scan_dir}: Failed to load DICOM {f_path}: {e}")
                break
        if not z_positions:
            self.write_error(f"{scan_dir}: No valid DICOM z-positions found.")
            return None
        # Find Z-position L3 image
        mask_file = os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, f'{vertebral_level}.nii.gz')
        if not os.path.exists(mask_file):
            self.write_error(f"{scan_dir}: Mask file not found: {mask_file}")
            return None
        try:
            mask_obj = nib.load(mask_file)
            mask = mask_obj.get_fdata()
            affine_transform = mask_obj.affine
        except Exception as e:
            self.write_error(f"{scan_dir}: Failed to load mask {mask_file}: {e}")
            return None
        indexes = np.array(np.where(mask == 1))
        if indexes.size == 0:
            self.write_error(f"{scan_dir}: No voxels found in mask {mask_file} for {vertebral_level}")
            return None        
        try:
            index_min = indexes.min(axis=1)
            index_max = indexes.max(axis=1)
        except ValueError as e:
            self.write_error(f"{scan_dir}: Invalid indexes array for {vertebral_level}: {e}")
            return None
        world_min = nib.affines.apply_affine(affine_transform, index_min)
        world_max = nib.affines.apply_affine(affine_transform, index_max)
        z_direction = affine_transform[:3, 2][2]
        if z_direction == 0:
            self.write_error(f"{scan_dir}: Affine z-direction is zero.")
            return None
        z_sign = math.copysign(1, z_direction)
        z_delta_offset = self.get_z_delta_offset_for_mask(vertebral_level)
        if z_delta_offset is None:
            return None
        z_delta = 0.333 * abs(world_max[2] - world_min[2]) # This needs to be vertebra-specific perhaps
        z_l3 = world_max[2] - z_sign * z_delta
        # Find closest L3 image in DICOM set
        positions = sorted(z_positions.keys())
        closest_file = None
        for z1, z2 in zip(positions[:-1], positions[1:]):
            if min(z1, z2) <= z_l3 <= max(z1, z2):
                closest_z = min(z_positions.keys(), key=lambda z: abs(z - z_l3))
                closest_file = z_positions[closest_z]
                LOG.info(f'Closest image: {closest_file}')
                break
        if closest_file is None:
            self.write_error(f"{scan_dir}: No matching slice found.")
        return closest_file

    def run(self):
        scan_dirs = self.load_scan_dirs()
        vertebra = self.param('vertebra')
        nr_steps = len(scan_dirs)
        for step in range(nr_steps):
            scan_dir = scan_dirs[step]
            scan_name = os.path.split(scan_dir)[1]
            errors = False
            LOG.info(f'Processing {scan_dir}...')
            try:
                self.extract_masks(scan_dir)
            except Exception as e:
                self.write_error(f'{scan_dir}: Could not extract masks [{str(e)}]. Skipping scan...')
                errors = True
            if not errors:
                file_path = self.find_slice(scan_dir, vertebra)
                if file_path is not None:
                    extension = '' if file_path.endswith('.dcm') else '.dcm'
                    target_file_path = os.path.join(self.output(), vertebra + '_' + scan_name + extension)
                    shutil.copyfile(file_path, target_file_path)
                else:
                    self.write_error(f'{scan_dir}: Could not find slice for vertebral level: {vertebra}')
                    errors = True
                self.delete_total_segmentator_output()
            if errors:
                LOG.info(f'Copying problematic scan {scan_dir} to error directory: {self._error_dir}')
                scan_error_dir = os.path.join(self._error_dir, scan_name)
                shutil.copytree(scan_dir, scan_error_dir)
            self.set_progress(step, nr_steps)