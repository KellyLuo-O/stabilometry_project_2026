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
stabilometry_project_2026/
│
├── data/
│   ├── all_data/                   # unified dataset for the main analysis (5 acquisitions)
│   │   ├── data1_AP.bin … data5_AP.bin   # 9 GHz radar binary files (anteroposterior axis)
│   │   └── data1_ML.bin … data5_ML.bin   # 24 GHz radar binary files (mediolateral axis)
│   │
│   ├── antoine/                    # raw data from subject 1
│   │   ├── plateforme/
│   │   │   ├── test1.xml … test4.xml     # Zebris session metadata + start timestamp
│   │   │   └── test1/ … test4/           # Zebris CSV exports per acquisition
│   │   │       ├── gait-line.csv         # CoP trajectory (AP and ML, used for stabilogram)
│   │   │       ├── force-curve.csv
│   │   │       └── parameters.csv
│   │   ├── radar9/   test1.bin … test4.bin   # 9 GHz raw binary (AP axis)
│   │   └── radar24/  test1.bin … test4.bin   # 24 GHz raw binary (ML axis)
│   │
│   └── kelly/                      # raw data from subject 2
│       ├── A151P148R1S5D0.bin       # 9 GHz radar binary
│       ├── iq_tx12.bin              # 24 GHz radar binary
│       ├── plat.xml                 # Zebris session metadata
│       └── gait-line.csv            # Zebris CoP trajectory
│
├── results/
│   ├── platform_descriptors.csv    # 73 CoP variables computed from force platform
│   ├── radar_descriptors.csv       # 73 CoP variables computed from radar pseudo-stabilogram
│   ├── icc.csv                     # Intraclass Correlation Coefficients (radar vs platform)
│   ├── tables/
│   │   ├── data1_AP_velocity.csv … data5_ML_velocity.csv  # extracted velocity vectors per axis
│   ├── antoine/                    # intermediate results (position CSVs, stabilogram PNGs)
│   ├── kelly/                      # intermediate results (stabilogram + statokinesigram PNGs)
│   └── figures/                    # resulting figures
│
└── scripts/
    │
    ├── 01_radar_processing.ipynb       # Step 1: full radar pipeline
    │                                   #  reads .bin → parser → Range FFT → MTI → CFAR
    │                                   #  → Doppler STFT → velocity extraction
    │                                   #  → saves velocity CSVs to results/tables/
    │
    ├── 02_radar_stabilogram.ipynb      # Step 2: pseudo-stabilogram reconstruction
    │                                   #  loads velocity CSVs → dominant-frequency filter
    │                                   #  → trapezoidal integration → centering
    │                                   #  → plots stabilogram + statokinesigram
    │                                   #  → computes 73 descriptors → saves radar_descriptors.csv
    │
    ├── 03_platform_stabilogram.ipynb   # Step 3: reference stabilogram from Zebris
    │                                   #  parses .xml for start timestamp
    │                                   #  → crops + synchronises gait-line.csv
    │                                   #  → filters + centres CoP signal
    │                                   #  → plots stabilogram + statokinesigram
    │                                   #  → computes 73 descriptors → saves platform_descriptors.csv
    │
    ├── 04_analyzing_descriptors.ipynb  # Step 4: comparison and analysis
    │                                   #  loads radar_descriptors.csv + platform_descriptors.csv
    │                                   #  → computes relative error per variable per acquisition
    │                                   #  → computes ICC → saves icc.csv
    │                                   #  → generates comparison figures
    │
    ├── radar/                          # reusable radar signal processing package
    │   ├── parser.py                   # reads .bin, de-interleaves I/Q, reshapes to (NTS × N_Chirps)
    │   ├── range_fft.py                # Blackman-Harris window + colums-wise FFT → range-time matrix
    │   ├── cfar.py                     # CFAR detector: adaptive threshold → detected range bins
    │   ├── build_mask_cfar_dp.py       # builds the binary detection mask used by cfar.py
    │   ├── doppler.py                  # Hann window + STFT row-wise on target bins → spectrogram
    │   ├── velocity.py                 # extracts peak Doppler frequency → radial velocity vector
    │   └── __init__.py
    │
    ├── code_descriptors_postural_control/   # postural descriptor library (Quijoux et al. 2021)
    │   ├── descriptors/
    │   │   ├── positional.py           # RMS, range, ellipse area, mean distance, planar deviation…
    │   │   ├── dynamic.py              # mean velocity, mean frequency, sway area/s, fractal dim…
    │   │   ├── frequentist.py          # total power, 50%/95% power freq, centroidal freq…
    │   │   ├── stochastic.py           # SDA: diffusion coefficients, scaling exponents, critical time
    │   │   └── indices_corresp.py      # maps variable index → name (used for CSV column headers)
    │   ├── stabilogram/
    │   │   ├── stato.py                # stabilogram and statokinesigram plotting utilities
    │   │   └── swarii.py               # non-uniform resampling correction (for irregular sampling)
    │   └── constants/labels.py         # axis labels and variable name strings
    │
    └── tests/                          # legacy exploratory notebooks (kept for reference only)
        ├── radar_9GHz_processing.ipynb
        └── radar_24GHz_processong.ipynb
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
