import numpy as np
import glob
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


def l3bin(filenames: str, out_name: str, product: str, spatial_bounds: list):
    """
    Runs the l3bin command to temporally bin multiple l3bin files

    Keyword arguments:
        filenames -- file name of a file containing all of the level 3 binned files to input
        out_name -- name for the temporally binned level 3 file
        product -- data product of the files (e.g. chlor_a)
        spatial_bounds -- list of boundary latitudes and longitudes in order of east, west, north, south
    """

    if not os.path.exists(os.path.dirname(out_name)):
        os.makedirs(os.path.dirname(out_name))

    print("\n=============>L3BIN<=============")
    subprocess.run(["l3bin",
                    "".join(["ifile=", filenames]),
                    "".join(["ofile=", out_name]),
                    "".join(["prod=", product]),
                    "".join(["loneast=", str(spatial_bounds[0])]),
                    "".join(["lonwest=", str(spatial_bounds[1])]),
                    "".join(["latnorth=", str(spatial_bounds[2])]),
                    "".join(["latsouth=", str(spatial_bounds[3])]),
                    "noext=1",
                    ])


def write_file_list(path: str, filenames: list) -> str:
    """
    Writes a list of all of the spatially binned level 3 files to a .txt file

    Keyword arguments:
        path -- filepath for directory containing the files to be listed
        filenames -- list of all the level 3 files to listed in the final file

    return:
        the full file name of the .txt file
    """

    file_list = "".join([path, "/", "l2b_list.txt"])

    f = open(file_list, 'w')
    for file in filenames:
        if os.path.exists("".join([path, "/", file, ".bl2bin"])):
            f.write("".join([path, "/", file, ".bl2bin\n"]))

    f.close()

    return file_list


def process(filenames: list, product: str, flags: str, spatial_res: int, sensor: str, year: int, spatial_bounds: list):
    """
    Takes raw level 2 files and converts them into spatially and temporally binned level 3 files

    TODO: Remove interemdiate files

    Keyword arguments:
        filenames -- list of file paths for the raw level 2 files to be binned
        product -- data product to include in level 3 files (e.g. chlor_a)
        flags -- flags to pass to l2bin seadas command
        spatial_res -- spatial resolution for binning (1: 1.1km, 4: 4.3km )
        sensor -- sensor which produced level 2 files (e.g. modis)
        year -- the year the files are from
        spatial_bounds -- list of boundary latitudes and longitudes in order of east, west, north, south
    """
    temp = os.path.dirname(filenames[0])
    l2bin_output = "/".join([temp + "l2bin"])
    l3bin_output = "l3bin"

    daily_files = [list(i) for j, i in groupby(np.sort(filenames), lambda a: os.path.basename(a)[5:8])]

    for day_files in daily_files:
        l2bin(day_files, l2bin_output, product, flags, spatial_res)
        file_list = write_file_list(l2bin_output, [os.path.basename(f)[:14] for f in day_files])

        l3bin_output_file = "/".join([l3bin_output, "daily", sensor, str(year), os.path.basename(day_files[0])])
        l3bin(file_list, l3bin_output_file, product, spatial_bounds)

    for file in glob.glob("/".join([l2bin_output, "*.bl2bin"])):
        os.remove(file)

    os.remove("/".join([l2bin_output, "l2b_list.txt"]))


def batch_process():
    filenames = glob.glob("requested_files/*.nc")
    flags = os.popen("more $OCSSWROOT/share/modis/l2bin_defaults.par | grep  flaguse").read().split('=')[1]
    process(filenames, "chlor_a", flags, 1, "modis", 2008, [-120, -180, 60, 20])


batch_process()
