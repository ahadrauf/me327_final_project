import numpy as np
from utils_plot import GamePhase, initialize_curve
from scipy.spatial.distance import cdist
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

file = "data/20220530_13_40_45_userstudy_directional_feedback_user0.npy"
# file = "data/20220530_13_48_21_userstudy_directional_feedback_user0.npy"
# file = "data/20220530_13_50_38_userstudy_directional_feedback_user0_blind.npy"
file = "data/20220601_08_48_13_userstudy_visual_user1.npy"
normal_files = ["data/20220601_10_25_17_userstudy_visual_user2.npy",
                "data/20220601_11_32_29_userstudy_visual_user2.npy",
                "data/20220601_11_53_25_userstudy_visual_user3.npy"]
blind_files = ["data/20220601_10_35_24_userstudy_blind_user2.npy",
               "data/20220601_11_40_42_userstudy_blind_user2.npy",
               "data/20220601_12_01_18_userstudy_blind_user3.npy"]
all_test_directions = np.array([])
all_actual_directions = np.array([])

normal_test_times = []
blind_test_times = []

for file in normal_files:
    data = np.load(file, allow_pickle=True)

    data, test_direction_values, actual_direction_values, test_times, return_times, final_vectors_to_center, playingCompletionTime, curve_ring = data
    N = np.shape(data)[0]
    print("Num Points", N)

    camera2World = np.array([[0, 0, 1],
                             [-1, 0, 0],
                             [0, -1, 0]])  # change camera perspective to best viewing perspective

    print("Test Times", test_times, np.mean(test_times), np.std(test_times), np.max(test_times), np.min(test_times))
    print(return_times, np.mean(return_times), np.std(return_times), np.max(return_times), np.min(return_times))

    statuses = np.reshape([status for status, test_num, currTime, num_loop, pose_t, pose_R, inside in data], (N,))
    positions = np.transpose(np.matmul(camera2World, np.transpose(
        np.reshape([pose_t for status, test_num, currTime, num_loops, pose_t, pose_R, inside in data], (N, 3)))))
    test_nums = np.reshape([test_num for status, test_num, currTime, num_loop, pose_t, pose_R, inside in data], (N,))
    print(positions.shape)

    for i in range(len(actual_direction_values)):
        if actual_direction_values[i] == -4:
            actual_direction_values[i] = 4

    all_test_directions = np.append(all_test_directions, test_direction_values)
    all_actual_directions = np.append(all_actual_directions, actual_direction_values)
    normal_test_times += test_times

    points_y = {sector: [] for sector in np.arange(-3, 5)}
    points_z = {sector: [] for sector in np.arange(-3, 5)}
    cardinal_directions = ["BL", "B", "BR", "R", "TR", "T", "TL", "L"]
    for i in range(N):
        if statuses[i] == GamePhase.Playing:
            points_y[test_direction_values[test_nums[i]]].append(positions[i, 1])
            points_z[test_direction_values[test_nums[i]]].append(positions[i, 2])
            # points_y[test_direction_values[0]].append(positions[i, 1])
            # points_z[test_direction_values[0]].append(positions[i, 2])

    print(points_y)
    print(points_z)

    # for sector in np.arange(-3, 5):
    #     plt.plot(points_y[sector], points_z[sector], label=cardinal_directions[sector + 3])
    # plt.legend()
    # plt.show()

print(all_test_directions)
print(all_actual_directions)
print("Accuracy of visual", np.count_nonzero(all_test_directions == all_actual_directions) / len(all_test_directions))
conf_matrix = confusion_matrix(all_test_directions, all_actual_directions)

# https://vitalflux.com/python-draw-confusion-matrix-matplotlib/
fig, ax = plt.subplots(figsize=(7.5, 7.5))
ax.matshow(conf_matrix, cmap=plt.get_cmap("Blues"), alpha=0.3)
for i in range(conf_matrix.shape[0]):
    for j in range(conf_matrix.shape[1]):
        ax.text(x=j, y=i, s=conf_matrix[i, j], va='center', ha='center', size='xx-large')

plt.xlabel('Direction Human Went', fontsize=18)
plt.ylabel('Direction of Vibration', fontsize=18)
ax.xaxis.set_ticks(range(8))
ax.yaxis.set_ticks(range(8))
ax.xaxis.set_ticklabels(cardinal_directions)
ax.yaxis.set_ticklabels(cardinal_directions)
plt.title('Confusion Matrix, Visual Interface Only\n(No Haptic Feedback) (N = 3)', fontsize=18)

