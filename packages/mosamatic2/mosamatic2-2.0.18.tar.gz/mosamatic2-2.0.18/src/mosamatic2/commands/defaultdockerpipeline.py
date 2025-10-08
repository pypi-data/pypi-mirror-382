import click

from mosamatic2.core.pipelines import DefaultDockerPipeline


@click.command(help='Runs default L3 analysis pipeline through Docker')
@click.option(
    '--images', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with L3 images (no spaces allowed)',
)
@click.option(
    '--model_files', 
    required=True, 
    type=click.Path(), 
    help='Input directory with AI model files (no spaces allowed)'
)
@click.option(
    '--version', 
    required=True, 
    help='Docker image version'
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory (no spaces allowed)'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite [true|false]'
)
def defaultdockerpipeline(images, model_files, version, output, overwrite):
    """
    Runs default L3 analysis pipeline through Docker
    
    Parameters
    ----------
    --images : str
        Directory with L3 images. Warning: This directory path cannot contain any spaces!
        Docker has issues working with that.

    --model_files : str
        Directory with AI model files. This directory can ONLY contain the following
        files:

        (1) contour_model-1.0.zip
        (2) model-1.0.zip
        (3) params-1.0.json

        These files can be downloaded from:
        https://mosamatic.rbeesoft.nl/wordpress/mosamatic/installation/

        Warning: This directory path cannot contain any spaces!

    --version : str
        Docker image version, e.g., 2.0.16
        Check https://hub.docker.com/repository/docker/brecheisen/mosamatic2-cli/general
        for the latest version and older versions.

    --output : str
        Path to output directory (no spaces!)

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    pipeline = DefaultDockerPipeline(
        inputs={'images': images, 'model_files': model_files},
        params={
            'target_size': 512,
            'model_type': 'tensorflow',
            'model_version': 1.0,
            'file_type': 'npy',
            'fig_width': 10,
            'fig_height': 10,
            'version': version,
        },
        output=output,
        overwrite=overwrite,
    )
    pipeline.run()