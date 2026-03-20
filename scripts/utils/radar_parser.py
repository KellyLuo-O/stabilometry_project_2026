import numpy as np
import pandas as pd
import struct

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

    #################################################
    ###     Unpack the raw data into complex numbers
    #################################################

    ## nouveau chirp quand commence par HEADER
    HEADER = 49152

    # I/Q intercalés (pas de 2)
    I1 = raw_data[::2]
    Q1 = raw_data[1::2]

    # détection pertes
    header_index = np.where(I1 >= HEADER)[0]

    # suppression header
    I1[header_index] = I1[header_index] - HEADER

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


def radar24_parser(file):
    
    with open(file, "rb") as f: 
        # --- Header ---
        LASN = struct.unpack('<I', f.read(4))[0]
        LANT = struct.unpack('<I', f.read(4))[0]

        lenTx = struct.unpack('<I', f.read(4))[0]
        TxSelect = f.read(lenTx).decode('ascii')

        lenRx = struct.unpack('<I', f.read(4))[0]
        RxSelect = f.read(lenRx).decode('ascii')

        Freq_start = struct.unpack('<d', f.read(8))[0]
        Freq_stop = struct.unpack('<d', f.read(8))[0]
        Sweep_Time_Number = struct.unpack('<d', f.read(8))[0]
        NumSweeps = struct.unpack('<I', f.read(4))[0]
        LANR = struct.unpack('<I', f.read(4))[0]
        order = struct.unpack('<I', f.read(4))[0]
        reserved = struct.unpack('<I', f.read(4))[0]

        # --- Données I/Q intercalées ---
        N = LASN * NumSweeps

        # Lecture des paires I/Q intercalées
        raw = np.fromfile(f, dtype='<i2', count=2*N).astype(np.float64)
        print(raw.shape)
        if raw.size != 2*N:
            raise ValueError(f"Unexpected EOF while reading data (N={N})")

        I1 = raw[0::2]
        Q1 = raw[1::2]

        I1 = I1 - np.mean(I1)
        Q1 = Q1 - np.mean(Q1)
        
        # Reconstruction du complexe : I + jQ
        c = I1 + 1j*Q1
        c = (np.real(c) + hilbert(np.real(c)))

        # Remise en forme [LASN x NumSweeps]
        if order == 0:  # row-major
            radar_data = c.reshape((LASN, NumSweeps), order='F')
        else:  # column-major
            radar_data = c.reshape((NumSweeps, LASN), order='F').T

        radar_data = radar_data - np.mean(radar_data, axis=0)

        # --- Métadonnées ---
        RADAR_PARAM = {
            "NTS": LASN,
            "num_chirps": NumSweeps,
            "TxSelect": TxSelect,
            "RxSelect": RxSelect,
            "freq_start": Freq_start,
            "freq_stop": Freq_stop,
            "sweep_time": Sweep_Time_Number,
            "order": order,
            "bw": Freq_stop - Freq_start,
            "fc": Freq_start + (Freq_stop - Freq_start) / 2,
            "fs": LASN / Sweep_Time_Number
        }

    return RADAR_PARAM, radar_data