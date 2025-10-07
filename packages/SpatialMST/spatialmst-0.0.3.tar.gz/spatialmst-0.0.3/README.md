# SpatialMST


[![image](https://img.shields.io/pypi/v/SpatialMST.svg)](https://pypi.python.org/pypi/SpatialMST)
[![image](https://img.shields.io/conda/vn/conda-forge/SpatialMST.svg)](https://anaconda.org/conda-forge/SpatialMST)

[![image](https://pyup.io/repos/github/SurajRepo/SpatialMST/shield.svg)](https://pyup.io/repos/github/SurajRepo/SpatialMST)


**Spatial Multimodal Self-supervised Transformer**
-   Free software: MIT License

## Installation
**Create environment**
```sh
conda create -n SpatialMSTEnv python=3.11
conda activate SpatialMSTEnv
```
**Install ipykernel**
```sh
conda install ipykernel
python -m ipykernel install --user --name SpatialMSTEnv --display-name "Python(SpatialMSTEnv)"
```
**Install POT: Python Optimal Transport**
```sh
conda install -c conda-forge pot
```
**Install Pytorch and pytorch-geometric**
```sh
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu129
pip install torch_geometric
```

### Install SpatialMST
PyPI package: https://pypi.org/project/SpatialMST
```sh
pip install SpatialMST
```

The source files for spMetaTME can be downloaded from the [Github repo](https://github.com/Angione-Lab/SpatialMST.git).

You can either clone the public repository:

```sh
git clone https://github.com/Angione-Lab/SpatialMST.git
```

Once you have a copy of the source, you can install it with:

```sh
cd spmetatme
uv pip install .
```
## Generate metabolic module flux rates and metabolite abundances for spatial transcriptomics using scFEA.
The estimated metabolic module flux rates and metabolite abundances construct the two modalities and the spatial transcriptomics data represents the third modality.

https://www.biorxiv.org/content/10.1101/2020.09.23.310656v1.full [Github link](https://github.com/changwn/scFEA/tree/master)

## Integrating spatial transcriptomics with metabolic module fluxes and metabolite abundance: 
[Tutorial on spatial multimodal integration and analysis](https://github.com/Angione-Lab/Multimodal_breast_cancer_subtype_analysis/tree/main/Spatial_multi_omics_analysis)

## Download the datasets from figshare
[Example dataset](https://figshare.com/ndownloader/articles/30290779/versions/1?folder_path=data_spatial)