#
# This is a template of configuration file for fsleyes_preset.py script
#
# Modify this template file (add items to dictionary and list below) and save the file to your home directory
# as ~/.fsleyes_preset/config.py
#
# Jan Valosek, fMRI laboratory Olomouc, 2021
#

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
    '_seg(_manual)*.nii(.gz)*': '-cm red -a 50',    # spinal cord segmentation
    '_seg_labeled.nii': '-cm random -a 70',         # spinal cord labeling
    '_gmseg(_manual)*.nii(.gz)*': '-cm blue -a 50', # spinal cord gray matter segmentation
    '.*FA.nii(.gz)*': '-cm red-yellow -dr 0 1',	    # DTI FA map
    'thresh_zstat': '-cm red-yellow',	            # FSL FEAT activation
    '_bin.nii': '-cm blue'		                    # Binarized mask
}

# List of images to set max intensity to 70%
set_intensity_list = ['T1w.nii.gz', 'T2w.nii.gz', 'T2star.nii.gz', 'Mprage.nii.gz', 'MprageGd.nii.gz']
