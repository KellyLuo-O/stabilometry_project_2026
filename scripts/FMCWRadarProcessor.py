import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import get_window, spectrogram, lfilter, hilbert
from scipy.signal.windows import blackmanharris

from utils.build_mask_cfar_dp import build_mask_cfar_dp

class FMCWRadarProcessor :

    def __init__(self, filename):
        self.filename = filename
    
    def parse_radar_9_file(self):
        radar_data = np.fromfile(self.filename, dtype=np.uint16)

        self.ch = radar_data[1]
        self.frequ_start, self.frequ_stop = int(radar_data[2]*1e6), int(radar_data[3]*1e6)
        self.sweep_time = radar_data[4]/1e6
        self.NTS = int(radar_data[5])
        self.raw_data = radar_data[6:]

        self.num_chirps = np.floor((len(self.raw_data) / 2) / self.NTS)
        self.samp_rate = self.NTS / self.sweep_time
        self.dopp_freq = 1 / self.sweep_time

        HEADER = 49152
        idx = np.where(self.raw_data >= HEADER)[0]

        if len(idx) == 0:
            print("WARNING: Aucun header trouvé. Fichier ignoré.")
        else:
            self.raw_data[idx] = self.raw_data[idx] - HEADER
        
    
    def parse_radar_24_file(self):
        pass

    def extract_data(self):
        if hasattr(self, "raw_data"):
            print("No raw data, parse file first")
        
        I1 = I1 - np.mean(I1)
        Q1 = Q1 - np.mean(Q1)

        data1 = I1 + 1j * Q1
        data1 = np.real(data1) + hilbert(np.real(data1))

        return data1
        




        