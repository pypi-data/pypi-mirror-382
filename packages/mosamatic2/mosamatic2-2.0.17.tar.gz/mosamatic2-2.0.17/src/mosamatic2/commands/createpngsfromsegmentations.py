import click

from mosamatic2.core.tasks import CreatePngsFromSegmentationsTask


@click.command(help='Create PNG images from segmentation files')
@click.option(
    '--segmentations', 
    required=True, 
    type=click.Path(exists=True), 
    help='Input directory to segmentation files'
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory for PNG images'
)
@click.option(
    '--fig_width', 
    type=click.Path(), 
    default=10,
    help='Figure width (default: 10)'
)
@click.option(
    '--fig_height', 
    type=click.Path(), 
    default=10,
    help='Figure height (default: 10)'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite [true|false]'
)
def createpngsfromsegmentations(segmentations, output, fig_width, fig_height, overwrite):
    """
    Creates PNG images from L3 muscle and fat segmentation files
    
    Parameters
    ----------
    --segmentations : str
        Directory with with input segmentation files. Must be L3 muscle and fat segmentations
        (output of "mosamatic2-cli segmentmusclefatl3tensorflow")

    --output : str
        Path to output directory

    --fig_width : int
        Width of PNG image

    --fig_height : int
        Height of PNG image

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    task = CreatePngsFromSegmentationsTask(
        inputs={'segmentations': segmentations},
        params={'fig_width': fig_width, 'fig_height': fig_height},
        output=output,
        overwrite=overwrite,
    )
    task.run()