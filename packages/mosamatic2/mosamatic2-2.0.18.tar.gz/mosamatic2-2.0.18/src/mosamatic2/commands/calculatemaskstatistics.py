import click

from mosamatic2.core.tasks import CalculateMaskStatisticsTask


@click.command(help='Calculates segmentation mask statistics')
@click.option(
    '--scans', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with scans in NIFTI format',
)
@click.option(
    '--masks',
    required=True,
    type=click.Path(exists=True), 
    help='Directory with segmentation mask files in NIFTI format',
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
def calculatemaskstatistics(scans, masks, output, overwrite):
    """
    Calculates segmentation mask statistics. The following metrics are calculated:

    (1) Mean radiation attenuation (HU)
    (2) Standard deviation radiation attenuation (HU)
    (3) Segmentation mask volume (mL)
    
    Parameters
    ----------
    --scans : str
        Directory with scans in NIFTI format

    --masks : str
        Directory with segmentation mask files in NIFTI format

    --output : str
        Path to output directory

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    task = CalculateMaskStatisticsTask(
        inputs={'scans': scans, 'masks': masks},
        params=None,
        output=output,
        overwrite=overwrite,
    )
    task.run()