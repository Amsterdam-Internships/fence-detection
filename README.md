## Fence Detection in Amsterdam with Segmentation Models
Research internship with the Gemeente Amsterdam concerning the detection of fencing along open water within the city center.

![Fences in Amsterdam](media/figure-amsterdam.pdf)


---


## Project Folder Structure

There are the following folders in the structure:

1) [`data`](./data): Placeholder that should contain the annotated dataset and geometry
1) [`experiments`](./experiments): Placeholder for train- and validation-logs and model weights
1) [`loaders`](./loaders): Folder containing the panorama- and dataloaders for training
1) [`models`](./models): Folder containing the models and training code
1) [`notebooks`](./notebooks): Folder containing Jupyter Notebooks for visualizations
1) [`scripts`](./notebooks): Folder containing scripts for inference, annotation converters, and data splits
1) [`utils`](./notebooks): Folder containing augmentation, logging, metrics, and other functions

---


## Installation
1) Clone this repository:
    ```bash
    git clone https://github.com/Amsterdam-Internships/fence-detection
    ```
1) Install all dependencies:
    ```bash
    pip install -r requirements.txt
    ```
---


## Usage

To create the visualisation linked above, run [inference.py](./scripts/inference.py) (params can be adjusted in the file itself). This creates a GeoJSON file which can be read and plotted accordingly. The visualisation linked above was made using the notebook [visualisation-predictions.ipynb](./notebooks/visualisation-predictions.ipynb).

## Training a Model
To train a model, we refer to the [models](./models) folder. Model parameters, dataset references, and output directories can be specified in [config.py](./models/config.py). Then simply run [train.py](./models/train.py).

<!-- ## How it works -->


## Acknowledgements

Our segmentation models use [Segmentation Models for PyTorch](https://github.com/qubvel/segmentation_models.pytorch) by [qubvel](https://github.com/qubvel/): 