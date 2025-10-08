import click

from mosamatic2.core.pipelines import LiverAnalysisPipeline


@click.command(help='Runs liver analysis pipeline')
@click.option(
    '--scans', 
    required=True, 
    type=click.Path(exists=True), 
    help='Root directory with scan directories for each patient (no spaces allowed)',
)
@click.option(
    '--compressed', 
    default=True,
    help='Whether to produce compressed NIFTI file or not (default: True)'
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
def liveranalysispipeline(scans, compressed, output, overwrite):
    """
    Runs liver analysis pipeline. This pipeline run the following steps on each scan: 

    (1) DICOM to NIFTI conversion
    (2) Extract liver segments using Total Segmentator
    (3) Calculate segment statistics, e.g., volume (mL), mean HU, std HU and PNG image
        of each segments HU histogram.
    
    Parameters
    ----------
    --scans : str
        Root directory with scan directories for each patient. Each scan directory should 
        contain DICOM images for a single scan only and nothing else. Also, the directory
        paths cannot contain any spaces.

    --compressed : str
        Whether to produce compressed NIFTI file or not (default: True)

    --output : str
        Path to output directory. No spaces allowed.

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    pipeline = LiverAnalysisPipeline(
        inputs={'scans': scans},
        params={'compressed': compressed},
        output=output,
        overwrite=overwrite,
    )
    pipeline.run()