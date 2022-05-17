# Run FSLeyes and automatically set display options

Jan Valosek, fMRI laboratory Olomouc, 2021 - 2022

## Description

The script automatically set display options for [FSLeyes](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSLeyes) viewer.

## Current features

1. Set display options (such as colormap, display range or opacity), e.g.:

```console
fsleyes_preset.sh sub-01_T1w_seg.nii.gz
# starts FSLeyes will following options:
fsleyes sub-01_T1w_seg.nii.gz -cm red -a 50
```

2. Set maximum intensity for structural images (such as T1w or T2w) to 70%, e.g.:

```console
fsleyes_preset.sh sub-01_T1w.nii.gz
# starts FSLeyes will following options:
fsleyes sub-01_T1w.nii.gz -dr 0 <max * 0.7>
```

3. Open all `.nii` and `.nii.gz` files from given directory and ignore all other files (such as json, yml, etc.), e.g.:

```console
fsleyes_preset.sh *
# starts FSLeyes will following options:
fsleyes sub-01_T1w_seg.nii.gz -cm red -a 50 sub-01_T1w.nii.gz -dr 0 <max * 0.7>
```

## Installation and usage

1. Clone repo:

```shell
git clone https://github.com/valosekj/fsleyes_preset.git
```

2. Create a virtual environment and install requirements - manual [here](https://gist.github.com/valosekj/8052b227bd3f439a615a33804beaf37f#venv-enviroment)

3. Run the script (shell wrapper calls python script ):

```
fsleyes_preset.sh <image_1.nii.gz> ... <image_X.nii.gz>
```

4. Create an alias using `ln -s`  to the directory with scripts (e.g., `/usr/local/bin`) to include `fsleyes_preset.sh` to your `$PATH` variable:

```
ln -s <PATH_TO_CLONED_REPO>/fsleyes_preset/fsleyes_preset.sh /usr/local/bin/fsleyes_preset.sh
```

5. Optionally, you can create an alias in your `rc` file (`.bashrc` or `.zshrc`) to start script only by typing `ff`:

```shell
alias ff='fsleyes_preset.sh'
# or if you do not want to get errors into CLI
alias ff='fsleyes_preset &> /dev/null'
```

6. Make repo up to date:

```shell
git pull
```
