#
# Open FSLeyes and automatically set display options (such as -cm (colormap), -dr (display range), -a (opacity))
#
# Display options are fetched from config.py file located in your home directory (~/.fsleyes_preset/config.py). If this
# file does not exist, the default template config.py file within this repository is used.
#
# Jan Valosek, fMRI laboratory Olomouc, 2021
#

import os
import sys
import re

import nibabel as nib
import numpy as np

from enum import Enum

# Path where your config.py configuration file should be located
config_file_path = os.path.expanduser('~/.fsleyes_preset')


class Machine(Enum):
    linux_laboratory = '/usr/local/fsl-6.0.4/bin/fsleyes'
    linux = '/usr/local/fsl/bin/fsleyes'
    mac = 'fsleyes'


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

    # Import settings from config file from your home directory ('~/.fsleyes_preset/config.py')
    if os.path.isfile(os.path.join(config_file_path, 'config.py')):
        sys.path.append(config_file_path)
        from config import conversion_dict, set_intensity_list
    # If config file in your home directory ('~/.fsleyes_preset/config.py') does not exist, use the default template
    elif os.path.isfile(os.path.join(os.path.dirname(sys.argv[0]), 'config.py')):
        print('\nWARNING: {} config file not found. Using template config file with limited settings.\n'.
              format(os.path.join(config_file_path, 'config.py')))
        from config import conversion_dict, set_intensity_list

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
