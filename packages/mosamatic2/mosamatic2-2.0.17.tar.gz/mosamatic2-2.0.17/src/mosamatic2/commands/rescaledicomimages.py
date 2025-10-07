import click

from mosamatic2.core.tasks import RescaleDicomImagesTask


@click.command(help='Rescale DICOM files to target size')
@click.option(
    '--images', 
    required=True, 
    type=click.Path(exists=True), 
    help='Input directory with images'
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--target_size', 
    default=512,
    help='Target size of rescaled images (default: 512)'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite [true|false]'
)
def rescaledicomimages(images, output, target_size, overwrite):
    """
    Rescales DICOM images to given (square) target size

    Parameters
    ----------
    --images : str
        Directory with input DICOM images

    --output : str
        Path to output directory

    --target_size : int
        Target size for rescaled images (default: 512)
    
    --overwrite : bool
        Overwrite contents output directory: [true|false]
    """
    task = RescaleDicomImagesTask(
        inputs={'images': images}, 
        params={'target_size': target_size}, 
        output=output, 
        overwrite=overwrite
    )
    task.run()