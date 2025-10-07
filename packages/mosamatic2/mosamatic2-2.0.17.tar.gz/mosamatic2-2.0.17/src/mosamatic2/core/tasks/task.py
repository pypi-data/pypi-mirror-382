import os
import shutil
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import create_name_with_timestamp, mosamatic_output_dir

LOG = LogManager()


class Task:
    INPUTS = []
    PARAMS = []
    OUTPUT = 'output'

    def __init__(self, inputs, params, output, overwrite=True):
        self._inputs = inputs
        self._params = params
        self._output = os.path.join(output, self.__class__.__name__.lower())
        self._overwrite = overwrite
        if self._overwrite and os.path.isdir(self._output):
            shutil.rmtree(self._output)
        os.makedirs(self._output, exist_ok=self._overwrite)
        # Check that the inputs match specification and type
        assert isinstance(self._inputs, dict)
        assert len(self._inputs.keys()) == len(self.__class__.INPUTS)
        for k, v in self._inputs.items():
            assert k in self.__class__.INPUTS
            assert isinstance(v, str)
        # Check that param names match specification (if not None)
        if self._params:
            assert len(self._params.keys()) == len(self.__class__.PARAMS)
            for k in self._params.keys():
                assert k in self.__class__.PARAMS

    def input(self, name):
        return self._inputs[name]
    
    def param(self, name):
        return self._params[name]
    
    def output(self):
        return self._output
    
    def overwrite(self):
        return self._overwrite
    
    def set_progress(self, step, nr_steps):
        LOG.info(f'[{self.__class__.__name__}] step {step} from {nr_steps}')
    
    def run(self):
        raise NotImplementedError()