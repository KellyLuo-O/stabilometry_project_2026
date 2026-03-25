# stabilometry_project_2026

## Motivation 

Research project supervised by Olivier Romain 
Part of CY University, Master ESI 2025-2026

This project investigates the use of dual FMCW radar sensors as a privacy-preserving, contact-free alternative to clinical force platforms for stabilometry. Two radars (9 GHz and 24 GHz) capture Anteroposterior (AP) and Mediolateral (ML) body sway simultaneously. Doppler velocity signals are processed to reconstruct pseudo-stabilograms, from which a full set of 73 postural control descriptors is computed and compared against a Zebris FDM force platform used as ground-truth reference.

This projet is about studying stabilometry with FMCW radar. 
The code in this repo is ainly about :
- extracting and processing FMCW radar 
- recovering pseudo stabilogram and therefore statokinesigram
- extract postural control metrics and descriptors

## Project Structure

```
stabilometry_project_2026/
│
├── data/                          # Raw acquisition files
│   ├── dataset1/                  # 10-second acquisitions (proof-of-concept)
│   └── dataset2/                  # 30-second acquisitions (ISPGR-compliant)
│
├── results/                       # All generated outputs
│   ├── figures/                   # Stabilograms, statokinesigrams, spectrograms
│   └── tables/                    # Descriptor comparison tables (CSV)
│
└── scripts/                       # All processing code
    ├── 01_radar_processing.ipynb          # Full radar signal processing pipeline
    ├── 02_radar_stabilogram.ipynb         # Pseudo-stabilogram reconstruction
    ├── 03_platform_stabilogram.ipynb      # Force platform signal extraction
    ├── 04_analyzing_descriptors.ipynb     # Descriptor computation and comparison
    │
    ├── radar/                             # Radar processing utility modules
    │   ├── parser.py                      # Binary .bin file parser (IQ deinterleaving)
    │   ├── range_fft.py                   # Range FFT and range-time matrix
    │   ├── build_mask_cfar_dp.py          # CFAR detector and target bin selection
    │   ├── cfar.py                        # CFAR threshold estimation
    │   ├── doppler.py                     # STFT-based Doppler spectrogram
    │   └── velocity.py                    # Peak velocity extraction from spectrogram
    │
    └── code_descriptors_postural_control/ # External library (Quijoux et al. 2021)
                                           # Computes all 73 CoP descriptors
```

---

## Main Scripts

| Notebook | Description |
|---|---|
| `01_radar_processing.ipynb` | Loads raw `.bin` files, applies Range FFT, MTI filter, CFAR detection, and STFT to extract the Doppler velocity signal for both radars. Exports velocity as CSV. |
| `02_radar_stabilogram.ipynb` | Integrates the exported velocity using the trapezoidal rule to reconstruct the pseudo-stabilogram (AP + ML). Centers the signal and plots stabilogram and statokinesigram. |
| `03_platform_stabilogram.ipynb` | Parses the `.xml` start timestamp, crops and synchronizes the `gait-line.csv` CoP signal from the Zebris platform, centers it, and plots the reference stabilogram. |
| `04_analyzing_descriptors.ipynb` | Computes the full set of 73 postural control descriptors on both the radar pseudo-stabilogram and the platform reference, then computes and reports relative errors. |

---

## Dataset

| Dataset | Acquisitions | Subject | Duration | Condition |
|---|---|---|---|---|
| Dataset 1 | Data 1 – 4 | Subject 1 | 10 s | Simulated large postural movements |
| Dataset 1 | Data 5 | Subject 2 | 10 s | Quiet standing |
| Dataset 2 | Data 1 – 7 | Subject 1 | 30 s | Quiet standing |
| Dataset 2 | Data 8 – 13 | Subject 1 | 30 s | Simulated large postural movements |

> Dataset 1 is primarily used for signal processing development and proof-of-concept validation.  
> Dataset 2 (30 s) complies with ISPGR recommendations and is used for the full descriptor comparison.

Each acquisition contains:
- `data#_ML.bin` or `/radar9/test#.bin` — raw IQ data from the 9 GHz radar (ML axis)
- `data#_AP.bin` or `/radar24/test#.bin` — raw IQ data from the 24 GHz radar (AP axis)
- `gait-line.csv` — time-stamped CoP coordinates from the Zebris FDM platform
- `config.xml` — acquisition metadata including the recording start timestamp

---

## Radar Parameters

| Parameter | 9 GHz radar (ML) | 24 GHz radar (AP) |
|---|---|---|
| Bandwidth | 400 MHz | 1000 MHz |
| Carrier frequency | 9.8 GHz | 25 GHz |
| Range resolution | 37.5 cm | 15 cm |
| Sweep time | 4 ms | 4 ms |
| Samples per chirp | 1024 | 1024 |

---

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

## References

- Quijoux et al. (2021) — *A review of center of pressure variables to quantify standing balance in elderly people: Algorithms and open-access code.* Physiological Reports. [doi:10.14814/phy2.15067](https://doi.org/10.14814/phy2.15067)
- Scoppa et al. (2012) — *Clinical stabilometry standardization.* Gait & Posture.
