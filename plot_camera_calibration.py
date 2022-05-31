"""
Plots a curve for how well the camera can estimate position of the AR tag as a function of distance from the camera
"""

import numpy as np
import matplotlib.pyplot as plt

INCH_TO_METERS = 0.0254

actual = np.arange(0.2, 1.6, 0.1)
measured_352x288 = 0.069/(2.5*INCH_TO_METERS)*np.array([0.1924, 0.298, 0.383, 0.473, 0.572, 0.662, 0.762, 0.867, 0.945, 1.03, 1.12, 1.21, 1.30, 1.39])  # I accidentally used the wrong measurement when testing
measured_640x480 = np.array([0.233, 0.313, 0.41, 0.508, 0.609, 0.724, 0.828, 0.929, 1.025, 1.125, 1.22, 1.313, 1.400, 1.52])
measured_1920x1080 = np.array([0.203, 0.302, 0.399, 0.498, 0.596, 0.69, 0.789, 0.889, 1.00, 1.08, 1.175, 1.28, 1.375, 1.475])
expected = actual

detection_labels = ["352x288", "640x480", "1920x1080"]
avg_detection_times = 1000*np.array([0.014413315331010455, 0.024098950268817202, 0.1323965751633987])
std_detection_times = 1000*np.array([0.007355659119345381, 0.005478367169663338, 0.022784556493893743])

fig, axs = plt.subplots(1, 2)
# axs[0].plot(actual, expected, label="Expected")
# axs[0].plot(actual, np.zeros(actual.shape), label="", lw=3, c='k')
axs[0].axhline(0, lw=2, c='k')
axs[0].plot(actual, measured_352x288 - actual, label="Measured, 352x288", lw=3)
axs[0].plot(actual, measured_640x480 - actual, label="Measured, 640x480", lw=3)
axs[0].plot(actual, measured_1920x1080 - actual, label="Measured, 1920x1080", lw=3)
axs[0].set_title("Apriltag Camera Calibration Error")
axs[0].set_xlabel("Actual Distance (m)")
axs[0].set_ylabel("Error, Measured Distance - Actual Distance (m)")
axs[0].grid(True)
axs[0].legend()

axs[1].bar(np.arange(len(avg_detection_times)), avg_detection_times, yerr=std_detection_times, align='center',
           alpha=0.5, ecolor='black', capsize=10, lw=2)
axs[1].set_ylabel("Detection Time (ms)")
axs[1].set_xticks(np.arange(len(avg_detection_times)))
axs[1].set_xticklabels(detection_labels)
axs[1].set_title("Apriltag Detection Time")
axs[1].yaxis.grid(True)
plt.tight_layout()

plt.show()
