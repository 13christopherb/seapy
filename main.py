import numpy as np
from itertools import groupby
import subprocess
from pathlib import Path
from typing import Sequence, Union
import os


def l2bin(filenames: Sequence[Path], out_dir: Union[str, Path], product: str, flags: str, spatial_res: float):
    """
    Runs the l2bin command on all the level 2 files provided and outputs
    level 3 files binned to the specified spatial resolution

    Keyword arguments:
        filenames -- list of file names to run l2bin on
        out_dir -- directory to write l3binned files to
        product -- data product of the files (e.g. chlor_a)
        flags -- flags to check for
        spatial_res -- desired spatial resolution of l3bin files
    """

    if not out_dir.exists():
        os.makedirs(out_dir)

    for filename in filenames:
        print("\n=============>L2BIN<=============")
        subprocess.run(["l2bin",
                        f"infile={filename}",
                        f"ofile={out_dir / filename.name[0:14]}.bl2bin",
                        f"l3bprod={product}",
                        f"resolve={spatial_res}",
                        f"flaguse={flags}",
                        ])


def l3bin(filename: str, out_name: str, product: str, spatial_bounds: list):
    """
    Runs the l3bin command to temporally bin multiple l3bin files

    Keyword arguments:
        filename -- file name of a file containing all of the level 3 binned files to input
        out_name -- name for the temporally binned level 3 file
        product -- data product of the files (e.g. chlor_a)
        spatial_bounds -- list of boundary latitudes and longitudes in order of east, west, north, south
    """

    if not os.path.exists(os.path.dirname(out_name)):
        os.makedirs(os.path.dirname(out_name))

    print("\n=============>L3BIN<=============")
    subprocess.run(["l3bin",
                    f"ifile={filename}",
                    f"ofile={out_name}",
                    f"prod={product}",
                    f"loneast={spatial_bounds[0]}",
                    f"lonwest={spatial_bounds[1]}",
                    f"latnorth={spatial_bounds[2]}",
                    f"latsouth={spatial_bounds[3]}",
                    "noext=1",
                    ])


def write_file_list(path: Union[str, Path], filenames: Sequence[Path]) -> str:
    """
    Writes a list of all of the spatially binned level 3 files to a .txt file

    Keyword arguments:
        path -- filepath for directory containing the files to be listed
        filenames -- list of all the level 3 files to listed in the final file

    return:
        the full file name of the .txt file
    """

    file_list = path / "l2b_list.txt"

    f = open(file_list, mode='w')
    for file in filenames:
        file_path = path / file
        if file_path.exists():
            f.write(f"{file_path}\n")

    f.close()

    return file_list


def process(filenames: Sequence[Path], product: str, flags: str, spatial_res: int, sensor: str, year: int, spatial_bounds: list):
    """
    Takes raw level 2 files and converts them into spatially and temporally binned level 3 files

    Keyword arguments:
        filenames -- list of file paths for the raw level 2 files to be binned
        product -- data product to include in level 3 files (e.g. chlor_a)
        flags -- flags to pass to l2bin seadas command
        spatial_res -- spatial resolution for binning (1: 1.1km, 4: 4.3km )
        sensor -- sensor which produced level 2 files (e.g. modis)
        year -- the year the files are from
        spatial_bounds -- list of boundary latitudes and longitudes in order of east, west, north, south
    """
    l2bin_output = Path(filenames[0]).parent / "l2bin"
    l3bin_output = Path("l3bin")

    daily_files = [list(i) for _, i in groupby(np.sort(filenames), lambda a: Path(a).name[5:8])]

    for day_files in daily_files:
        l2bin(day_files, l2bin_output, product, flags, spatial_res)
        file_list = write_file_list(l2bin_output, [Path(f"{f.name[:14]}.bl2bin") for f in day_files])

        l3bin_output_file = (l3bin_output / "daily" / sensor / str(year) / day_files[0].name[:8]).with_suffix(".nc")
        l3bin(file_list, l3bin_output_file, product, spatial_bounds)

    for file in l2bin_output.glob("*.bl2bin"):
        os.remove(file)

    os.remove(l2bin_output / "l2b_list.txt")


def batch_process():
    p = Path("requested_files/modis")
    filenames = list(p.glob("*.nc"))
    flags = os.popen("more $OCSSWROOT/share/modis/l2bin_defaults.par | grep  flaguse").read().split('=')[1]
    process(filenames, "chlor_a", flags, 4, "modis", 2008, [-120, -180, 60, 20])


batch_process()
