import os
from mosamatic2.core.pipelines.pipeline import Pipeline
from mosamatic2.core.tasks import Dicom2NiftiTask
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import (
    is_docker_running, 
    to_unix_path,
    current_time_in_seconds,
    elapsed_time_in_seconds,
    duration,
)

LOG = LogManager()


class BoaDockerPipeline(Pipeline):
    INPUTS = ['scans']
    PARAMS = []

    def __init__(self, inputs, params, output, overwrite):
        super(BoaDockerPipeline, self).__init__(inputs, params, output, overwrite)

    def load_nifti_files(self):
        nifti_files_dir = os.path.join(self.output(), 'dicom2niftitask')
        nifti_files = []
        for f in os.listdir(nifti_files_dir):
            f_path = os.path.join(nifti_files_dir, f)
            if f.endswith('.nii') or f.endswith('.nii.gz'):
                nifti_files.append(f_path)
        return nifti_files

    def run(self):
        assert is_docker_running()
        # First convert DICOM series to NIFTI format
        dicom2nifti_task = Dicom2NiftiTask(
            inputs={'scans': self.input('scans')},
            params={'compressed': True},
            output=self.output(),
            overwrite=self.overwrite(),
        )
        dicom2nifti_task.run()
        # Load NIFTI file paths
        nifti_files = self.load_nifti_files()
        workspaces_dir = to_unix_path(os.path.join(self.output(), 'workspaces'))
        os.makedirs(workspaces_dir, exist_ok=True)
        weights_dir = to_unix_path(os.path.join(self.output(), 'weights'))
        start_time = current_time_in_seconds()
        for f in nifti_files:
            start_time_f = current_time_in_seconds()
            f = to_unix_path(f)
            dir_name = os.path.split(f)[1][:-7]
            workspace = to_unix_path(os.path.join(workspaces_dir, dir_name))
            # Build Docker script
            docker_script = 'docker run --rm ' + \
                '-v "{}":/image.nii.gz '.format(f) + \
                '-v "{}":/workspace '.format(workspace) + \
                '-v "{}":/app/weights '.format(weights_dir) + \
                '--gpus all ' + \
                '--network host ' + \
                '--shm-size=8g --ulimit memlock=-1 --ulimit stack=67108864 ' + \
                '--entrypoint /bin/sh ' + \
                'shipai/boa-cli -c ' + \
                '"python body_organ_analysis --input-image /image.nii.gz --output-dir /workspace/ --models all --verbose"'
            LOG.info(f'Running BOA Docker script: {docker_script}')
            # Run Docker script
            os.system(docker_script)
            elapsed_f = elapsed_time_in_seconds(start_time_f)
            LOG.info(f'Elapsed {dir_name}: {duration(elapsed_f)}')
        elapsed_total = elapsed_time_in_seconds(start_time)
        LOG.info(f'Elapsed total: {duration(elapsed_total)}')