all_test_directions = np.array([])
all_actual_directions = np.array([])
for file in blind_files:
    data = np.load(file, allow_pickle=True)

    data, test_direction_values, actual_direction_values, test_times, return_times, final_vectors_to_center, playingCompletionTime, curve_ring = data
    N = np.shape(data)[0]
    print("Num Points", N)

    camera2World = np.array([[0, 0, 1],
                             [-1, 0, 0],
                             [0, -1, 0]])  # change camera perspective to best viewing perspective

    print("Test Times", test_times, np.mean(test_times), np.std(test_times), np.max(test_times), np.min(test_times))
    print(return_times, np.mean(return_times), np.std(return_times), np.max(return_times), np.min(return_times))

    statuses = np.reshape([status for status, test_num, currTime, num_loop, pose_t, pose_R, inside in data], (N,))
    positions = np.transpose(np.matmul(camera2World, np.transpose(
        np.reshape([pose_t for status, test_num, currTime, num_loops, pose_t, pose_R, inside in data], (N, 3)))))
    test_nums = np.reshape([test_num for status, test_num, currTime, num_loop, pose_t, pose_R, inside in data], (N,))
    print(positions.shape)

    for i in range(len(actual_direction_values)):
        if actual_direction_values[i] == -4:
            actual_direction_values[i] = 4

    all_test_directions = np.append(all_test_directions, test_direction_values)
    all_actual_directions = np.append(all_actual_directions, actual_direction_values)
    blind_test_times += test_times

    points_y = {sector: [] for sector in np.arange(-3, 5)}
    points_z = {sector: [] for sector in np.arange(-3, 5)}
    cardinal_directions = ["BL", "B", "BR", "R", "TR", "T", "TL", "L"]
    for i in range(N):
        if statuses[i] == GamePhase.Playing:
            points_y[test_direction_values[test_nums[i]]].append(positions[i, 1])
            points_z[test_direction_values[test_nums[i]]].append(positions[i, 2])
            # points_y[test_direction_values[0]].append(positions[i, 1])
            # points_z[test_direction_values[0]].append(positions[i, 2])

    print(points_y)
    print(points_z)

    # for sector in np.arange(-3, 5):
    #     plt.plot(points_y[sector], points_z[sector], label=cardinal_directions[sector + 3])
    # plt.legend()
    # plt.show()

print(all_test_directions)
print(all_actual_directions)
conf_matrix = confusion_matrix(all_test_directions, all_actual_directions)
print("Accuracy of haptic", np.count_nonzero(all_test_directions == all_actual_directions) / len(all_test_directions))

# https://vitalflux.com/python-draw-confusion-matrix-matplotlib/
fig, ax = plt.subplots(figsize=(7.5, 7.5))
ax.matshow(conf_matrix, cmap=plt.get_cmap("Blues"), alpha=0.3)
for i in range(conf_matrix.shape[0]):
    for j in range(conf_matrix.shape[1]):
        ax.text(x=j, y=i, s=conf_matrix[i, j], va='center', ha='center', size='xx-large')

plt.xlabel('Direction Human Went', fontsize=18)
plt.ylabel('Direction of Vibration', fontsize=18)
ax.xaxis.set_ticks(range(8))
ax.yaxis.set_ticks(range(8))
ax.xaxis.set_ticklabels(cardinal_directions)
ax.yaxis.set_ticklabels(cardinal_directions)
plt.title('Confusion Matrix, Directional Haptic Feedback Only\n(No Visual Interface) (N = 3)', fontsize=18)


fig, ax = plt.subplots(figsize=(5, 7.5))
test_times = [np.mean(normal_test_times), np.mean(blind_test_times)]
test_std = [np.mean(normal_test_times), np.std(blind_test_times)]
ax.bar(range(len(test_times)), test_times, width=0.3, yerr=test_std, capsize=5)
ax.set_xticks(range(len(test_times)))
ax.set_xticklabels(["Visual Interface Only,\nNo Haptic Feedback", "Directional Haptic Feedback Only\nNo Visual Interface"])
# plt.legend()
ax.set_ylabel("Time (s)")
plt.title("Time Taken to Move to Virtual Wire")
plt.tight_layout()

plt.show()
