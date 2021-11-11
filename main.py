import numpy as np
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
                        str.join(["infile=", filename]),
                        str.join(["ofile=", out_dir + "/" + os.path.basename(filename)[0:14],  ".bl2bin"]),
                        str.join(["l3bprod=", product]),
                        str.join(["resolve=", str(spatial_res)]),
                        str.join(["flaguse=", flags])
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
                    str.join(["ifile=", filenames]),
                    str.join(["ofile=", out_name]),
                    str.join(["prod=", product]),
                    str.join(["loneast=", str(input_coords[0])]),
                    str.join(["lonwest=", str(input_coords[1])]),
                    str.join(["latnorth=", str(input_coords[2])]),
                    str.join(["latsouth=", str(input_coords[3])]),
                    ])

l2bin(["test.nc"], "test2", "chlor_a", "", 4.6)