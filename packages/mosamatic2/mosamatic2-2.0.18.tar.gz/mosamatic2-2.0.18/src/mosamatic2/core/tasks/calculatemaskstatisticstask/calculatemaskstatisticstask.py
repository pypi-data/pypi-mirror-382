import os
import numpy as np
import nibabel as nb
import pandas as pd
import matplotlib.pyplot as plt
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager

LOG = LogManager()


class CalculateMaskStatisticsTask(Task):
    INPUTS = ['scans', 'masks']
    PARAMS = []

    def __init__(self, inputs, params, output, overwrite):
        super(CalculateMaskStatisticsTask, self).__init__(inputs, params, output, overwrite)

    def load_scans(self):
        scans = []
        for f in os.listdir(self.input('scans')):
            if f.endswith('.nii.gz'):
                scan = os.path.join(self.input('scans'), f)
                if os.path.isfile(scan):
                    scans.append(scan)
        return scans

    def load_mask_files(self):
        mask_files = []
        for f in os.listdir(self.input('masks')):
            if f.endswith('.nii.gz'):
                mask_file = os.path.join(self.input('masks'), f)
                if os.path.isfile(mask_file):
                    mask_files.append(mask_file)
        return mask_files
    
    def collect_scan_mask_file_pairs(self, scans, mask_files):
        scan_mask_file_pairs = []
        for scan in scans:
            scan_name = os.path.split(scan)[1][:-7]
            for mask_file in mask_files:
                mask_file_name = os.path.split(mask_file)[1][:-7]
                if scan_name in mask_file_name:
                    scan_mask_file_pairs.append((scan, mask_file))
        return scan_mask_file_pairs
    
    def get_masked_voxels(self, scan_mask_file_pair):
        scan_image_file = scan_mask_file_pair[0]
        scan_image = nb.load(scan_image_file)
        scan_image_data = scan_image.get_fdata()
        mask_file_image_file = scan_mask_file_pair[1]
        mask_file_image_file_name = os.path.split(mask_file_image_file)[1]
        mask_file_image = nb.load(mask_file_image_file)
        mask_file_image_data = mask_file_image.get_fdata()
        mask = mask_file_image_data > 0
        masked_voxels = scan_image_data[mask]
        return masked_voxels, mask_file_image_file_name
    
    def calculate_volume_in_mL(self, mask_file):
        nifti_image = nb.load(mask_file)
        nifti_image_data = nifti_image.get_fdata()
        voxel_dims = nifti_image.header.get_zooms()[:3]
        voxel_volume = np.prod(voxel_dims)
        num_voxels = np.sum(nifti_image_data > 0.5)
        mask_volume = num_voxels * voxel_volume / 1000.0
        return mask_volume
    
    def create_histogram_png(self, masked_voxels, file_name):
        histogram_png_file = os.path.join(self.output(), f'{file_name}.png')
        plt.figure(figsize=(8,6))
        plt.hist(masked_voxels, bins=100, color='steelblue', edgecolor='black')
        plt.title(f'Histogram of HU values inside {file_name}')
        plt.xlabel('HU')
        plt.ylabel('Frequency')
        plt.savefig(histogram_png_file, dpi=300, bbox_inches='tight')
        plt.close()

    def save_data_to_file(self, data):
        csv_file_path = os.path.join(self.output(), 'statistics.csv')
        xls_file_path = os.path.join(self.output(), 'statistics.xlsx')
        df = pd.DataFrame(data=data)
        df.to_csv(csv_file_path, index=False, sep=';')
        df.to_excel(xls_file_path, index=False, engine='openpyxl')

    def run(self):
        scans = self.load_scans()
        mask_files = self.load_mask_files()
        scan_mask_file_pairs = self.collect_scan_mask_file_pairs(scans, mask_files)
        nr_steps = len(scan_mask_file_pairs)
        data = {
            'file': [],
            'mean_HU': [],
            'std_HU': [],
            'volume_mL': [],
        }
        for step in range(nr_steps):
            masked_voxels, file_name = self.get_masked_voxels(scan_mask_file_pairs[step])
            data['file'].append(file_name)
            data['mean_HU'].append(round(np.mean(masked_voxels)))
            data['std_HU'].append(round(np.std(masked_voxels)))
            data['volume_mL'].append(round(self.calculate_volume_in_mL(scan_mask_file_pairs[step][1])))
            self.create_histogram_png(masked_voxels, file_name)
            self.set_progress(step, nr_steps)
        self.save_data_to_file(data)