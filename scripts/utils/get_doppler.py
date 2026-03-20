import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import spectrogram
from scipy.signal.windows import hann

def plot_dopler(RADAR_PARAM, MD, doppler_data):

    time_axis = np.linspace(
        0,
        RADAR_PARAM["num_chirps"] * RADAR_PARAM["sweep_time"],
        doppler_data.shape[1]
    )
    vel_axis = MD["DopplerAxis"] * 3e8 / (2 * RADAR_PARAM["fc"])

    fig, ax = plt.subplots(figsize=(12,6))

    im = ax.imshow(
        20*np.log10(np.abs(doppler_data)),
        aspect='auto',
        origin='lower',
        extent=[time_axis[0], time_axis[-1],
                vel_axis[0], vel_axis[-1]],
        cmap='jet',
        vmin=-40,
        vmax=0
    )

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Power (dB)")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Velocity (m/s)")

    plt.show()


def get_doppler(RADAR_PARAM, range_FFT, M, W, bin_indl, bin_indu):

    
    # === paramètres STFT ===

    N_SFFT_points = 256
    Pad_Factor = 4
    OverlapFactor = 0.95

    window2 = hann(N_SFFT_points, sym=False)

    use_soft_mask = True

    # === sélection des lignes (bins distance) ===

    rows = np.arange(bin_indl, bin_indu + 1)

    # if "M" in locals() and M is not None:
    #     active = np.any(M[rows, :], axis=1)
    #     rows = rows[active]

    #     if len(rows) == 0:
    #         rows = np.arange(bin_indl, bin_indu + 1)

    if 'M' is not None and M.size > 0:
        rows_masked = rows[np.any(M[rows, :], axis=1)]
        if rows_masked.size > 0:
            rows = rows_masked

    # === calcul spectrogramme Doppler ===

    data_spec_MTI2 = None

    for RBin in rows:

        if use_soft_mask:
            x = range_FFT[RBin, :] * W[RBin, :]
        else:
            x = range_FFT[RBin, :].copy()
            x[~M[RBin, :]] = 0

        f, t, S = spectrogram(
            x,
            window=window2,
            fs=1 / RADAR_PARAM["sweep_time"],
            noverlap=int(OverlapFactor * N_SFFT_points),
            nfft=Pad_Factor * N_SFFT_points,
            mode='complex',
            scaling='spectrum'
        )
        S = np.fft.fftshift(S, axes=0)
        if data_spec_MTI2 is None:
            data_spec_MTI2 = np.abs(S)
        else:
            data_spec_MTI2 += np.abs(S)
    
    # === inversion + normalisation ===

    data_spec_MTI2 = np.flipud(data_spec_MTI2)

    MaxVal = np.max(data_spec_MTI2)
    MinVal = np.min(data_spec_MTI2)

    if MaxVal > MinVal:
        data_spec_MTI2 = (data_spec_MTI2 - MinVal) / (MaxVal - MinVal)

    
    # === paramètres Doppler ===

    MD = {}

    MD["PRF"] = 1 / RADAR_PARAM["sweep_time"]
    MD["TimeWindowLength"] = 256
    MD["OverlapFactor"] = 0.95
    MD["OverlapLength"] = round(MD["TimeWindowLength"] * MD["OverlapFactor"])

    MD["Pad_Factor"] = 4
    MD["FFTPoints"] = MD["Pad_Factor"] * MD["TimeWindowLength"]

    MD["DopplerBin"] = MD["PRF"] / data_spec_MTI2.shape[0]
    MD["DopplerAxis"] = np.arange(-MD["PRF"]/2, MD["PRF"]/2, MD["DopplerBin"])
    MD["WholeDuration"] = range_FFT.shape[1] / MD["PRF"]

    MD["TimeAxis"] = np.linspace(0, MD["WholeDuration"], data_spec_MTI2.shape[1])


    return MD, data_spec_MTI2
