import click

from mosamatic2.core.tasks import SegmentMuscleFatL3TensorFlowTask


@click.command(help='Extracts muscle and fat regions from CT images at L3 (uses PyTorch)')
@click.option(
    '--images', 
    required=True, 
    type=click.Path(), 
    help='Input directory with images'
)
@click.option(
    '--model_files', 
    required=True, 
    type=click.Path(), 
    help='Input directory with AI model files'
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--overwrite', 
    default=False, 
    type=click.BOOL, 
    help='Overwrite [true|false]'
)
def segmentmusclefatl3tensorflow(images, model_files, output, overwrite):
    """
    Automatically segments muscle and fat tissue in CT images at L3 level.
    
    Parameters
    ----------
    --images : str
        Directory with input L3 images

    --model_files : str
        Directory with AI model files (model-1.0.zip, contour_model-1.0.zip, params-1.0.json)

    --output : str
        Path to output directory

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    task = SegmentMuscleFatL3TensorFlowTask(
        inputs={'images': images, 'model_files': model_files},
        params={'model_version': 1.0},
        output=output,
        overwrite=overwrite,
    )
    task.run()