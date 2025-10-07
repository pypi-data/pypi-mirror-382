import click

from mosamatic2.core.pipelines import BoaDockerPipeline


@click.command(help='Runs 3D body composition analysis pipeline using BOA algorithm')
@click.option(
    '--scans', 
    required=True, 
    type=click.Path(exists=True), 
    help='Root directory with scan directories for each patient (no spaces allowed)',
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
def boadockerpipeline(scans, output, overwrite):
    """
    Runs 3D body composition analysis pipeline using BOA algorithm.
    
    Parameters
    ----------
    --scans : str
        Root directory with scan directories for each patient. Each scan directory should 
        contain DICOM images for a single scan only and nothing else. Also, the directory
        paths cannot contain any spaces.

    --output : str
        Path to output directory. No spaces allowed.

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    pipeline = BoaDockerPipeline(
        inputs={'scans': scans},
        params=None,
        output=output,
        overwrite=overwrite,
    )
    pipeline.run()