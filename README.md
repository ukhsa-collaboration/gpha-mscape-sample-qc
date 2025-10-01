# mscape-sample-qc

A repository containing code relating to per sample quality control of samples submitted to mscape. A climb ID is taken as input, and basic QC metrics are calculated for the
given sample. QC metrics are then added to an analysis table in Onyx in json format.

## Installation

Clone repo:
```
git clone git@github.com:ukhsa-collaboration/mscape-sample-qc.git
cd mscape-sample-qc
conda create -n mscape_sample_qc python
conda activate mscape_sample_qc
```

User installation:
`pip install .`

For developers:
`pip install -e ".[dev]"`

## Flags

| Flag              | Required? |      Description      |
|-------------------|-----------|-----------------------|
| --help, -h        |    No     | Display help message  |
| --input , -i      |    Yes    | Climb ID for sample   |
| --config, -c      |    No     | Specify QC metrics config file to use. If not specified, the default will be used |
| --output, -o      |    Yes     | Folder to save QC results to |
| --server, -s      |    Yes    |  Specify server code is being run on. Options: mscape, synthscape |
| --dry-run, -d     |    No     | Use this option to do a test upload and check for errors before attempting an upload to onyx |

## Usage

Example command using default config file and output to current directory:  
`qc_sample --input "C-1234" --output .`

Example command specifying config file and output directory path:  
`qc_sample --input "C-1234" --config /path/to/config/config_file.yaml --output /path/to/results/`
