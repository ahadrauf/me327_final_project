import numpy as np
import cv2
from datetime import datetime
from utils_plot import *
from utils_apriltag import *
from utils_arduino import *
import winsound
import time

user_number = 3
com_port = "COM10"  # COM port of Arduino
radius_multiplier = 1.5  # >1 = larger virtual loop --> easier for user to thread through wire
tag_size = 2.5*INCH_TO_METERS  # 2.875*INCH_TO_METERS # 2.5*INCH_TO_METERS
save_data = True

num_trials = 40
assert (num_trials%8 == 0)

top_left_pin = 6  # 5
top_right_pin = 11  # 11
bottom_left_pin = 10  # 11  # 9
bottom_right_pin = 5  # 6
# top_left_pin = 10  # 11  # 5
# top_right_pin = 5  # 11
# bottom_left_pin = 6  # 9
# bottom_right_pin = 9  # 6
zero_pin = 3
max_power = int(0.8*255)
old_sector = None
prev_radial_partition = 0

RED_normal = (1, 0, 0)
RED_colorblind = (202/255, 0, 32/255)
YELLOW_normal = (1, 1, 0)
YELLOW_colorblind = (244/255, 165/255, 130/255)
GREEN_normal = (0, 1, 0)
GREEN_colorblind = (5/255, 133/255, 176/255)
RED = RED_normal
YELLOW = YELLOW_normal
GREEN = GREEN_normal


