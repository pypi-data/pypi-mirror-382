import click

from mosamatic2.core.tasks import CreateDicomSummaryTask


@click.command(help='Creates a DICOM summary inside a root directory')
@click.option(
    '--directory', 
    required=True, 
    type=click.Path(exists=True), 
    help='Root directory with DICOM images (can be multiple scans)',
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
def createdicomsummary(directory, output, overwrite):
    """
    Creates a DICOM summary inside a root directory. Each patient should have
    its own directory. Inside each patient's directory, there can be multiple
    scans (called series) and multiple DICOM files per scan. The output of this
    command is a file summary.txt (stored in the output directory) that contains
    the following information:

    - A list of patient directory names with the number of scans inside each
      patient directory
    - For each patient directory and scan directory the following information:
        - Nr. of DICOM images in the scan
        - Modality (e.g., CT or MRI)
        - Image type (e.g., for Dixon scans can be in-phase, opposite-phase, 
          water or fat images)
        - Rows/columns (size of the images)
        - Pixel spacing (size of each pixel in mm^2)
        - Slice thickness: (thickness of each image slice)

    Parameters
    ----------
    --directory : str
        Root directory with patient directories, scans and DICOM images

    --output : str
        Path to output directory

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    task = CreateDicomSummaryTask(
        inputs={'directory': directory},
        params=None,
        output=output,
        overwrite=overwrite,
    )
    task.run()