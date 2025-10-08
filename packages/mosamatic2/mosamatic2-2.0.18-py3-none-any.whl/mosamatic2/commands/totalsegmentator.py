import click

from mosamatic2.core.tasks import TotalSegmentatorTask


@click.command(help='Run Total Segmentator on CT scans')
@click.option(
    '--scans', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with scans (each patient separate subdirectory)',
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--tasks', 
    default='total',
    help='Comma-separated list of Total Segmentator tasks to run (no spaces!)'
)
@click.option(
    '--format',
    default='dicom',
    help='Process scans in DICOM or NIFTI format [dicom|nifti] (default: dicom)'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite [true|false]'
)
def totalsegmentator(scans, tasks, format, output, overwrite):
    """
    Run Total Segmentator on CT scans. If you want to run specialized tasks
    like "liver_segments" or "liver_vessels" you need an educational license.
    Check out https://github.com/wasserth/TotalSegmentator?tab=readme-ov-file
    to find out how to get such a license.
    
    Parameters
    ----------
    --scans : str
        Directory to scans. Each patient's scan should be in a separate
        subdirectory. For example:

        /scans
        /scans/patient1
        /scans/patient1/file1.dcm
        /scans/patient1/file2.dcm
        ...
        /scans/patient2
        ...

    --output : str
        Path to output directory where selected slices will be placed. Each
        slice's file name will be the same as the scan directory name, so in
        the example above that would be "patient1", "patient2", etc.

    --tasks : str
        Comma-separated list of Total Segmentator tasks to run (no spaces!)

    --format : str
        Process scans in DICOM or NIFTI format. Options: [dicom|nifti]
        Default is 'dicom'.

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    task = TotalSegmentatorTask(
        inputs={'scans': scans},
        params={'tasks': tasks, 'format': format},
        output=output,
        overwrite=overwrite,
    )
    task.run()