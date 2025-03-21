#
# Open FSLeyes and automatically set display options such as -cm (colormap), -dr (display range), -a (opacity)
#
# Authors: Jan Valosek, 2021-2024
#

import os
import sys
import re
import glob

import nibabel as nib
import numpy as np

from enum import Enum


class Machine(Enum):
#    linux_laboratory = '/usr/local/fsl-6.0.4/bin/fsleyes'
    linux_laboratory = '/usr/local/fsleyes-1.3.3.env/bin/fsleyes'
    linux = '/usr/local/fsl/bin/fsleyes'
    mac = 'fsleyes'

# Some of FSLeyes options
# To see all options, run fsleyes --fullhelp
# -dr LO HI - display range
# -cm CMAP - color map color
# -un - use negative colormap
# -nc CMAP - ngative colormap color
# -a PERC - alpha (opacity)
# -ot TYPE - overlay type (complex, label, linevector, mask, mesh, mip, rgb, rgbvector, sh, tensor, volume)
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
    'sub.*acq-T1-T2map.*MRF(_crop)*(masked)*.nii(.gz)*': '-dr 0 50', 	# T1/T2 ratio
    'sub.*acq-M0map.*MRF(_crop)*(_masked)*.nii(.gz)*': '-dr 0 300',  # M0-map (proton density)
    '_seg([-_]manual)*.nii(.gz)*': '-cm red -a 50',  # SC segmentation
    '_centerline.nii(.gz)*': '-cm red',		# SC centerline
    '_pred.nii(.gz)*': '-cm blue -a 50',	# ivadomed prediction
    '_seg_crop': '-cm red -a 50',	# Cropped SC segmetnation
    '_seg_labeled.*.nii(.gz)*': '-cm cortical -a 70',  # SC labeling
    '_lesion([-_]manual)*.nii(.gz)*': '-cm blue',		# SCI/MS lesion seg
    # Custom jet colormap: https://gist.github.com/valosekj/e9464071a07197f52a4526d8014e2e9a
    'rootlet.*.nii(.gz)*': '-cm jet_matplotlib',		# spinal rootlets
#    '_*labels.*.nii(.gz)*': '-cm red',  # SC labels    # commenting because it matches also /derivatives/labels
    '_gmseg([-_]manual)*.nii(.gz)*': '-cm red-yellow -a 50',  # GM segmentation
    '_wmseg(_erode)*([-_]manual)*.nii(.gz)*': '-cm blue-lightblue -a 50',  # WM segmentation
    'PAM50_cord': '-cm red -a 50',  # PAM50 SC
    'PAM50_levels': '-cm cortical -a 50',  # PAM50 labeling
    'PAM50_wm': '-cm blue-lightblue -dr 0.5 1', # PAM50 WM template
    'PAM50_atlas_51': '-cm blue-lightblue -dr 0.5 1', # PAM50 WM atlas
    'PAM50_gm': '-cm red-yellow -dr 0.5 1',		# PAM50 GM template
    'PAM50_atlas_52': '-cm red-yellow -dr 0.5 1',		# PAM50 GM atlas
    'PAM50_atlas_53': '-cm green -dr 0.3 1',	# PAM50 dorsal columns
    'PAM50_atlas_54': '-cm blue-lightblue -dr 0.3 1',	# PAM50 lateral columns
    'PAM50_atlas_55': '-cm yellow -dr 0.3 1',	# PAM50 ventral columns
    '.*FA.nii(.gz)*': '-cm red-yellow -dr 0 1',	# DTI FA map
    '.*dyads.*.nii(.gz)*': ' -ot linevector',        # FSL bedpostx output
    '_perf_': '-dr 0 20',		# perfusion
    '.*zstat.*': '-cm red-yellow -nc blue-lightblue -un',	    # FEAT activation (-un - use negative colormap)
    '_bin.nii(.gz)*': '-cm blue -a 50',		# Binarized mask
    '.*mask.*': '-cm blue -a 50',		# Binarized mask
    '.*brain.nii(.gz)*': '-cm blue -a 50',			# Brain mask (FSL BET output)
    'fdt_paths.nii.gz': '-cm red-yellow'
}

# max intensity (*100 to get %)
set_intensity_dict = {
    '[tT]1w.nii(.gz)*': [0, 0.7],
    '[tT]2w.nii(.gz)*': [0, 0.7],
    '[tT]2s(tar)*(w)*.nii(.gz)*': [0, 0.7],
    'T2TRA_thr_bias_corr.nii(.gz)*': [0, 0.7],
    'Mprage([1-9])*.nii(.gz)*': [0, 0.5],
    'MprageGd.nii(.gz)*': [0, 0.5],
    'dti([1-9])*.nii(.gz)*': [0, 0.5],
    '.*mddw.*.nii(.gz)*': [0, 0.5],
    'sub-[1-9][1-9][1-9]([1-9]B)*(_acq-0[0-9])*(_inv-01)*(_)*part-mag_IRT1.nii(.gz)*': [0, 0.2],
    '.*part-real_IRT1.nii(.gz)*': [0.35, 0.6]
}

