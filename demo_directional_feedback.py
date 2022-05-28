import numpy as np
import cv2
from datetime import datetime
from utils_plot import *
from utils_apriltag import *
from utils_arduino import *

user_number = 0
com_port = "COM10"  # COM port of Arduino
radius_multiplier = 1.5  # >1 = larger virtual loop --> easier for user to thread through wire
tag_size = 2.5*INCH_TO_METERS  # 2.875*INCH_TO_METERS # 2.5*INCH_TO_METERS
save_data = True

if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_demo_directional_feedback_user{}".format(user_number)
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    width, height = 352, 288
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # camera_intrinsics = [443.8266, 443.4999, 320.3827, 247.3580]  # from matlab calibration, 640x480
    camera_intrinsics = [263.5568, 269.5951, 179.0278, 147.3135]  # from matlab calibration, 352x288
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
    # curve_z = lambda x: 0.0
    curve, curve_midpoints = initialize_curve(x_min, x_max, curve_y, curve_z, N=100)
    curve_line, curve_midpoints_line = initialize_curve(0.25, 1, lambda x: 0.0, lambda x: 0.0, N=100)

    # Setup global objects
    fig, axs = setup_plot()
    apriltag_detector = create_apriltag_detector(nthreads=2)
    ring_pts = initialize_ring(ring_radius, N=15)
    handle_pts = initialize_handle(ring_radius, handle_length)
    rings, handles, splines, status_text, update_text, backgrounds = initialize_plot_objects(fig, axs, curve)
    update_curve(splines, curve_line)

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
                inside = update_ring(rings, tags[0].pose_t, tags[0].pose_R, ring_pts, curve_midpoints, camera2World,
                                     ring_radius)
            else:
                inside = update_ring(rings, tags[0].pose_t, tags[0].pose_R, ring_pts, curve_midpoints_line,
                                     camera2World, ring_radius)
            update_handle(handles, tags[0].pose_t, tags[0].pose_R, handle_pts, camera2World, inside)

            if inside:
                update_text.set_text("Good Job!")
                update_text.set_color("black")
                num_inside += 1
                if status == GamePhase.Playing:
                    num_inside_while_playing += 1
            else:
                update_text.set_text("GET BACK IN THE GAME!")
                update_text.set_color("red")
                num_outside += 1
                if status == GamePhase.Playing:
                    num_outside_while_playing += 1

            if status == GamePhase.Exploring and not finished:
                status_text.set_text("Status: Exploring, Save = {}".format(save_data))
            elif status == GamePhase.Exploring and finished:
                status_text.set_text(
                    "Status: Finished!, Time = {} s, % Outside Wire = {}%".format(int(playingCompletionTime),
                                                                                  int(100*num_outside_while_playing/(
                                                                                              num_inside_while_playing + num_outside_while_playing))))
            elif status == GamePhase.NavigatingToOrigin:
                status_text.set_text("Status: Navigating to Origin, Save = {}".format(save_data))
            elif status == GamePhase.Playing:
                status_text.set_text("Status: Playing Buzzwire!, Save = {}".format(save_data))

            data.append((status, datetime.now(), num_loops, tags[0].pose_t, tags[0].pose_R, inside))

            # Check whether completed
            if status == GamePhase.Playing and tags[0].pose_t[2] < x_min:
                finished = True
                playingCompletionTime = (datetime.now() - playingStartTime).total_seconds()

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
        elif key_input == ord('1') or (finished and status == GamePhase.Playing):
            status = GamePhase.Exploring
            update_curve(splines, curve_line)
            curvesUpdated = True
        elif key_input == ord('2'):
            status = GamePhase.NavigatingToOrigin
            update_curve(splines, curve)
            curvesUpdated = True
        elif key_input == ord('3'):
            status = GamePhase.Playing
            playingStartTime = datetime.now()
            num_inside_while_playing = 0
            num_outside_while_playing = 0
            finished = False
        elif key_input == ord('4'):
            status = GamePhase.Exploring
        elif key_input == ord('8'):
            save_data = True
        elif key_input == ord('9'):
            save_data = False
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

    if save_data:
        np.save("data/" + timestamp + ".npy", [data, num_inside, num_outside, num_inside_while_playing, num_outside_while_playing, playingCompletionTime, curve], allow_pickle=True)
