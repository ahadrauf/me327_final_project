import numpy as np
from utils_plot import GamePhase, initialize_curve
from scipy.spatial.distance import cdist
from datetime import datetime
import matplotlib.pyplot as plt

import os

list_of_files = []

for root, dirs, files in os.walk("data/"):
    for file in files:
        list_of_files.append(os.path.join(root, file))

# file = "data/20220531_09_00_33_demo_user1.npy"
all_data = {}

for file in list_of_files:
    if not ("demo_user" in file and "demo_user0" not in file):
        continue

    data = np.load(file, allow_pickle=True)

    # data, num_inside, num_outside, num_inside_while_playi5ng, num_outside_while_playing, playingCompletionTime = data
    data, num_inside, num_outside, num_inside_while_playing, num_outside_while_playing, playingCompletionTime, curve = data
    N = np.shape(data)[0]
    print("Num Points", N)

    # x_min, x_max = 0.25, 1.2
    # curve_y = lambda x: 0.0
    # # curve_y = lambda x: 0.025*(np.sin(5*x) + np.cos(6*x))
    # curve_z = lambda x: 0.075*(np.sin(7*x) + np.cos(3*x))
    # curve, curve_midpoints = initialize_curve(x_min, x_max, curve_y, curve_z, N=100)

    # status, datetime.now(), num_loops, tags[0].pose_t, tags[0].pose_R, inside
    # times = np.reshape([time for status, time, num_loop, pose_t, pose_R, inside in data], (N,))
    # statuses = np.reshape([status for status, time, num_loop, pose_t, pose_R, inside in data], (N,))
    # positions = np.reshape([pose_t for status, time, num_loop, pose_t, pose_R, inside in data], (N, 3))
    # insides = np.reshape([inside for status, time, num_loop, pose_t, pose_R, inside in data], (N,))
    times = np.reshape([time for directional, curve_num, status, time, num_loop, pose_t, pose_R, inside in data], (N,))
    statuses = np.reshape([status for directional, curve_num, status, time, num_loop, pose_t, pose_R, inside in data],
                          (N,))
    positions = np.reshape([pose_t for directional, curve_num, status, time, num_loop, pose_t, pose_R, inside in data],
                           (N, 3))
    insides = np.reshape([inside for directional, curve_num, status, time, num_loop, pose_t, pose_R, inside in data],
                         (N,))
    directions = np.reshape(
        [directional for directional, curve_num, status, time, num_loop, pose_t, pose_R, inside in data],
        (N,))

    camera2World = np.array([[0, 0, 1],
                             [-1, 0, 0],
                             [0, -1, 0]])  # change camera perspective to best viewing perspective

    num_collisions = 0
    num_inside_while_playing_total = 0
    num_outside_while_playing_total = 0
    completion_time = 0
    completion_distance = 0
    deviations = []
    mean_deviation = 0
    speeds = []
    avg_speed = 0
    start_time_navigate_to_origin = 0
    end_time_navigate_to_origin = 0
    start_time_playing = 0
    end_time_playing = 0
    num_rounds = 0
    directional = True

    curve_length = 0
    for i in range(len(curve) - 1):
        curve_length += np.linalg.norm(curve[i + 1] - curve[i])

    for i in range(N):
        pos = np.matmul(camera2World, positions[i])
        if (i > 0) and (statuses[i - 1] == GamePhase.Exploring) and (statuses[i] == GamePhase.NavigatingToOrigin):
            start_time_navigate_to_origin = times[i]
        elif (i > 0) and (statuses[i - 1] == GamePhase.NavigatingToOrigin) and (statuses[i] == GamePhase.Playing):
            end_time_navigate_to_origin = times[i]

        if (i > 0) and (statuses[i - 1] == GamePhase.NavigatingToOrigin) and (statuses[i] == GamePhase.Playing):
            start_time_playing = times[i]
        elif (i > 0) and (statuses[i - 1] == GamePhase.Playing) and (statuses[i] == GamePhase.Exploring):
            end_time_playing = times[i]
            # break  # stop counting after first play session
            print("ROUND", num_rounds)
            print("Num Points Per Time", N/(times[-1] - times[0]).total_seconds())
            print("Navigation Time", (end_time_navigate_to_origin - start_time_navigate_to_origin).total_seconds(), "s")
            print("Completion Time", (end_time_playing - start_time_playing).total_seconds(), "s")
            print("Percent Inside",
                  100*num_inside_while_playing_total/(num_inside_while_playing_total + num_outside_while_playing_total),
                  "%")
            print("Completion Distance", completion_distance, "m")
            print("Curve Length", curve_length, "m")
            # print("Average Speed", np.mean(speeds), np.std(speeds), "m/s")
            print("Average Speed", completion_distance/((end_time_playing - start_time_playing).total_seconds()))
            print("Mean Deviation", np.mean(deviations), np.std(deviations), "m")
            print("Directional Feedback", directions[i - 1])
            print("----------------------------")

            if file not in all_data:
                all_data[file] = []
            all_data[file] += [(N/(times[-1] - times[0]).total_seconds(),
                                (end_time_navigate_to_origin - start_time_navigate_to_origin).total_seconds(),
                                (end_time_playing - start_time_playing).total_seconds(),
                                100*num_inside_while_playing_total/(
                                        num_inside_while_playing_total + num_outside_while_playing_total),
                                completion_distance,
                                curve_length,
                                completion_distance/((end_time_playing - start_time_playing).total_seconds()),
                                np.mean(deviations),
                                np.std(deviations),
                                directions[i - 1])]
            num_rounds += 1

        if statuses[i] != GamePhase.Playing:
            continue
        if (i < N - 1) and insides[i] and not insides[i + 1]:
            num_collisions += 1

        if insides[i]:
            num_inside_while_playing_total += 1
        else:
            num_outside_while_playing_total += 1

        if i > 0:
            last_pos = np.matmul(camera2World, positions[i - 1])
            completion_distance += np.linalg.norm(pos - last_pos)
            speeds += [np.linalg.norm(pos - last_pos)/(times[i] - times[i - 1]).total_seconds()]

        deviations += [np.min(cdist(curve, np.array([pos])))]

