#!/bin/bash

#
# N.B. - This is only shell wrapper for python script fsleyes_preset.py
#
# Open FSLeyes and automatically set display options (such as -cm (colormap), -dr (display range), -a (opacity))
#
# Jan Valosek, fMRI laboratory Olomouc, 2021
#

if [[ $# -eq 0 ]] || [[ $1 =~ "-h" ]];then
    echo -e "Open FSLeyes and automatically set display options (such as -cm (colormap), -dr (display range), -a (opacity))"
    echo -e "\nN.B. - This script is only shell wrapper for python script fsleyes_preset.py."
    echo -e "Jan Valosek, fMRI laboratory Olomouc, 2021."
    echo -e "\nUSAGE:\n\t${0##*/} <image_1.nii.gz> ... <image_X.nii.gz>"
    echo -e "\nEXAMPLE:\n\t${0##*/} sub-001_T1w_seg.nii.gz sub-001_T1w_gmseg.nii.gz ..."
else
    # Get path to the python script
    if [[ ${SHELL} == "/bin/bash" ]];then
    	script_path=$(dirname $(realpath -s "$0"))
    elif [[ ${SHELL} == "/bin/zsh" ]];then
	script_path=$(dirname $(readlink "$0"))
    fi

    # Call python script and pass all input arguments
    "${script_path}"/venv/bin/python "${script_path}"/fsleyes_preset.py "$@"
fi

