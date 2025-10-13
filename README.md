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
| --no-onyx         |    No     | Use this option to write QC results to file with no onyx steps |
| --store-onyx      |    No     | Use this option to write QC results to file and create an onyx analysis object that is written to file for later upload |
| --test-onyx         |    No     | Use this option to write QC results to file and test submitting an onyx analysis object to onyx |
| --prod-onyx         |    No     | Use this option to write QC results to file and submit an onyx analysis object to onyx |


## Usage

Example command using default config file and output QC results file to current directory:
`qc_sample --input <sample_id> --output . --server "synthscape" --no-onyx`

Example command specifying config file and output dir, and testing submission to onyx:
`qc_sample --input  --config </path/to/config/config_file.yaml> --output </path/to/results/> --server synthscape --test-onyx`
