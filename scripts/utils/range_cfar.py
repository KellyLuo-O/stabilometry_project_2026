import numpy as np
import matplotlib.pyplot as plt

from .build_mask_cfar_dp import build_mask_cfar_dp

def range_cfar(RADAR_PARAM,
               rangeFFT_data,
               MIN_RANGE_FOR_DOPPLER_DETECTION=0,
               MAX_RANGE_FOR_DOPPLER_DETECTION=5):

    # =========================
    # Axes temps et distance
    # =========================
    _, ns = rangeFFT_data.shape       # Nn de chprs pour l'échelle temps

    time_axis = np.arange(ns) * RADAR_PARAM["sweep_time"]
    freq_axis = np.arange(0, RADAR_PARAM["NTS"]//2) * (RADAR_PARAM["fs"] / RADAR_PARAM["NTS"])
    range_axis = (freq_axis * 3e8 * RADAR_PARAM["sweep_time"]) / (2 * RADAR_PARAM["bw"])

    # =========================
    # Range-Time plot
    # =========================
    plt.figure(figsize=(12,5))

    plt.imshow(
        20*np.log10(np.abs(rangeFFT_data)),
        aspect='auto',
        extent=[time_axis[0], time_axis[-1], range_axis[0], range_axis[-1]],
        origin='lower',
        cmap='jet',
        vmin=35,
    )

    plt.xlabel("Time (s)")
    plt.ylabel("Range (m)")
    plt.title("Range-Time")

    plt.colorbar(label="Power (dB)")
    plt.grid(True)

    # CFAR + piste + overlay

    dt_for_mask = RADAR_PARAM["sweep_time"]
    vmax = 2.0

    M, W, rhat, Thr, B = build_mask_cfar_dp(
        rangeFFT_data,
        range_axis,
        dt_for_mask,
        vmax,
        MinRange=MIN_RANGE_FOR_DOPPLER_DETECTION,
        MaxRange=MAX_RANGE_FOR_DOPPLER_DETECTION,
        Mode='SOCA',
        Train=8,
        Guard=2,
        Pfa=1e-3,
        BandHalfWidth=2,
        SoftSigma=0.8,
        SoftFloor=0.05
    )

    plt.imshow(
        M.astype(float),
        aspect='auto',
        origin='lower',
        extent=[time_axis.min(), time_axis.max(),
                range_axis.min(), range_axis.max()],
        cmap='jet',
        alpha=0.25
    )

    rhat_idx = np.array(rhat, dtype=float)
    rhat_idx[np.isnan(rhat_idx)] = 0
    rhat_idx = rhat_idx.astype(int)

    plt.plot(
        time_axis,
        range_axis[rhat_idx],
        'w-',
        linewidth=1.2
    )
    
    plt.ylim(0, MAX_RANGE_FOR_DOPPLER_DETECTION+2)
    plt.show()

    # === sélection des bins de distance ===

    bin_indl = np.where(range_axis >= MIN_RANGE_FOR_DOPPLER_DETECTION)[0][0]
    bin_indu = np.where(range_axis <= MAX_RANGE_FOR_DOPPLER_DETECTION)[0][-1]

    return M, W, bin_indl, bin_indu
    