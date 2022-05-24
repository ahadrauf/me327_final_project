import numpy as np
import matplotlib.pyplot as plt
import cv2
import pupil_apriltags
from datetime import datetime
import mpl_toolkits.mplot3d.art3d
from mpl_toolkits.mplot3d import Axes3D

INCH_TO_METERS = 0.0254

thickness = 0.02*2  # thickness of wand
ring_r_inner = 0.075/2  # inner radius of the ring (m)
ring_r_outer = 0.045  # outer radius of the ring (m)
handle_length = 0.130  # handle length
handle_width = 0.03  # handle width


def detect_ar_tag(img, apriltag_detector, estimate_tag_pose=False, camera_params=None, tag_size=None):
    tags = apriltag_detector.detect(img, estimate_tag_pose=estimate_tag_pose, camera_params=camera_params,
                                    tag_size=tag_size)
    return tags


def hermite_interpolation(t, p0, p1, m0, m1):
    """
    Cubic hermite interpolation
    https://en.wikipedia.org/wiki/Cubic_Hermite_spline
    :param t: Time [0, 1]
    :param p0: Initial position (t = 0)
    :param p1: Final position (t = 1)
    :param m0: Initial tangent (t = 0)
    :param m1: Final tangent (t = 1)
    :return: Point at time t
    """
    t2 = t*t
    t3 = t*t*t
    h00 = 2*t3 - 3*t2 + 1
    h10 = t3 - 2*t2 + t
    h01 = -2*t3 + 3*t2
    h11 = t3 - t2
    return h00*p0 + h10*m0 + h01*p1 + h11*m1


def draw_wand(ax: Axes3D, ring: mpl_toolkits.mplot3d.art3d.Line3D, handle: mpl_toolkits.mplot3d.art3d.Line3D,
              pos: np.ndarray, R: np.ndarray, N: int = 10, change_perspective: bool = False):
    """
    Generates a 3D visualization for the arm

    Tutorial for drawing cylinders: https://stackoverflow.com/questions/32317247/how-to-draw-a-cylinder-using-matplotlib-along-length-of-point-x1-y1-and-x2-y2
    :param ax: Matplotlib axes on which to plot the wand
    :param ring: 3D line used to draw the ring
    :param handle: 3D line used to draw the handle
    :param pos: Position of the center of the ring
    :param R: Rotation matrix of the center of the ring
    :param N: Number of points used to describe the ring
    :return: None
    """
    # swap = np.array([[0, 0, 1],
    #                  [0, 1, 0],
    #                  [-1, 0, 0]])
    swap = np.array([[0, 0, 1],
                     [-1, 0, 0],
                     [0, -1, 0]])

    # update ring points
    ring_r_avg = (ring_r_outer + ring_r_inner)/2
    pts = [(ring_r_avg*np.cos(t), ring_r_avg*np.sin(t), 0) for t in np.linspace(0, 2*np.pi, N)]
    pts = np.reshape(pts, (N, 3))
    pts = np.transpose(np.matmul(R, np.transpose(pts))) + np.ndarray.flatten(pos)
    if change_perspective:
        pts = np.transpose(np.matmul(swap, np.transpose(pts)))
    ring.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])
    print(np.mean(pts, axis=0))

    # update handle
    pts = [(ring_r_inner, 0, 0), (ring_r_outer + handle_length, 0, 0)]
    pts = np.reshape(pts, (2, 3))
    pts = np.transpose(np.matmul(R, np.transpose(pts))) + np.ndarray.flatten(pos)
    if change_perspective:
        pts = np.transpose(np.matmul(swap, np.transpose(pts)))
    handle.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])

    return ring, handle


if __name__ == "__main__":
    # define a video capture object
    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # width, height = 1920, 1080  # 640x480 = default width of camera, up to 1920x1080
    # width, height = 640*1, 360*1  # 640x480 = default width of camera, up to 1920x1080
    width, height = 640, 480
    # if width != 640:
    # vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # AprilTag settings
    apriltag_detector = pupil_apriltags.Detector(families="tag36h11",
                                                 nthreads=1,
                                                 quad_decimate=1.0,
                                                 quad_sigma=0.0,
                                                 refine_edges=1,
                                                 decode_sharpening=0.25,
                                                 debug=0)
    estimate_tag_pose = True
    # camera_params = [np.deg2rad(46.4*2), np.deg2rad(29.1*2), 0., 0.]  # [fx, fy, cx, cy]
    # camera_params = [958.9126, 956.1364, 957.4814, 557.8223]  # from matlab calibration, 1920x1080
    camera_params = [443.8266, 443.4999, 320.3827, 247.3580]  # from matlab calibration, 640x480
    tag_size = 3*INCH_TO_METERS

    # define AR tag tracking variables
    # camera matrix for E-Meet (https://smile.amazon.com/gp/product/B08DXSG5QR/)
    # K = compute_intrinsic_camera_matrix(1920, 1080, fov_x=46.4*2, fov_y=29.1*2)
    # K = compute_intrinsic_camera_matrix(width, height, fov_x=46.4*2, fov_y=29.1*2)
    # print("K", K)
    # ref_img = cv2.imread("./images/ar_tag_1_v2.jpg", cv2.IMREAD_GRAYSCALE)

    control_pts = 0.1*np.array([[2, 0, 0], [4, 0, 1], [6, 0, 0], [8, 0, 1], [10, 0, 0.5], [12, 0, 0], [14, 0, 0]])
    tangents = 0.2*np.array([[1, 0, 0]]*len(control_pts))  # every tangent = in x-direction

    # Compute spline curve
    num_points_per_spline = 20
    curve = []
    for i in range(len(control_pts) - 1):
        for t in np.linspace(0, 1, num_points_per_spline, endpoint=False):
            curve += [hermite_interpolation(t, np.array(control_pts[i]), np.array(control_pts[i + 1]),
                                            np.array(tangents[i]), np.array(tangents[i + 1]))]
    curve += [np.array(control_pts[-1])]
    curve = np.array(curve)

    # define helper variables
    print_every = 50
    start_time = datetime.now()
    num_loops = 0
    lastTime = datetime.now()
    fps_average_interval = 100  # should be > print_every
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)

    # Setup plot
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.grid(False)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ax.set_xlim(0, 1.5)
    ax.set_ylim(-0.2, 0.2)
    ax.set_zlim(-0.2, 0.2)
    spline, = plt.plot(curve[:, 0], curve[:, 1], curve[:, 2])
    ring, = plt.plot([], [])  # , lw=(ring_r_outer-ring_r_inner)/2)
    handle, = plt.plot([], [])

    while True:
        ret, frame = vid.read()  # Capture the video frame by frame
        greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detect_ar_tag(greyscale, apriltag_detector, estimate_tag_pose, camera_params, tag_size)

        for tag in tags:
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

        # cv2.imshow('Camera Feed', cv2.resize(frame, (640, 360)))
        cv2.imshow('Camera Feed', frame)

        if len(tags) > 0:
            ring, handle = draw_wand(ax, ring, handle, tags[0].pose_t, tags[0].pose_R, change_perspective=True)
            # print(tags[0].pose_t)
        plt.draw()
        plt.pause(0.001)

        # the 'q' button is set as the quitting button
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        num_loops += 1

        if num_loops == print_every:
            print("Avg. FPS:", print_every/(datetime.now() - lastTime).total_seconds())
            lastTime = datetime.now()
            num_loops = 0

    vid.release()
    cv2.destroyAllWindows()
