# Kontiguity: tool for eukaryotes contigs retrieval from genomic data and classification

Kontiguity is a python and bash pipeline created to retrieve unidentified contigs from eukaryotes genomic data, and to classify said contigs based on genomic contact data (Hi-C).

## Installation

```bash
pip install kontiguity
```

For development:

```bash
git clone https://github.com/Mae-4815162342/kontiguity.git
cd kontiguity
pip install -e .
```

## Presenting pipeline

Kontiguity is based on a pipeline of three subfunctions:

- **load** which serves data retrieval and formating, and provides a scrapping method to build a dataset from DToL (ref to add).

- **retrieve** for the retrieval of new contigs from WGS reads aligned on a reference genome (by default produces Hi-C maps for the further step, can be deactivated).

- **classify** for the contigs contacts classification, based on a plasmid-detection-oriented model at this day (a larger model can be provided later.)

Those three functions can be called individually or in order with the **pipeline** command, which provides an option to start at any step.

## Usage

### Loading a dataset

```bash
kontiguity load -n Saccaromyces_cerevisiae -r S_cerevisiae.fa 
```


## Outputs

TODO

## Classification model

TODO