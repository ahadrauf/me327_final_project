import numpy as np
import cv2
from datetime import datetime
from utils_plot import *
from utils_apriltag import *
from utils_arduino import *
import winsound
import time

user_number = 0
com_port = "COM10"  # None  # "COM10"  # COM port of Arduino
radius_multiplier = 1.5  # >1 = larger virtual loop --> easier for user to thread through wire
tag_size = 0.069  # 2.5*INCH_TO_METERS  # 2.875*INCH_TO_METERS # 2.5*INCH_TO_METERS
save_data = True
running_cyclic_test = False
directional_feedback = True
curve_num = 1

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


def write_pwm_by_quadrant(arduino: serial.Serial, vector_to_center: np.ndarray, inside: bool, radius: float) -> None:
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
        pwr = int(max_power*1/2)
    else:
        pwr = max_power

    if not directional_feedback:
        write_four_numbers(arduino, DriveMode.Adirectional.value, zero_pin, zero_pin, pwr)
        return

    # pwr = min(max_power, int(max_power/2*(distance_to_center/radius*2*(not inside)*(distance_to_center - radius)/radius)))
    # print("Wrote to Arduino", sector, pwr, vector_to_center, inside)
    # scalar = 0.67
    if not running_cyclic_test:
        if curve_num == 1:
            if sector == EightfoldSector.Right.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, bottom_left_pin, pwr)
            elif sector == EightfoldSector.TopRight.value:
                write_four_numbers(arduino, DriveMode.Directional.value, bottom_left_pin, zero_pin, pwr)
            elif sector == EightfoldSector.Top.value:
                write_four_numbers(arduino, DriveMode.Directional.value, bottom_left_pin, bottom_right_pin, pwr)
            elif sector == EightfoldSector.TopLeft.value:
                write_four_numbers(arduino, DriveMode.Directional.value, bottom_right_pin, zero_pin, pwr)
            elif sector == EightfoldSector.Left1.value or sector == EightfoldSector.Left2.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_right_pin, bottom_right_pin, pwr)
            elif sector == EightfoldSector.BottomLeft.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_right_pin, zero_pin, pwr)
            elif sector == EightfoldSector.Bottom.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, top_right_pin, pwr)
            elif sector == EightfoldSector.BottomRight.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, zero_pin, pwr)
        else:
            # When blindfolded, we found that vibrating away from the direction of desired motion was actually preferred
            # (it felt like we were hitting a virtual wall that we should move away from)
            if sector == EightfoldSector.Left1.value or sector == EightfoldSector.Left2.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, bottom_left_pin, pwr)
            elif sector == EightfoldSector.BottomLeft.value:
                write_four_numbers(arduino, DriveMode.Directional.value, bottom_left_pin, zero_pin, pwr)
            elif sector == EightfoldSector.Bottom.value:
                write_four_numbers(arduino, DriveMode.Directional.value, bottom_left_pin, bottom_right_pin, pwr)
            elif sector == EightfoldSector.BottomRight.value:
                write_four_numbers(arduino, DriveMode.Directional.value, bottom_right_pin, zero_pin, pwr)
            elif sector == EightfoldSector.Right.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_right_pin, bottom_right_pin, pwr)
            elif sector == EightfoldSector.TopRight.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_right_pin, zero_pin, pwr)
            elif sector == EightfoldSector.Top.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, top_right_pin, pwr)
            elif sector == EightfoldSector.TopLeft.value:
                write_four_numbers(arduino, DriveMode.Directional.value, top_left_pin, zero_pin, pwr)


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_demo_user{}".format(user_number)
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # width, height = 352, 288
    # width, height = 640, 480
    # vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    camera_intrinsics = [443.8266, 443.4999, 320.3827, 247.3580]  # from matlab calibration, 640x480
    # camera_intrinsics = [263.5568, 269.5951, 179.0278, 147.3135]  # from matlab calibration, 352x288
    # camera_intrinsics = [650.9442, 649.9007, 333.9212, 246.2005]  # from matlab calibration, 640x480 (laptop webcam)
    camera2World = np.array([[0, 0, 1],
                             [-1, 0, 0],
                             [0, -1, 0]])  # change camera perspective to best viewing perspective

    ring_r_inner = 0.075/2  # inner radius of the ring (m)
    ring_r_outer = 0.045  # outer radius of the ring (m)
    ring_radius = (ring_r_inner + ring_r_outer)/2*radius_multiplier
    handle_length = 0.130  # handle length

    # Setup curve
    # curve_z = lambda x: 0.05*(np.sin(4*x) + np.cos(7*x))
    x_min = 0.25
    x_max = 1.2
    curve_y = lambda x: 0.0
    # curve_y = lambda x: 0.025*(np.sin(5*x) + np.cos(6*x))
    curve_z = lambda x: 0.075*(np.sin(7*x) + np.cos(3*x))
    curve_z2 = lambda x: 0.05*(np.sin(5*x) + np.cos(6*x))
    # curve_z = lambda x: 0.0
    curve, curve_midpoints = initialize_curve(x_min, x_max, curve_y, curve_z, N=100)
    curve2, curve_midpoints2 = initialize_curve(x_min, x_max, curve_y, curve_z2, N=100)
    curves = [curve, curve2]
    curves_midpoints = [curve_midpoints, curve_midpoints2]
    curve_line, curve_midpoints_line = initialize_curve(x_min, x_max, lambda x: 0.0, lambda x: 0.0, N=100)

    # Setup global objects
    fig, axs = setup_plot()
    apriltag_detector = create_apriltag_detector(nthreads=3)
    ring_pts = initialize_ring(ring_radius, N=15)
    handle_pts = initialize_handle(ring_radius, handle_length)
    rings, handles, splines, status_text, update_text, backgrounds = initialize_plot_objects(fig, axs, curve)
    update_curve(splines, curve_line)
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
    switch_to_playing = False

    while True:
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
            if status != GamePhase.Exploring:
                inside, vector_to_center = update_ring(rings, tags[0].pose_t, tags[0].pose_R, ring_pts,
                                                       curves_midpoints[curve_num - 1], camera2World, ring_radius,
                                                       RED, YELLOW, GREEN)
            else:
                inside, vector_to_center = update_ring(rings, tags[0].pose_t, tags[0].pose_R, ring_pts,
                                                       curve_midpoints_line, camera2World, ring_radius,
                                                       RED, YELLOW, GREEN)
            update_handle(handles, tags[0].pose_t, tags[0].pose_R, handle_pts, camera2World, inside, RED, GREEN)

            if arduino is not None:
                write_pwm_by_quadrant(arduino, vector_to_center, inside, ring_radius)

            if inside:
                update_text.set_text("Good Job!")
                update_text.set_color("black")
                num_inside += 1
                if status == GamePhase.Playing:
                    num_inside_while_playing += 1
            else:
                update_text.set_text("GET BACK ON THE WIRE!")
                update_text.set_color("red")
                num_outside += 1
                if status == GamePhase.Playing:
                    num_outside_while_playing += 1

            directional_status = "Directional Feedback" if directional_feedback else "Adirectional Feedback"
            if status == GamePhase.Exploring and not finished:
                status_text.set_text(
                    "Status: Exploring\nSave = {}, {}, Curve {}".format(save_data, directional_status, curve_num))
            elif status == GamePhase.Exploring and finished:
                status_text.set_text(
                    "Status: Finished!, Time = {} s, % Threading Wire = {}%\nSave = {}, {}, Curve {}".format(
                        int(playingCompletionTime),
                        int(100*num_inside_while_playing/(num_inside_while_playing + num_outside_while_playing)),
                        save_data, directional_status, curve_num))
            elif status == GamePhase.NavigatingToOrigin:
                status_text.set_text(
                    "Status: Navigating to Origin\nSave = {}, {}, Curve {}".format(save_data, directional_status,
                                                                                   curve_num))
            elif status == GamePhase.Playing:
                status_text.set_text(
                    "Status: Playing Buzzwire!\nSave = {}, {}, Curve {}".format(save_data, directional_status,
                                                                                curve_num))

            data.append(
                (directional_feedback, curve_num, status, datetime.now(), num_loops, tags[0].pose_t, tags[0].pose_R,
                 inside))

            # Check whether completed
            if status == GamePhase.Playing and tags[0].pose_t[2] < x_min:
                finished = True
                playingCompletionTime = (datetime.now() - playingStartTime).total_seconds()
            if status == GamePhase.NavigatingToOrigin and \
                    np.linalg.norm(curves[curve_num - 1][-1] - np.ndarray.flatten(
                        np.matmul(camera2World, tags[0].pose_t))) < ring_radius:
                switch_to_playing = True

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

        cv2.imshow('Camera Feed', cv2.resize(frame, (320, 240)))
        # cv2.imshow('Camera Feed', frame)
        key_input = cv2.waitKey(1) & 0xFF
        if key_input == ord('q') or key_input == ord('5'):
            plt.close(fig)
            break
        elif key_input == ord('1') or (finished and status == GamePhase.Playing):
            status = GamePhase.Exploring
            update_curve(splines, curve_line)
            curvesUpdated = True
            winsound.Beep(440, 250)
            time.sleep(0.25)
        elif key_input == ord('2'):
            status = GamePhase.NavigatingToOrigin
            update_curve(splines, curves[curve_num - 1])
            curvesUpdated = True
        elif key_input == ord('3') or switch_to_playing:
            status = GamePhase.Playing
            playingStartTime = datetime.now()
            num_inside_while_playing = 0
            num_outside_while_playing = 0
            finished = False
            switch_to_playing = False
            winsound.Beep(440, 250)
            time.sleep(0.25)
            winsound.Beep(440, 250)
            time.sleep(0.25)
            winsound.Beep(900, 500)
            time.sleep(0.5)
        elif key_input == ord('4'):
            status = GamePhase.Exploring
            data = 0
            num_inside = 0
            num_outside = 0
            num_inside_while_playing = 0
            num_outside_while_playing = 0
            write_four_numbers(arduino, DriveMode.Off.value, zero_pin, zero_pin, 0)
        elif key_input == ord('6'):
            running_cyclic_test = False
        elif key_input == ord('7'):
            running_cyclic_test = True
            write_four_numbers(arduino, DriveMode.Cycle.value, zero_pin, zero_pin, max_power)
        elif key_input == ord('8'):
            save_data = True
        elif key_input == ord('9'):
            save_data = False

        elif key_input == ord('+'):
            directional_feedback = True
        elif key_input == ord('-'):
            directional_feedback = False
        elif key_input == ord('*'):
            curve_num = 2
            directional_feedback = True
        elif key_input == ord('/'):
            curve_num = 1
        elif key_input == ord('c'):
            RED = RED_colorblind
            YELLOW = YELLOW_colorblind
            GREEN = GREEN_colorblind
        elif key_input == ord('v'):
            RED = RED_normal
            YELLOW = YELLOW_normal
            GREEN = GREEN_normal
        # plt.pause(0.001)

        # the 'q' button is set as the quitting button
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        num_loops += 1

        currTime = datetime.now()
        times.append((currTime - lastTime).total_seconds())
        lastTime = currTime
        if times[-1] > 0.33:
            count += 1

        # if num_loops == print_every:
        #     fps = 1./np.array(times)
        #     print("Avg. FPS:", np.mean(fps), np.std(fps), np.min(fps), np.max(fps), np.sort(times)[:10], count)
        #     num_loops = 0

    vid.release()
    cv2.destroyAllWindows()
    write_four_numbers(arduino, DriveMode.Off.value, 0, 0, 0)

    if save_data:
        np.save("data/" + timestamp + ".npy",
                [data, num_inside, num_outside, num_inside_while_playing, num_outside_while_playing,
                 playingCompletionTime, curve], allow_pickle=True)
