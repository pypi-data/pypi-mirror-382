import os
from mosamatic2.core.pipelines.pipeline import Pipeline
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import is_docker_running, to_unix_path

LOG = LogManager()


class DefaultDockerPipeline(Pipeline):
    INPUTS = [
        'images',
        'model_files',
    ]
    PARAMS = ['version']
    
    def __init__(self, inputs, params, output, overwrite):
        super(DefaultDockerPipeline, self).__init__(inputs, params, output, overwrite)

    def run(self):
        assert is_docker_running()
        docker_script = 'docker run --rm ' + \
            '-v "{}":/data/images '.format(to_unix_path(self.input('images'))) + \
            '-v "{}":/data/model_files '.format(to_unix_path(self.input('model_files'))) + \
            '-v "{}":/data/output '.format(to_unix_path(self.output())) + \
            'brecheisen/mosamatic2-cli:{} defaultpipeline '.format(self.param('version')) + \
            '--images /data/images --model_files /data/model_files --output /data/output --overwrite true'
        LOG.info(f'Running Docker script: {docker_script}')
        os.system(docker_script)