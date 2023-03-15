#!/bin/bash

#
# N.B. - This is only shell wrapper for python script fsleyes_preset.py
#
# Open FSLeyes and automatically set display options (such as -cm (colormap), -dr (display range), -a (opacity))
#
# Jan Valosek, fMRI laboratory Olomouc, 2021-2022
#

if [[ $# -eq 0 ]] || [[ $1 == "-h" ]];then
    echo -e "Open FSLeyes and automatically set display options (such as -cm (colormap), -dr (display range), -a (opacity))"
    echo -e "\nN.B. - This script is only shell wrapper for python script fsleyes_preset.py."
    echo -e "Jan Valosek, fMRI laboratory Olomouc, 2021-2022."
    echo -e "\nUSAGE:\n\t${0##*/} <image_1.nii.gz> ... <image_X.nii.gz>"
    echo -e "\nEXAMPLE:\n\t${0##*/} sub-001_T1w_seg.nii.gz sub-001_T1w_gmseg.nii.gz ..."
    echo -e "\t${0##*/} std1mm"
    echo -e "\t${0##*/} PAM50_t1"
    echo -e "\t${0##*/} PAM50_t2s"
else
    # Get absolute path to the directory where is located the python script and the venv
    if [[ ${SHELL} == "/bin/bash" ]];then
    	script_path=$(dirname $(realpath "$0"))
    elif [[ ${SHELL} == "/bin/zsh" ]];then
	script_path=$(dirname $(readlink "$0"))
    fi

    # Call python script and pass all input arguments
    "${script_path}"/venv/bin/python "${script_path}"/fsleyes_preset.py "$@"
fi
