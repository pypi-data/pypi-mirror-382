import click

from mosamatic2.core.tasks import SelectSliceFromScansTask


@click.command(help='Selects specific slice from CT scans')
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
    '--vertebra', 
    required=True,
    help='Vertebral level for selecting slice (default: "L3")'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite [true|false]'
)
def selectslicefromscans(scans, vertebra, output, overwrite):
    """
    Selects specific slice from list of CT scans
    
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

    --vertebra : str
        Vertebral level where to take slice [L3|T4]

    --overwrite : bool
        Overwrite contents output directory [true|false]
    """
    task = SelectSliceFromScansTask(
        inputs={'scans': scans},
        params={'vertebra': vertebra},
        output=output,
        overwrite=overwrite,
    )
    task.run()