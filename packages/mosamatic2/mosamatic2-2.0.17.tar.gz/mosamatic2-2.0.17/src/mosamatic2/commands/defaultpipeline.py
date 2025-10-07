import click

from mosamatic2.core.pipelines import DefaultPipeline


@click.command(help='Runs default L3 analysis pipeline')
@click.option(
    '--images', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with L3 images',
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
    type=click.BOOL, 
    default=False, 
    help='Overwrite [true|false]'
)
def defaultpipeline(images, model_files, output, overwrite):
    """
    Runs default L3 analysis pipeline
    
    Parameters
    ----------
    --images : str
        Directory with L3 images

    --model_files : str
        Directory with AI model files. This directory can ONLY contain the following
        files:

        (1) contour_model-1.0.zip
        (2) model-1.0.zip
        (3) params-1.0.json

        These files can be downloaded from:
        https://mosamatic.rbeesoft.nl/wordpress/mosamatic/installation/

    --output : str
        Path to output directory

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    pipeline = DefaultPipeline(
        inputs={'images': images, 'model_files': model_files},
        params={
            'target_size': 512,
            'model_type': 'tensorflow',
            'model_version': 1.0,
            'file_type': 'npy',
            'fig_width': 10,
            'fig_height': 10,
        },
        output=output,
        overwrite=overwrite,
    )
    pipeline.run()