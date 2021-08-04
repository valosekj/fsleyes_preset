#
# Open FSLeyes and automatically set display options (such as -cm (colormap), -dr (display range), -a (opacity))
#
# Jan Valosek, fMRI laboratory Olomouc, 2021
#

import os
import sys
import re

import nibabel as nib
import numpy as np

from enum import Enum


class Machine(Enum):
    linux_laboratory = '/usr/local/fsl-6.0.4/bin/fsleyes'
    linux = '/usr/local/fsl/bin/fsleyes'
    mac = 'fsleyes'

# Some of FSLeyes options
# To see all options, run fsleyes --fullhelp
# -dr LO HI - display range
# -cm CMAP - color map
# -a PERC - alpha (opacity)
# -xh - hide the X plane
# -yh - hide the Y plane
# -zh - hide the Z plane
# -n - set name to overlay (only within FSLeyes)

# REGEX explanation
# ".*" - matches any number of characters
# "." - matches only a single character
# "*" - matches zero or more - group in brackets () that precedes the star can occur any number of times in the text

conversion_dict = {
    'sub.*acq-T1map.*MRF(_crop)*(_masked)*.nii(.gz)*': '-dr 0 2000 -cm hot',  # T1-map
    'sub.*acq-T2map.*MRF(_crop)*(_masked)*.nii(.gz)*': '-dr 0 80 -cm brain_colours_2winter_iso',  # T2-map
    '_seg(_manual)*.nii(.gz)*': '-cm red -a 50',  # SC segmentation
    '_seg_crop': '-cm red -a 50',	# Cropped SC segmetnation
    '_seg_labeled.nii': '-cm random -a 70',  # SC labeling
    '_labels.nii': '-cm red',  # SC labels
    '_gmseg(_manual)*.nii(.gz)*': '-cm blue -a 50',  # GM segmentation
    'PAM50_cord': '-cm red -a 50',  # PAM50 SC
    'PAM50_levels': '-cm random -a 50',  # PAM50 labeling
    'PAM50_wm': '-cm blue-lightblue -dr 0.5 1', # PAM50 WM
    'PAM50_gm': '-cm red-yellow -dr 0.5 1',		# PAM50 GM
    'PAM50_atlas_53': '-cm green -dr 0.3 1',	# PAM50 dorsal columns
    'PAM50_atlas_54': '-cm blue-lightblue -dr 0.3 1',	# PAM50 lateral columns
    'PAM50_atlas_55': '-cm yellow -dr 0.3 1',	# PAM50 ventral columns
    '.*FA.nii(.gz)*': '-cm red-yellow -dr 0 1',	# DTI FA map
    '_perf_': '-dr 0 20',		# perfusion
    'thresh_zstat': '-cm red-yellow',	# FEAT activation
    '_bin.nii': '-cm blue'		# Binarized mask
}

# List of images to set max intensity to 70%
set_intensity_list = ['T1w.nii.gz', 'T2w.nii.gz', 'T2star.nii.gz', 'Mprage.nii.gz', 'MprageGd.nii.gz']


def run_command(command, print_command=True):
    """
    Run shell command using os.system and print the command itself as a string into terminal
    :param command: str: shell command to run
    :param print_command: bool: if true, print command into terminal, if false, do not print command
    :return:
    """
    if print_command:
        print('Executing: {}'.format(command))
    os.system(command)


def get_fsleyes_command():
    """
    Get shell command for FSLeyes based on OS
    :return: str: fsleyes command
    """
    # MacOS
    if sys.platform == 'darwin':
        return Machine.mac.value
    # Linux in fMRI laboratory
    elif sys.platform == 'linux' and os.path.isfile(Machine.linux_laboratory.value):
        return Machine.linux_laboratory.value
    # All other Linux machines
    else:
        return Machine.linux.value


def get_image_intensities(fname_image):
    """
    Get min and max intensities for input nifti image
    :param fname_image: str: input nifti image
    :return: min_intensity: float64: minimum intensity of input image
    :return: max_intensity: float64: maximum intensity of input image
    """
    # Load nii image
    image = nib.load(fname_image)
    # Get min intensity
    min_intensity = np.min(image.get_fdata())
    # Get max intensity
    max_intensity = np.max(image.get_fdata())

    return min_intensity, max_intensity


def main(argv=None):
    """
    Construct fsleyes command
    :param argv:
    :return:
    """

    arguments_list = list()
    no_arguments_list = list()

    # Loop across input arguments (i.e., individual input files)
    for arg in argv:

        if not os.path.isfile(arg):
            print(f'ERROR - File {arg} does not exist.')
            sys.exit()

        if '[' in arg or ']' in arg:
            print('ERROR - Regular expression in filenames is not supported, use wild card (*) instead')
            sys.exit()

        # Loop across items in conversion dict
        for key, value in conversion_dict.items():
	    # Compile a regular expression pattern into regular expression object
            keyRegex = re.compile(key)
            # Check if input file (arg) is included in conversion dict (keyRegex)
            if bool(keyRegex.search(arg)):
                # Add options (-dr, -cm, ...) for given file
                arguments_list.append(arg + ' ' + value)

        # Loop across items in list with structural images to decrease max intensity
        for item in set_intensity_list:
            if item in arg:
                # Get absolute path to nii file
                fname = os.path.abspath(arg)
                # Get max intensity
                _, max_intensity = get_image_intensities(fname)
                # Decrease max intensity to 70 %
                max_intensity = str(int(max_intensity * 0.7))
                # Add -dr option
                arguments_list.append(arg + ' -dr 0 ' + max_intensity)

    # Convert list of arguments into one single string
    arguments_string = ' '.join([str(element) for element in arguments_list])

    # Identify files without any argument
    # Loop across input arguments (i.e., individual input files)
    for arg in argv:
        # Continue only if current file is nifti file (i.e., skip json, yml and all other files)
        if arg.endswith('.nii') or arg.endswith('.nii.gz'):
            if arg not in arguments_string:
                no_arguments_list.append(arg)

    # Convert list into one single string
    no_arguments_string = ' '.join([str(element) for element in no_arguments_list])

    # Construct shell command with fsleyes based on operating system (linux or darwin)
    command = get_fsleyes_command() + ' ' + no_arguments_string + ' ' + arguments_string

    # Call shell command
    run_command(command)


if __name__ == "__main__":
    main(sys.argv[1:])
