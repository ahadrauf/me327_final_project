import numpy as np
import matplotlib.pyplot as plt
import cv2
import pupil_apriltags
from datetime import datetime

INCH_TO_METERS = 0.0254


def detect_ar_tag(img, apriltag_detector, estimate_tag_pose=False, camera_params=None, tag_size=None):
    tags = apriltag_detector.detect(img, estimate_tag_pose=estimate_tag_pose, camera_params=camera_params,
                                    tag_size=tag_size)
    return tags


if __name__ == "__main__":
    # define a video capture object
    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # width, height = 640*1, 480*1  # 640x480 = default width of camera, up to 1920x1080
    # width, height = 640*1, 360*1  # 640x480 = default width of camera, up to 1920x1080
    # width, height = 352, 288
    width, height = 1920, 1080
    # if width != 640:
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # AprilTag settings
    apriltag_detector = pupil_apriltags.Detector(families="tag36h11",
                                                 nthreads=1,
                                                 quad_decimate=1.0,
                                                 quad_sigma=0.0,
                                                 refine_edges=1,
                                                 decode_sharpening=0.5,
                                                 debug=0)
    estimate_tag_pose = True
    # camera_params = [np.deg2rad(46.4*2), np.deg2rad(29.1*2), 0., 0.]  # [fx, fy, cx, cy]
    # camera_params = [np.deg2rad(46.4*2), np.deg2rad(29.1*2), 0., 0.]  # [fx, fy, cx, cy]
    camera_params = [958.9126, 956.1364, 957.4814, 557.8223]  # from matlab calibration, 1920x1080
    # camera_params = [443.8266, 443.4999, 320.3827, 247.3580]  # from matlab calibration, 640x480
    # camera_params = [233.4269, 232.5352, 214.9525, 123.1879]  # from matlab calibration, 424x240
    # camera_params = [263.5568, 269.5951, 179.0278, 147.3135]  # from matlab calibration, 352x288
    tag_size = 0.069  # 2.5*INCH_TO_METERS

    # define AR tag tracking variables
    # camera matrix for E-Meet (https://smile.amazon.com/gp/product/B08DXSG5QR/)
    # K = compute_intrinsic_camera_matrix(1920, 1080, fov_x=46.4*2, fov_y=29.1*2)
    # K = compute_intrinsic_camera_matrix(width, height, fov_x=46.4*2, fov_y=29.1*2)
    # print("K", K)
    # ref_img = cv2.imread("./images/ar_tag_1_v2.jpg", cv2.IMREAD_GRAYSCALE)

    # define helper variables
    print_every = 50
    start_time = datetime.now()
    num_loops = 0
    fps_average_interval = 100  # should be > print_every
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    times = []

    while True:
        ret, frame = vid.read()  # Capture the video frame by frame
        # print(np.shape(frame))
        greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        start_time = datetime.now()
        tags = detect_ar_tag(greyscale, apriltag_detector, estimate_tag_pose, camera_params, tag_size)
        end_time = datetime.now()
        times.append((end_time - start_time).total_seconds())
        # print(len(tags))

        for tag in tags:
            print(np.ndarray.flatten(tag.pose_t), np.mean(times), np.std(times))  # , np.ndarray.flatten(tag.pose_R), tag.pose_err)
            corners = np.array(tag.corners).astype("int")
            for corner in corners:
                frame = cv2.circle(frame, corner, 10, BLUE)
            frame = cv2.polylines(frame, [corners], isClosed=True, color=BLUE, thickness=4)

        # # grayscale = cv2.blur(grayscale, (3, 3))
        # if np.mean(greyscale) == 128:
        #     continue
        #
        # if num_loops%print_every == 0:
        #     print("FPS:", num_loops/(datetime.now() - start_time).total_seconds())
        #     print(np.shape(frame), np.shape(ref_img))
        # if num_loops > 100:
        #     start_time = datetime.now()
        #     num_loops = 0
        #
        # locs, scene, H = find_ar_tag(greyscale, ref_img, ratio_threshold=0.9)
        # if locs is None:
        #     print("No AR tag found")
        # else:
        #     # T, N = homography_to_axes(H, K)
        #
        #     # Display the resulting frame (1/2 size so it shows up better on a normal screen)
        #     locs = locs.astype("int")
        #     for loc in locs:
        #         print("loc", loc)
        #         frame = cv2.circle(frame, loc, 10, BLUE)
        #     frame = cv2.polylines(frame, [locs], isClosed=True, color=BLUE, thickness=4)
        #     frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
        #     cv2.imshow('Camera Feed', frame)

        cv2.imshow('Camera Feed', frame)

        # the 'q' button is set as the quitting button
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        num_loops += 1

    vid.release()
    cv2.destroyAllWindows()
