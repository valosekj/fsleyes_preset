#
# Open FSLeyes and automatically set display options (such as -cm (colormap), -dr (display range), -a (opacity))
#
# Jan Valosek, fMRI laboratory Olomouc, 2021
#

import os
import sys

fsleyes_command = {
    'linux': '/usr/local/fsl-6.0.4/bin/fsleyes',
    'darwin': 'fsleyes'
}

conversion_dict = {
    'acq-T1map': '-dr 0 2000 -cm hot',  # T1-map
    'acq-T2map': '-dr 0 150 -cm brain_colours_2winter_iso',  # T2-map
    '_seg.nii': '-cm red -a 50',  # SC segmentation
    '_seg_labeled.nii': '-cm random -a 70',  # SC labeling
    '_labels.nii': '-cm red',  # SC labels
    '_gmseg.nii': '-cm blue -a 50',  # GM segmentation
    'PAM50_cord': '-cm red -a 50',  # PAM50 SC
    'PAM50_levels': '-cm random -a 50'  # PAM50 labeling
}


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


def main(argv=None):
    """
    Construct fsleyes command
    :param argv:
    :return:
    """

    arguments_list = list()

    # Loop across input arguments (i.e., individual input files)
    for arg in argv:
        # Loop across items in conversion dict
        for key, value in conversion_dict.items():
            # Check if input file is included in conversion dict
            if key in arg:
                # Add options (-dr, -cm, ...) for given file
                arguments_list.append(arg + ' ' + value)

    # Convert list of arguments into one single string
    arguments_string = ' '.join([str(element) for element in arguments_list])

    # Construct shell command with fsleyes based on operating system (linux or darwin)
    command = fsleyes_command[sys.platform] + ' ' + arguments_string

    # Call shell command
    run_command(command)


if __name__ == "__main__":
    main(sys.argv[1:])
