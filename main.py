import numpy as np
from itertools import groupby
import subprocess
import os

def l2bin(filenames: list, out_dir: str, product: str, flags: str, spatial_res: float):
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

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for filename in filenames:
        print("\n=============>L2BIN<=============")
        subprocess.run(["l2bin",
                        "".join(["infile=", filename]),
                        "".join(["ofile=", out_dir + "/" + os.path.basename(filename)[0:14],  ".bl2bin"]),
                        "".join(["l3bprod=", product]),
                        "".join(["resolve=", str(spatial_res)]),
                        "".join(["flaguse=", flags])
                        ])

def l3bin(filenames: str, out_name: str, product: str, input_coords: list):
    """
    Runs the l3bin command to temporally bin multiple l3bin files

    Keyword arguments:
    filenames -- file name of a file containing all of the level 3 binned files to input
    out_name -- name for the temporally binned level 3 file
    product -- data product of the files (e.g. chlor_a)
    input_coords -- list of boundary latitudes and longitudes in order of east, west, north, south
    """
    print("\n=============>L3BIN<=============")
    subprocess.run(["l3bin",
                    "".join(["ifile=", filenames]),
                    "".join(["ofile=", out_name]),
                    "".join(["prod=", product]),
                    "".join(["loneast=", str(input_coords[0])]),
                    "".join(["lonwest=", str(input_coords[1])]),
                    "".join(["latnorth=", str(input_coords[2])]),
                    "".join(["latsouth=", str(input_coords[3])]),
                    ])


def process(filenames, product, flags, spatial_res, sensor, year, coords):

    # make directories
    temp = os.path.dirname(filenames[0])
    l2bin_output = temp + '/l2bin'
    l3bin_output = temp + '/l3bin'

    daily_files = [list(i) for j, i in groupby(np.sort(filenames),lambda a: os.path.basename(a)[5:8])]

    # average
    for day_files in daily_files:
        l2bin(day_files, l2bin_output, product, flags, spatial_res)

        #TODO make list of files to give l3bin

        l3bin_output_dir = l3bin_output + '/' + "daily"
        l3bin_output_file = l3bin_output_dir + '/' + sensor + str(year) + os.path.basename(day_files[0])[5:8] + str(year) + day_files[0] + '.nc'
        l3bin(ascii_files, l3bin_output_file, product, coords)


l2bin(["test.nc"], "test2", "chlor_a", "", 4.6)