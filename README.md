# stabilometry_project_2026

## Motivation 

Research project supervised by Olivier Romain 
Part of CY University, Master ESI 2025-2026

This projet is about studying stabilometry with FMCW radar. 
The code in this repo is ainly about :
- extracting and processing FMCW radar 
- recovering pseudo stabilogram and therefore statokinesigram
- extract postural control metrics and descriptors

## File organization 

```bash
stabilogram_extraction/
└── data/                       # Directory containing radar and force platform measurements
    └── antoine/                # Directory containing measurements of subject Antoine
    └── kelly/                  # Directory containing measurements of subject Kelly
└── results/                    # Directory containing result figures
└── scripts/                    # Direcotry containing program sripts
    └── utils/                  # Direcotry containing utils functions
    └── code_descriptors_postural_control 
└── README.md          # Documentation principale

stabilogram_extraction/
├───data                        # Directory containing radar and force platform measurements
│   ├───antoine                 # Directory containing measurements of subject Antoine
│   │   ├───plateforme
│   │   ├───radar24
│   │   └───radar9
│   └───kelly                   # Directory containing measurements fo subject Kelly 
├───results                     # Directory containing result figures
│   ├───antoine
│   └───kelly
└───scripts                     # Directory containing all program scrpits
    ├───code_descriptors_postural_control     # librairy for postural control metrics
    │   ├───constants
    │   ├───descriptors
    │   └───stabilogram
    ├───utils
    │   ├───build_mask_cfar_dp.py
    │   ├───get_dopler.py
    │   ├───get_max_velocity.py
    │   ├───get_range.py
    │   ├───radar_parser.py
    │   └───range_cfar.py
    ├───radar_9GHz_processing.ipynb     # Jupyter notebook for radar (9GHz) processing
    ├───radar_24GHz_processing.ipynb    # Jupyter notebook for radar (24GHz) processing
    ├───radar_processing_clean.ipynb    # Jupyter notebook for processing both radar
    ├───radar_stabilogram.ipynb         # Jupyter notebook recovering pseudo stabilogram from velocity
    └───platform_stabilogram.py         # Jupyter notebook for vizualizing analyzing data from force plateform

```

## Method 

### Data processing of FMCW radar data

- Extraction:
    - Unpacking data unto complex data 
    - Reshaping data into matric of NTS (Number of Time Sample) X Number of Chirps

- Range FFT:
    - Filtering with Blackman Harris window
    - FFT over each sample to the Range FFT
    - Moving Target Indicator (MTI) filter (cancelling static noises)

- Constant False Alarm (CFAR) detection on the range
    - Get bins of target

- Dopler Spectre
    - Filtering with hann window
    - STFT of bins of target to get Doppler focused on target
    - MTI filter 

- Velocity Extraction
    - Extracting max velocity from dopler, representing center of body
    - exporting into csv file 

### Pseudo stabilogram recovering from radar 

- Extracting the velocity from previous data processing
- Derivate to get postition 
- Center
- Plot statbilogram, statokinesigram
- Extract postural control metrics and descriptors 

### Stabilogram from force platform

- Get synchro time from .xml file 
- Get synchronized measure from gait-line.csv
- Center
- Plot stabilogram, statokinesigram 
- extract postural control metrics and descriptors 