print(all_data)

# print("Num Points Per Time", N/(times[-1] - times[0]).total_seconds())
# print("Navigation Time", (end_time_navigate_to_origin - start_time_navigate_to_origin).total_seconds(), "s")
# print("Completion Time", (end_time_playing - start_time_playing).total_seconds(), "s")
# print("Percent Inside",
#       100*num_inside_while_playing_total/(num_inside_while_playing_total + num_outside_while_playing_total), "%")
# print("Completion Distance", completion_distance, "m")
# print("Curve Length", curve_length, "m")
# # print("Average Speed", np.mean(speeds), np.std(speeds), "m/s")
# print("Average Speed", completion_distance/((end_time_playing - start_time_playing).total_seconds()))
# print("Mean Deviation", np.mean(deviations), np.std(deviations), "m")

num_valid_users = 0
num_adirectional = 0
completion_times_normal = []
completion_times_blind = []
completion_times_adirectional = []
pctinside_normal = []
pctinside_blind = []
pctinside_adirectional = []
completion_distance_normal = []
completion_distance_blind = []
completion_distance_adirectional = []
avg_speed_normal = []
avg_speed_blind = []
avg_speed_adirectional = []
mean_deviation_normal = []
mean_deviation_blind = []
mean_deviation_adirectional = []
std_deviation_normal = []
std_deviation_blind = []
std_deviation_adirectional = []
for file, userdata in all_data.items():
    for curr_data in userdata:
        if curr_data[9] == False:
            num_adirectional += 1
    if len(userdata) < 2:  # they only did the normal test
        continue
    if len(userdata) > 2:
        print("woah!", len(userdata), "tests!")

    num_valid_users += 1
    for test_num, curr_data in enumerate(userdata):
        if curr_data[9] == False:
            completion_times_adirectional.append(curr_data[2])
            pctinside_adirectional.append(curr_data[3])
            completion_distance_adirectional.append(curr_data[4])
            avg_speed_adirectional.append(curr_data[6])
            mean_deviation_adirectional.append(curr_data[7])
            std_deviation_adirectional.append(curr_data[8])
        elif test_num == 0:
            completion_times_normal.append(curr_data[2])
            pctinside_normal.append(curr_data[3])
            completion_distance_normal.append(curr_data[4])
            avg_speed_normal.append(curr_data[6])
            mean_deviation_normal.append(curr_data[7])
            std_deviation_normal.append(curr_data[8])
        elif test_num == 1:
            completion_times_blind.append(userdata[1][2])
            pctinside_blind.append(userdata[1][3])
            completion_distance_blind.append(userdata[1][4])
            avg_speed_blind.append(userdata[1][6])
            mean_deviation_blind.append(userdata[1][7])
            std_deviation_blind.append(userdata[1][8])

