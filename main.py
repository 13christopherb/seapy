import numpy as np
import subprocess
import os
def l2bin(filenames: list, out_dir: str, product: str, flags: str, spatial_res: float):
    """
    Runs the l2bin command on all the level 2 files provided and outputs
    level 3 files binned to the specified spatial resolution

    Keyword arguments:
    filenames -- list of filenames to run l2bin on
    out_dir -- directory to write l3binned files to
    product -- data product of the files (e.g. chlor_a)
    flags -- flags to check for
    spatial_res -- desired spatial resolution of l3bin files
    """

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for filename in filenames:
        print("\n=============>L2BIN<=============")
        subprocess.run(['l2bin',
                        'infile=' + filename,
                        "ofile=" + out_dir + "/" + os.path.basename(filename)[0:14] + ".bl2bin", "l3bprod=" + product,
                        "resolve=" + str(spatial_res),
                        "flaguse=" + flags])

l2bin(["test.nc"], "test2", "chlor_a", "", 4.6)