"""
flekspy Public API.
"""

from pathlib import Path
import errno
from itertools import islice
from flekspy.idl import read_idl, IDLAccessor
from flekspy.yt import YtFLEKSData, extract_phase
from flekspy.tp import FLEKSTP
from flekspy.amrex import AMReXParticleData
import xarray as xr


def load(
    filename: str,
    iDomain: int = 0,
    iSpecies: int = 0,
    iFile: int = 0,
    readFieldData: bool = False,
    use_yt_loader: bool = False,
):
    """Load FLEKS data.

    Args:
        filename (str): Input file name pattern.
        iDomain (int, optional): Test particle domain index. Defaults to 0.
        iSpecies (int, optional): Test particle species index. Defaults to 0.
        iFile (int, optional): The index of the file to load if the pattern
            matches multiple files. Defaults to 0.
        readFieldData (bool, optional): Whether or not to read field data for test particles. Defaults to False.
        use_yt_loader (bool, optional): If True, forces the use of the yt loader for AMReX data. Defaults to False.

    Returns:
        FLEKS data: xarray.Dataset, YtFLEKSData, or FLEKSTP
    """
    p = Path(filename)
    file_generator = p.parent.rglob(p.name)
    # Advance the generator to the iFile-th position and get the file.
    selected_file_iter = islice(file_generator, iFile, iFile + 1)
    try:
        selected_file = next(selected_file_iter)
    except StopIteration:
        selected_file = None

    if selected_file is None:
        message = f"No files found matching pattern: '{filename}'"
        if iFile > 0:
            message += f" at index {iFile}"
        raise FileNotFoundError(errno.ENOENT, message, filename)
    filename = str(selected_file.resolve())

    filepath = Path(filename)
    basename = filepath.name

    if basename == "test_particles":
        return FLEKSTP(filename, iDomain=iDomain, iSpecies=iSpecies)
    elif filepath.suffix in [".out", ".outs"]:
        return read_idl(filename)
    elif basename.endswith("_amrex"):
        if use_yt_loader or "particle" not in basename:
            return YtFLEKSData(filename, readFieldData)
        else:
            return AMReXParticleData(filename)
    else:
        raise Exception("Error: unknown file format!")
