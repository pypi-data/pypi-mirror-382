import click

from mosamatic2.core.tasks import CalculateScoresTask


@click.command(help='Calculates body composition scores')
@click.option(
    '--images', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with images',
)
@click.option(
    '--segmentations',
    required=True,
    type=click.Path(exists=True), 
    help='Directory with segmentations',
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--file_type',
    default='npy',
    help='Options: [npy, tag]'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite [true|false]'
)
def calculatescores(images, segmentations, output, file_type, overwrite):
    """
    Calculates the following body composition metrics from the muscle and fat 
    images and segmentation files:

    (1) Muscle area (cm^2)
    (2) Mean muscle radiation attenuation (HU)
    (3) Subcutaneous fat area (cm^2)
    (4) Mean subcutaneous fat radiation attenuation (HU)
    (5) Visceral fat area (cm^2)
    (6) Mean visceral fat radiation attenuation (HU)
    
    Parameters
    ----------
    --images : str
        Directory with input L3 images

    --segmentations : str
        Directory with L3 muscle and fat segmenation files. Must be output of 
        "mosamatic2-cli segmentmusclefatl3tensorflow" OR a list of TAG files
        corresponding to the input images

    --output : str
        Path to output directory

    --file_type : str
        Type of segmentation file to use. Can be either "npy" or "tag"
    
    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    task = CalculateScoresTask(
        inputs={'images': images, 'segmentations': segmentations},
        params={'file_type': file_type},
        output=output,
        overwrite=overwrite,
    )
    task.run()