print("Num valid users", num_valid_users)
print("Num adirectional users", num_adirectional)

plt.rcParams["figure.figsize"] = [10, 5]
fig, axs = plt.subplots(1, 2)

normal_means = np.array([np.mean(completion_distance_normal), 100*np.mean(avg_speed_normal), 100*np.mean(mean_deviation_normal)])
normal_std = np.array([np.std(completion_distance_normal), 100*np.std(avg_speed_normal), 100*np.std(mean_deviation_normal)])
blind_means = np.array([np.mean(completion_distance_blind), 100*np.mean(avg_speed_blind), 100*np.mean(mean_deviation_blind)])
blind_std = np.array([np.std(completion_distance_blind), 100*np.std(avg_speed_blind), 100*np.std(mean_deviation_blind)])
adirectional_means = np.array([np.mean(completion_distance_adirectional), 100*np.mean(avg_speed_adirectional), 100*np.mean(mean_deviation_adirectional)])
adirectional_std = np.array([np.std(completion_distance_adirectional), 100*np.std(avg_speed_adirectional), 100*np.std(mean_deviation_adirectional)])
print("Normal Means", normal_means, normal_std)
print("Blind Means", blind_means, blind_std)
print("Adirectional Means", adirectional_means, adirectional_std)
metrics = ["Completion Distance\n(m)", "Average Speed\n(cm/s)", "Mean Deviation\nfrom Wire (cm)"]

x_axis = np.arange(len(normal_means))
axs[0].bar(x_axis - 0.3, normal_means, width=0.3, label='Eyes Open, Directional Feedback', yerr=normal_std, capsize=5)
axs[0].bar(x_axis, blind_means, width=0.3, label='Eyes Closed, Directional Feedback', yerr=blind_std, capsize=5)
axs[0].bar(x_axis + 0.3, adirectional_means, width=0.3, label='Eyes Open, Non-Directional Feedback', yerr=blind_std, capsize=5)
axs[0].set_xticks(x_axis)
axs[0].set_xticklabels(metrics)
plt.legend()
plt.tight_layout()

normal_means = np.array([np.mean(completion_times_normal), np.mean(pctinside_normal)])
normal_std = np.array([np.std(completion_times_normal), np.std(pctinside_normal)])
blind_means = np.array([np.mean(completion_times_blind), np.mean(pctinside_blind)])
blind_std = np.array([np.std(completion_times_blind), np.std(pctinside_blind)])
adirectional_means = np.array([np.mean(completion_times_adirectional), np.mean(pctinside_adirectional)])
adirectional_std = np.array([np.std(completion_times_adirectional), np.std(pctinside_adirectional)])
metrics = ["Completion Time\n(s)", "% of Time Wire\nInside Ring (%)"]

x_axis = np.arange(len(normal_means))
# axs[1].bar(x_axis - 0.2, normal_means, width=0.4, label='Normal Test', yerr=normal_std, capsize=3)
# axs[1].bar(x_axis + 0.2, blind_means, width=0.4, label='Eyes Closed', yerr=blind_std, capsize=3)
axs[1].bar(x_axis - 0.3, normal_means, width=0.3, label='Eyes Open, Directional Feedback', yerr=normal_std, capsize=5)
axs[1].bar(x_axis, blind_means, width=0.3, label='Eyes Closed, Directional Feedback', yerr=blind_std, capsize=5)
axs[1].bar(x_axis + 0.3, adirectional_means, width=0.3, label='Eyes Open, Non-Directional Feedback', yerr=blind_std, capsize=5)
axs[1].set_xticks(x_axis)
axs[1].set_xticklabels(metrics)
plt.legend()
plt.suptitle("Buzzwire Performance (N = 12)")
plt.tight_layout()
plt.show()
