import numpy as np
from utils_plot import GamePhase, initialize_curve
from scipy.spatial.distance import cdist
from datetime import datetime

file = "data/20220528_09_46_20_demo_directional_feedback_user0.npy"
data = np.load(file, allow_pickle=True)

data, num_inside, num_outside, num_inside_while_playing, num_outside_while_playing, playingCompletionTime = data
# data, num_inside, num_outside, num_inside_while_playing, num_outside_while_playing, playingCompletionTime, x_min, x_max, curve_y, curve_z = data
N = np.shape(data)[0]
print("Num Points", N)

x_min, x_max = 0.25, 1.2
curve_y = lambda x: 0.0
# curve_y = lambda x: 0.025*(np.sin(5*x) + np.cos(6*x))
curve_z = lambda x: 0.075*(np.sin(7*x) + np.cos(3*x))
curve, curve_midpoints = initialize_curve(x_min, x_max, curve_y, curve_z, N=100)

# status, datetime.now(), num_loops, tags[0].pose_t, tags[0].pose_R, inside
times = np.reshape([time for status, time, num_loop, pose_t, pose_R, inside in data], (N,))
statuses = np.reshape([status for status, time, num_loop, pose_t, pose_R, inside in data], (N,))
positions = np.reshape([pose_t for status, time, num_loop, pose_t, pose_R, inside in data], (N, 3))
insides = np.reshape([inside for status, time, num_loop, pose_t, pose_R, inside in data], (N,))

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
        break  # stop counting after first play session

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

print("Navigation Time", (end_time_navigate_to_origin - start_time_navigate_to_origin).total_seconds(), "s")
print("Completion Time", (end_time_playing - start_time_playing).total_seconds(), "s")
print("Percent Inside",
      100*num_inside_while_playing_total/(num_inside_while_playing_total + num_outside_while_playing_total), "%")
print("Completion Distance", completion_distance, "m")
print("Curve Length", curve_length, "m")
print("Average Speed", np.mean(speeds), np.std(speeds), "m/s")
print("Mean Deviation", np.mean(deviations), np.std(deviations), "m")
