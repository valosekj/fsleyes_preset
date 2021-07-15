# Run FSLeyes and automatically set display options

Jan Valosek, fMRI laboratory Olomouc, 2021

## Description

The script automatically set display options for FSLeyes viewer, e.g., 

```
fsleyes_preset.sh sub-01_T1w_seg.nii.gz
```

starts FSLeyes will following options:

```
fsleyes sub-01_T1w_seg.nii.gz -cm red -a 50
```

## Usage

1. Clone repo:

```
git clone https://github.com/valosekj/fsleyes_preset.git
```

2. Create virtual environment - manual [here](https://gist.github.com/valosekj/8052b227bd3f439a615a33804beaf37f#venv-enviroment)

3. Call python script using shell wrapper:

```
fsleyes_preset.sh <image_1.nii.gz> ... <image_X.nii.gz>
```

4. Create an alias to the scripts using `ln -s`, e.g.:

```
ln -s <PATH_TO_CLONED_REPO>/fsleyes_preset/fsleyes_preset.sh /usr/local/bin/fsleyes_preset.sh
```
