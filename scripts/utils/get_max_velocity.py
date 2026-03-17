import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_max_velocity(RADAR_PARAM, MD, doppler_data, output_filepath):
    """
    Plot the maw_velocity from given doppler specter data
    And save it into csv file
    """

    vel_axis = MD["DopplerAxis"] * 3e8 / (2 * RADAR_PARAM["fc"])

    num_time_bins = doppler_data.shape[1]
    vmax_time = np.zeros(num_time_bins)

    for k in range(num_time_bins):
        idx_max = np.argmax(doppler_data[:, k])  # index Doppler max
        vmax_time[k] = vel_axis[idx_max]           # vitesse correspondante

    # Créer un DataFrame et sauvegarder en CSV
    df = pd.DataFrame({
        "Time_s": MD["TimeAxis"],
        "Vmax_m_s": vmax_time
    })

    df.to_csv(output_filepath, index=False)

    # Tracer la vitesse maximale détectée
    plt.figure(figsize=(12,4))
    plt.plot(MD["TimeAxis"], vmax_time, linewidth=1.5)
    plt.grid(True)
    plt.xlabel("Temps (s)")
    plt.ylabel("Vitesse max (m/s)")
    plt.title("Vitesse maximale détectée")
    plt.show()

    