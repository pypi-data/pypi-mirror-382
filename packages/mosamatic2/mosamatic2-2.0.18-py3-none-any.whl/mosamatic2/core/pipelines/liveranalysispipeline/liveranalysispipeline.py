import os
from mosamatic2.core.pipelines.pipeline import Pipeline
from mosamatic2.core.tasks import (
    Dicom2NiftiTask,
    TotalSegmentatorTask,
    CalculateMaskStatisticsTask,
)
from mosamatic2.core.managers.logmanager import LogManager

LOG = LogManager()


class LiverAnalysisPipeline(Pipeline):
    INPUTS = ['scans']
    PARAMS = ['compressed']

    def __init__(self, inputs, params, output, overwrite):
        super(LiverAnalysisPipeline, self).__init__(inputs, params, output, overwrite)
        self.add_task(
            Dicom2NiftiTask(
                inputs={'scans': self.input('scans')},
                params={'compressed': self.param('compressed')},
                output=self.output(),
                overwrite=self.overwrite(),
            )
        )
        self.add_task(
            TotalSegmentatorTask(
                inputs={'scans': os.path.join(self.output(), 'dicom2niftitask')},
                params={
                    'tasks': 'liver_segments', 
                    'format': 'nifti',
                },
                output=self.output(),
                overwrite=self.overwrite(),
            )
        )
        self.add_task(
            CalculateMaskStatisticsTask(
                inputs={
                    'scans': os.path.join(self.output(), 'dicom2niftitask'),
                    'masks': os.path.join(self.output(), 'totalsegmentatortask'),
                },
                params=None,
                output=self.output(),
                overwrite=self.overwrite(),
            )
        )