def write_pwm_by_quadrant(arduino: serial.Serial, sector: np.ndarray, inside, radius) -> None:
    """
    Writes PWM to Arduino based on the quadrant the vector_to_center is
    :param arduino: Arduino serial object
    :param vector_to_center: Vector from the closest point on the spline to the ring's center (ring_pos - spline)
    :return: None
    """
    global old_sector, prev_radial_partition
    angle = np.arctan2(vector_to_center[2], vector_to_center[1])  # radians
    sector = int((angle + np.pi/8)//(np.pi/4))
    distance_to_center = np.linalg.norm(vector_to_center)

    if distance_to_center < radius/3:
        ring_partition = 0
    elif distance_to_center < radius:
        ring_partition = 1
    else:
        ring_partition = 2

    if sector == old_sector and prev_radial_partition == ring_partition:
        return
    else:
        old_sector = sector
        prev_radial_partition = ring_partition

    if distance_to_center < radius/3:
        write_four_numbers(arduino, DriveMode.Off.value, zero_pin, zero_pin, 0)
        return
    elif distance_to_center < radius:
        pwr = int(max_power*1/3)
    else:
        pwr = max_power

    # pwr = max_power
    print("Wrote to Arduino", sector, pwr)
    # scalar = 0.67
    if sector == EightfoldSector.Right.value:
        write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, bottom_left_pin, pwr)
    elif sector == EightfoldSector.TopRight.value:
        write_four_numbers(arduino, DriveMode.Directional.value, bottom_left_pin, 0, pwr)
    elif sector == EightfoldSector.Top.value:
        write_four_numbers(arduino, DriveMode.Directional.value, bottom_left_pin, bottom_right_pin, pwr)
    elif sector == EightfoldSector.TopLeft.value:
        write_four_numbers(arduino, DriveMode.Directional.value, bottom_right_pin, 0, pwr)
    elif sector == EightfoldSector.Left1.value or sector == EightfoldSector.Left2.value:
        write_four_numbers(arduino, DriveMode.Directional.value, top_right_pin, bottom_right_pin, pwr)
    elif sector == EightfoldSector.BottomLeft.value:
        write_four_numbers(arduino, DriveMode.Directional.value, top_right_pin, 0, pwr)
    elif sector == EightfoldSector.Bottom.value:
        write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, top_right_pin, pwr)
    elif sector == EightfoldSector.BottomRight.value:
        write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, 0, pwr)


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_userstudy_blind_user{}".format(user_number)
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    width, height = 640, 480  # 352, 288
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    camera_intrinsics = [443.8266, 443.4999, 320.3827, 247.3580]  # from matlab calibration, 640x480
    # camera_intrinsics = [263.5568, 269.5951, 179.0278, 147.3135]  # from matlab calibration, 352x288
    camera2World = np.array([[0, 0, 1],
                             [-1, 0, 0],
                             [0, -1, 0]])  # change camera perspective to best viewing perspective

    ring_r_inner = 0.075/2  # inner radius of the ring (m)
    ring_r_outer = 0.045  # outer radius of the ring (m)
    ring_radius = (ring_r_inner + ring_r_outer)/2*radius_multiplier
    handle_length = 0.130  # handle length
    x_min = 0.25
    x_max = 1.2
    curve_radius = 0.2
    min_threshold = curve_radius - ring_radius
    curve_line, curve_midpoints_line = initialize_curve(x_min, x_max, lambda x: 0.0, lambda x: 0.0, N=100)
    curve_ring = {sector: initialize_curve(x_min, x_max, lambda x: curve_radius*np.cos(EightfoldSectorAngles[sector]),
                                           lambda x: curve_radius*np.sin(EightfoldSectorAngles[sector]), N=100)
                  for sector in EightfoldSector}
    active_curve = curve_line
    active_curve_midpoints = curve_midpoints_line

    # Setup global objects
    fig, axs = setup_plot()
    apriltag_detector = create_apriltag_detector(nthreads=3)
    ring_pts = initialize_ring(ring_radius, N=15)
    handle_pts = initialize_handle(ring_radius, handle_length)
    rings, handles, splines, status_text, update_text, backgrounds = initialize_plot_objects(fig, axs, curve_line,
                                                                                             show_plot=False)
    arduino = generate_arduino(com_port) if com_port is not None else None

    # Debug and data variables
    # define helper variables
    print_every = 50
    start_time = datetime.now()
    num_loops = 0
    lastTime = datetime.now()
    times = []
    count = 0
    data = []
    num_inside = 0
    num_outside = 0
    num_inside_while_playing = 0
    num_outside_while_playing = 0

    status = GamePhase.Exploring
    finished = False
    playingCompletionTime = 0
    playingStartTime = 0
    curvesUpdated = False

    test_directions = []
    for test_direction in EightfoldSector:
        if test_direction == EightfoldSector.Left2:
            continue
        for _ in range(num_trials//8):
            test_directions.append(test_direction)
    np.random.shuffle(test_directions)
    test_direction_values = [test_direction.value for test_direction in test_directions]
    actual_direction_values = []

    test_num = -1
    test_start_time = datetime.now()
    test_end_time = datetime.now()
    test_times = []
    return_times = []
    final_vectors_to_center = []
    returning_to_zero = True
    start_position = np.array([0, 0, 0])
    end_position = np.array([0, 0, 0])

    while test_num < num_trials:
        ret, frame = vid.read()  # Capture the video frame by frame
        greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detect_apriltag(greyscale, apriltag_detector, estimate_tag_pose=True,
                               camera_intrinsics=camera_intrinsics,
                               tag_size=tag_size)

        for tag in tags:
            corners = np.array(tag.corners).astype("int")
            for corner in corners:
                frame = cv2.circle(frame, corner, 10, (255, 0, 0))
            frame = cv2.polylines(frame, [corners], isClosed=True, color=(255, 0, 0), thickness=4)

        if len(tags) > 0:
            inside, vector_to_center = update_ring(rings, tags[0].pose_t, tags[0].pose_R, ring_pts,
                                                   active_curve_midpoints, camera2World, ring_radius, RED, YELLOW, GREEN)
            update_handle(handles, tags[0].pose_t, tags[0].pose_R, handle_pts, camera2World, inside, RED, GREEN)

            if arduino is not None:
                write_pwm_by_quadrant(arduino, vector_to_center, inside, ring_radius)

            # if inside:
            #     update_text.set_text("Good Job!")
            #     update_text.set_color("black")
            #     num_inside += 1
            #     if status == GamePhase.Playing:
            #         num_inside_while_playing += 1
            # else:
            #     update_text.set_text("GET BACK IN THE GAME!")
            #     update_text.set_color("red")
            #     num_outside += 1
            #     if status == GamePhase.Playing:
            #         num_outside_while_playing += 1
            if returning_to_zero:
                update_text.set_text("Return to origin")
            else:
                update_text.set_text("Move to new line")

            if status == GamePhase.Exploring and not finished:
                status_text.set_text("Status: Exploring, Save = {}".format(save_data))
            elif status == GamePhase.Exploring and finished:
                status_text.set_text(
                    "Status: Finished!, Time = {} s, % Threading Wire = {}%".format(int(playingCompletionTime),
                                                                                    int(100*num_inside_while_playing/(
                                                                                            num_inside_while_playing + num_outside_while_playing))))
            elif status == GamePhase.NavigatingToOrigin:
                status_text.set_text("Status: Navigating to Origin, Save = {}".format(save_data))
            elif status == GamePhase.Playing:
                status_text.set_text("Status: Playing User Study!, Save = {}".format(save_data))

            data.append((status, test_num, datetime.now(), num_loops, tags[0].pose_t, tags[0].pose_R, inside))

            # Check whether completed
            if status == GamePhase.Playing:
                end_position = tags[0].pose_t
                if inside and returning_to_zero:
                    if test_num != -1:
                        test_end_time = datetime.now()
                        return_times.append((test_end_time - test_start_time).total_seconds())
                        # cv2.waitKey(3000)  # 3s delay
                    winsound.Beep(440, 250)
                    time.sleep(0.25)
                    winsound.Beep(440, 250)
                    time.sleep(0.25)
                    winsound.Beep(900, 500)
                    time.sleep(0.5)
                    test_num += 1
                    if test_num < num_trials:
                        active_curve, active_curve_midpoints = curve_ring[test_directions[test_num]]
                        update_curve(splines, active_curve)
                        test_start_time = datetime.now()
                    returning_to_zero = False
                    start_position = end_position
                elif not returning_to_zero and np.linalg.norm(end_position - start_position) >= min_threshold:
                    print(np.linalg.norm(end_position - start_position), min_threshold)
                    test_end_time = datetime.now()
                    test_times.append((test_end_time - test_start_time).total_seconds())
                    # cv2.waitKey(3000)  # 3s delay
                    winsound.Beep(440, 250)
                    time.sleep(0.25)
                    winsound.Beep(600, 500)
                    time.sleep(0.5)
                    final_vectors_to_center.append(vector_to_center)
                    vector_to_center = np.matmul(camera2World, tags[0].pose_t)
                    angle = np.arctan2(vector_to_center[2], vector_to_center[1])  # radians
                    sector = int((angle + np.pi/8)//(np.pi/4))
                    actual_direction_values.append(sector)
                    print("Expected direction:", test_direction_values[test_num], " Actual direction:", sector,
                          vector_to_center, "time:", test_times[-1], "s")
                    active_curve, active_curve_midpoints = curve_line, curve_midpoints_line
                    update_curve(splines, active_curve)
                    test_start_time = datetime.now()
                    returning_to_zero = True

        for background, ax, ring, handle, spline in zip(backgrounds, axs, rings, handles, splines):
            fig.canvas.restore_region(background)
            ax.draw_artist(ring)
            ax.draw_artist(handle)
            ax.draw_artist(spline)
            fig.canvas.blit(ax.bbox)
        curvesUpdated = False
        # fig.canvas.update()
        fig.canvas.flush_events()
        plt.draw()

        cv2.imshow('Camera Feed', frame)
        key_input = cv2.waitKey(1) & 0xFF
        if key_input == ord('q'):
            plt.close(fig)
            break
        elif key_input == ord('1'):
            status = GamePhase.Playing
            playingStartTime = datetime.now()
        elif finished:
            status = GamePhase.Exploring
            playingCompletionTime = (datetime.now() - playingStartTime).total_seconds()
        elif key_input == ord('7'):
            write_four_numbers(arduino, DriveMode.Cycle.value, 0, 0, max_power)
        elif key_input == ord('8'):
            save_data = True
        elif key_input == ord('9'):
            save_data = False
        # plt.pause(0.001)

        # the 'q' button is set as the quitting button
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        num_loops += 1
        print(test_num, "/", num_trials)

        # currTime = datetime.now()
        # times.append((currTime - lastTime).total_seconds())
        # lastTime = currTime
        # if times[-1] > 0.33:
        #     count += 1

        # if num_loops == print_every:
        #     fps = 1./np.array(times)
        #     print("Avg. FPS:", np.mean(fps), np.std(fps), np.min(fps), np.max(fps), np.sort(times)[:10], count)
        #     num_loops = 0

    vid.release()
    cv2.destroyAllWindows()

    if save_data:
        clarifier = "_feedback={}".format(arduino is not None)
        np.save("data/" + timestamp + ".npy",
                [data, test_direction_values, actual_direction_values, test_times, return_times,
                 final_vectors_to_center,
                 playingCompletionTime, curve_ring], allow_pickle=True)
