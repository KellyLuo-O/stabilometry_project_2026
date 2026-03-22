import numpy as np
from scipy.signal import lfilter
from scipy.signal.windows import blackmanharris

def range_fft(data):
    """
    Prend en argument la matrice de donnée 
    """
    NTS, num_chirps = data.shape

    # Fenêtre Blackman-Harris
    win = np.tile(blackmanharris(NTS), (num_chirps, 1)).T

    # Range FFT
    data_range = np.fft.fft(data * win, axis=0)

    # garder demi bande positive
    data_range = data_range[:NTS//2, :]

    # =========================
    # MTI filter (5-pulse canceler)
    # =========================
    filterCoeffs = np.array([1, 3, -2, -3, 1])
    data_range_MTI = lfilter(filterCoeffs, 1, data_range, axis=1)

    return data_range_MTI