# Dict of images to set human readable name in FSLeyes
# if key == value, name is set based on abs filename (which includes subID), otherwise, name is set based on key
set_name = {'fdt_paths.nii.gz': 'fdt_paths.nii.gz',
            'PAM50_atlas_50': 'PAM50_spinal_cord',
            'PAM50_atlas_51': 'PAM50_white_matter',
            'PAM50_atlas_52': 'PAM50_gray_matter',
            'PAM50_atlas_53': 'PAM50_ventral_columns',
            'PAM50_atlas_54': 'PAM50_lateral_columns',
            'PAM50_atlas_55': 'PAM50_dorsal_columns',
            'PAM50_atlas_56': 'PAM50_fasciculus_gracilis',
            'PAM50_atlas_57': 'PAM50_dorsal_cuneatus',
            'PAM50_atlas_58': 'PAM50_lateral_corticospinal_tracts',
            'PAM50_atlas_59': 'PAM50_spinal_lemniscus',
            'PAM50_atlas_60': 'PAM50_ventral_corticospinal_tracts',
            'PAM50_atlas_61': 'PAM50_ventral_GM_horns',
            'PAM50_atlas_62': 'PAM50_dorsal_GM_horns',
            }

# List of supported nifti datatypes
supported_data_types = ['int8', 'int16', 'int32', 'float32', 'float64', 'uint8', 'uint16']


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


def get_image_type(fname_image):
    """
    Get nifti image datatype
    :param fname_image: str: input nifti image
    :return: bool
    """

    # TODO - image with RGB datatype could be shown with -ot rgb option

    # Load nii image
    image = nib.load(fname_image)
    # Check data_type (e.g., exclude RGB FA)
    data_type = image.get_data_dtype()
    # If data type is in list of supported datatype, return True, otherwise return False
    if data_type in supported_data_types:
        return True
    else:
        return False


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

        # Open MNI standard if -std1mm or std1mm is passed
        if 'std1mm' in arg:
            # Get all available FSL versions
            available_fsl = glob.glob('/usr/local/fsl*')
            # Select the first one
            # TODO - consider if the first one is always the best
            available_fsl.sort()
            first_fsl = available_fsl[0]
            std1mm_path = os.path.join(first_fsl, 'data/standard/MNI152_T1_1mm.nii.gz')
            if os.path.isfile(std1mm_path):
                no_arguments_list.append(std1mm_path)
            else:
                print(f'ERROR - Standard {std1mm_path} does not exist.')
            continue

        # Skip argument if it is folder
        if os.path.isdir(arg):
            continue

        if not os.path.isfile(arg):
            print(f'ERROR - File {arg} does not exist.')
            sys.exit()

        if '[' in arg or ']' in arg:
            print('ERROR - Regular expression in filenames is not supported, use wild card (*) instead')
            sys.exit()

        # Skip json, yml and all other files
        if not arg.endswith('.nii') and not arg.endswith('.nii.gz'):
            continue

        if not get_image_type(os.path.abspath(arg)):
            print(f'WARNING - Unsupported datatype for {arg}')
            continue

        # Loop across items in conversion dict
        for key, value in conversion_dict.items():
            # Compile a regular expression pattern into regular expression object
            keyRegex = re.compile(key)
            # Check if input file (arg) is included in conversion dict (keyRegex)
            if bool(keyRegex.search(arg)):
                # Add options (-dr, -cm, ...) for given file
                arguments_list.append(arg + ' ' + value)
                # Loop across keys in dict to change name
                for item in set_name.keys():
                    # Compile a regular expression pattern into regular expression object
                    itemRegex = re.compile(item)
                    # Check if input file (arg) is included in itemRegex
                    if bool(itemRegex.search(arg)):
                        # if key is equal to value, set name based on abs filename (which includes subID)
                        if item == set_name[item]:
                            # Get full absolute path to input file
                            arg_full_path = os.path.abspath(arg)
                            # Get name of directory where is the file saved
                            directory_name = arg_full_path.split('/')[-2]
                            # Append to the list
                            arguments_list.append(' -n ' + directory_name)
                        # if key is not equal to value, set name based on dict value
                        else:
                            # Append to the list
                            arguments_list.append(' -n ' + set_name[item])

        # Loop across items in dict with images to decrease min and max intensity
        for key, value in set_intensity_dict.items():
            # Compile a regular expression pattern into regular expression object
            itemRegex = re.compile(key)
            # Check if input file (arg) is included in itemRegex
            if bool(itemRegex.search(arg)):
                # Get absolute path to nii file
                fname = os.path.abspath(arg)
                # Get max intensity
                _, max_intensity = get_image_intensities(fname)
                # Set min intensity to x % from max
                min_intensity = str(max_intensity * value[0])
                # Decrease max intensity to x %
                max_intensity = str(max_intensity * value[1])
                # Add -dr option
                arguments_list.append(arg + ' -dr ' + min_intensity + ' ' + max_intensity)

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
