import numpy as np
from utils_plot import GamePhase, initialize_curve
from scipy.spatial.distance import cdist
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

file = "data/20220530_13_40_45_userstudy_directional_feedback_user0.npy"
# file = "data/20220530_13_48_21_userstudy_directional_feedback_user0.npy"
file = "data/20220530_13_50_38_userstudy_directional_feedback_user0_blind.npy"
data = np.load(file, allow_pickle=True)

data, test_direction_values, actual_direction_values, test_times, return_times, final_vectors_to_center, playingCompletionTime, curve_ring = data
N = np.shape(data)[0]
print("Num Points", N)

camera2World = np.array([[0, 0, 1],
                         [-1, 0, 0],
                         [0, -1, 0]])  # change camera perspective to best viewing perspective

print(test_times, np.mean(test_times), np.std(test_times), np.max(test_times), np.min(test_times))
print(return_times, np.mean(return_times), np.std(return_times), np.max(return_times), np.min(return_times))

statuses = np.reshape([status for status, currTime, num_loop, pose_t, pose_R, inside in data], (N,))
positions = np.transpose(np.matmul(camera2World, np.transpose(
    np.reshape([pose_t for status, currTime, num_loops, pose_t, pose_R, inside in data], (N, 3)))))
print(positions.shape)

for i in range(len(actual_direction_values)):
    if actual_direction_values[i] == -4:
        actual_direction_values[i] = 4

points_y = {sector: [] for sector in np.arange(-3, 5)}
points_z = {sector: [] for sector in np.arange(-3, 5)}
for i in range(N):
    if statuses[i] == GamePhase.Playing:
        # points_y[test_direction_values[i]].append(positions[i, 1])
        # points_z[test_direction_values[i]].append(positions[i, 2])
        points_y[test_direction_values[0]].append(positions[i, 1])
        points_z[test_direction_values[0]].append(positions[i, 2])

print(points_y)
print(points_z)

# for sector in np.arange(-3, 5):
#     plt.plot(points_y[sector], points_z[sector])
# plt.show()
conf_matrix = confusion_matrix(test_direction_values, actual_direction_values)

# https://vitalflux.com/python-draw-confusion-matrix-matplotlib/
fig, ax = plt.subplots(figsize=(7.5, 7.5))
ax.matshow(conf_matrix, cmap=plt.get_cmap("Blues"), alpha=0.3)
for i in range(conf_matrix.shape[0]):
    for j in range(conf_matrix.shape[1]):
        ax.text(x=j, y=i, s=conf_matrix[i, j], va='center', ha='center', size='xx-large')

plt.xlabel('Direction Human Went', fontsize=18)
plt.ylabel('Direction of Vibration', fontsize=18)
plt.title('Confusion Matrix', fontsize=18)
plt.show()
