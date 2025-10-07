import argparse
import mosamatic2.constants as constants
from flask import Flask, request
from mosamatic2.core.tasks import RescaleDicomImagesTask
from mosamatic2.core.tasks import SegmentMuscleFatL3TensorFlowTask
from mosamatic2.core.tasks import CalculateScoresTask
from mosamatic2.core.tasks import CreatePngsFromSegmentationsTask
from mosamatic2.core.tasks import Dicom2NiftiTask
from mosamatic2.core.tasks import SelectSliceFromScansTask
from mosamatic2.core.tasks import CreateDicomSummaryTask

app = Flask(__name__)


@app.route('/test')
def run_tests():
    return 'PASSED'


@app.route('/rescaledicomimages')
def run_rescaledicomimages():
    images = request.args.get('images')
    target_size = request.args.get('target_size', default=512, type=int)
    output = request.args.get('output')
    overwrite = request.args.get('overwrite', default=True, type=bool)
    task = RescaleDicomImagesTask(
        inputs={'images': images},
        params={'target_size': target_size},
        output=output,
        overwrite=overwrite,
    )
    task.run()
    return 'PASSED'


@app.route('/segmentmusclefatl3tensorflow')
def run_segmentmusclefatl3tensorflow():
    images = request.args.get('images')
    model_files = request.args.get('model_files')
    output = request.args.get('output')
    overwrite = request.args.get('overwrite', default=True, type=bool)
    task = SegmentMuscleFatL3TensorFlowTask(
        inputs={
            'images': images,
            'model_files': model_files,
        },
        params={'model_version': 1.0},
        output=output,
        overwrite=overwrite,
    )
    task.run()
    return 'PASSED'


@app.route('/calculatescores')
def run_calculatescores():
    images = request.args.get('images')
    segmentations = request.args.get('segmentations')
    file_type = request.args.get('file_type', default='npy', type=str)
    output = request.args.get('output')
    overwrite = request.args.get('overwrite', default=True, type=bool)
    task = CalculateScoresTask(
        inputs={
            'images': images,
            'segmentations': segmentations,
        },
        params={'file_type': file_type},
        output=output,
        overwrite=overwrite,
    )
    task.run()
    return 'PASSED'


@app.route('/createpngsfromsegmentations')
def run_createpngsfromsegmentations():
    segmentations = request.args.get('segmentations')
    fig_width = request.args.get('fig_width', default=10, type=int)
    fig_height = request.args.get('fig_height', default=10, type=int)
    output = request.args.get('output')
    overwrite = request.args.get('overwrite', default=True, type=bool)
    task = CreatePngsFromSegmentationsTask(
        inputs={'segmentations': segmentations},
        params={
            'fig_width': fig_width,
            'fig_height': fig_height,
        },
        output=output,
        overwrite=overwrite,
    )
    task.run()
    return 'PASSED'


@app.route('/dicom2nifti')
def run_dicom2nifti():
    images = request.args.get('images')
    output = request.args.get('output')
    overwrite = request.args.get('overwrite', default=True, type=bool)
    task = Dicom2NiftiTask(
        inputs={'images': images},
        params=None,
        output=output,
        overwrite=overwrite,
    )
    task.run()
    return 'PASSED'


@app.route('/selectslicefromscans')
def run_selectslicefromscans():
    scans = request.args.get('scans')
    vertebra = request.args.get('vertebra')
    output = request.args.get('output')
    overwrite = request.args.get('overwrite', default=True, type=bool)
    task = SelectSliceFromScansTask(
        inputs={'scans': scans},
        params={'vertebra': vertebra},
        output=output,
        overwrite=overwrite,
    )
    task.run()
    return 'PASSED'


@app.route('/createdicomsummary')
def run_createdicomsummary():
    directory = request.args.get('directory')
    output = request.args.get('output')
    overwrite = request.args.get('overwrite', default=True, type=bool)
    task = CreateDicomSummaryTask(
        inputs={'directory': directory},
        params=None,
        output=output,
        overwrite=overwrite,
    )
    task.run()
    return 'PASSED'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=constants.MOSAMATIC2_SERVER_PORT)
    parser.add_argument('--debug', type=bool, default=constants.MOSAMATIC2_SERVER_DEBUG)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=args.debug)