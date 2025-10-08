import os

from mosamatic2.core.pipelines.pipeline import Pipeline
from mosamatic2.core.tasks import (
    RescaleDicomImagesTask, 
    SegmentMuscleFatL3TensorFlowTask,
    SegmentMuscleFatL3TensorFlowTask,
    CreatePngsFromSegmentationsTask,
    CalculateScoresTask,
)
from mosamatic2.core.managers.logmanager import LogManager

LOG = LogManager()


class DefaultPipeline(Pipeline):
    INPUTS = [
        'images',
        'model_files',
    ]
    PARAMS = [
        'target_size',
        'file_type',
        'fig_width',
        'fig_height',
        'model_type',
        'model_version',
    ]
    def __init__(self, inputs, params, output, overwrite):
        super(DefaultPipeline, self).__init__(inputs, params, output, overwrite)
        LOG.info('Found {} images to process'.format(len(os.listdir(self.input('images')))))
        model_type = self.param('model_type')
        # segmentation_task_class = SegmentMuscleFatL3Task if model_type == 'pytorch' else SegmentMuscleFatL3TensorFlowTask
        segmentation_task_class = SegmentMuscleFatL3TensorFlowTask
        self.add_task(
            RescaleDicomImagesTask(
                inputs={'images': self.input('images')},
                params={'target_size': self.param('target_size')},
                output=self.output(),
                overwrite=self.overwrite(),
            )
        )
        self.add_task(
            segmentation_task_class(
                inputs={
                    'images': os.path.join(self.output(), 'rescaledicomimagestask'),
                    'model_files': self.input('model_files'),
                },
                params={'model_version': self.param('model_version')},
                output=self.output(),
                overwrite=self.overwrite(),
            )
        )
        self.add_task(
            CalculateScoresTask(
                inputs={
                    'images': os.path.join(self.output(), 'rescaledicomimagestask'),
                    'segmentations': os.path.join(
                        self.output(),
                        'segmentmusclefatl3pytorchtask' if model_type == 'pytorch' else 'segmentmusclefatl3tensorflowtask',
                    )
                },
                params={'file_type': self.param('file_type')},
                output=self.output(),
                overwrite=self.overwrite(),
            )
        )
        self.add_task(
            CreatePngsFromSegmentationsTask(
                inputs={
                    'segmentations': os.path.join(
                        self.output(),
                        'segmentmusclefatl3pytorchtask' if model_type == 'pytorch' else 'segmentmusclefatl3tensorflowtask',
                    )
                },
                params={
                    'fig_width': self.param('fig_width'),
                    'fig_height': self.param('fig_height'),
                },
                output=self.output(),
                overwrite=self.overwrite(),
            )
        )