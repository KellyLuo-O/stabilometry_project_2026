import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import get_window, spectrogram

def plot_dopler(RADAR_PARAM, MD, doppler_data):
    time_axis = np.linspace(
        0,
        RADAR_PARAM["num_chirps"] * RADAR_PARAM["sweep_time"],
        doppler_data.shape[1]
    )
    vel_axis = MD["DopplerAxis"] * 3e8 / (2 * RADAR_PARAM["fc"])

    fig, ax = plt.subplots(figsize=(10,6))

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


def get_doppler(RADAR_PARAM, MD, range_FFT, M, W, bin_indl, bin_indu):
    
    # === paramètres STFT ===

    N_SFFT_points = 256
    Pad_Factor = 4
    OverlapFactor = 0.95

    window2 = get_window('hann', N_SFFT_points)

    use_soft_mask = False

    # === sélection des lignes (bins distance) ===

    rows = np.arange(bin_indl, bin_indu + 1)

    if "M" in locals() and M is not None:
        active = np.any(M[rows, :], axis=1)
        rows = rows[active]

        if len(rows) == 0:
            rows = np.arange(bin_indl, bin_indu + 1)


    # === calcul spectrogramme Doppler ===

    data_spec_MTI2 = 0

    for RBin in rows:

        if use_soft_mask:
            x = range_FFT[RBin, :] * W[RBin, :]
        else:
            x = range_FFT[RBin, :].copy()
            x[~M[RBin, :]] = 0

        f, t, S = spectrogram(
            x,
            window=window2,
            noverlap=int(OverlapFactor * N_SFFT_points),
            nfft=Pad_Factor * N_SFFT_points,
            mode="magnitude"
        )

        S = np.fft.fftshift(S, axes=0)

        data_spec_MTI2 += np.abs(S)

    # === inversion + normalisation ===

    data_spec_MTI2 = np.flipud(data_spec_MTI2)

    MaxVal = np.max(data_spec_MTI2)
    MinVal = np.min(data_spec_MTI2)

    if MaxVal > MinVal:
        data_spec_MTI2 = (data_spec_MTI2 - MinVal) / (MaxVal - MinVal)

    return data_spec_MTI2