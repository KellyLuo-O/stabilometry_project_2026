import numpy as np
import pandas as pd

from scipy.signal import hilbert

def radar9_parser(file):

    # Read the CSV file
    radar_data = np.fromfile(file, dtype=np.uint16)
    
    ch = radar_data[1]
    frequ_start, frequ_stop = int(radar_data[2]*1e6), int(radar_data[3]*1e6)
    sweep_time = radar_data[4]/1e6
    NTS = int(radar_data[5])
    bw = frequ_stop - frequ_start
    fc = frequ_start + bw/2

    RADAR_PARAM = {
        "ch": ch,
        "frequ_start": frequ_start,
        "frequ_stop": frequ_stop,
        "sweep_time": sweep_time,
        "NTS": NTS,
        "bw": bw,
        "fc": fc,
        "fs": NTS / sweep_time
    }

    raw_data = radar_data[6:]
    num_chirps = int(np.floor((len(raw_data) / 2) / NTS))
    RADAR_PARAM["num_chirps"] = num_chirps


    # Unpack the raw data into complex numbers

    ## nouveau chirp quand commence par HEADER
    HEADER = 49152
    idx = np.where(raw_data >= HEADER)[0]

    start = idx[0]
    end = int(num_chirps * NTS * 2)

    # I/Q intercalés (pas de 2)
    I1 = raw_data[::2]
    Q1 = raw_data[1::2]

    # détection pertes
    header_index = np.where(I1 >= HEADER)[0]
    print(header_index)
    
    if np.any(np.diff(header_index) != NTS):
        print("ATTENTION: perte de données détectée.")

    # suppression header
    I1[header_index] = I1[header_index] - HEADER
    print(I1.shape)

    # centrage DC
    I1 = I1 - np.mean(I1)
    Q1 = Q1 - np.mean(Q1)

    data1 = I1 + 1j * Q1
    data1 = np.real(data1) + hilbert(np.real(data1))

    # Tronquer pour multiple de NTS
    data1 = data1[:NTS * num_chirps]

    # matrice [samples x chirps]
    radar_data = data1.reshape(NTS, num_chirps, order='F')

    return RADAR_PARAM, radar_data

  