import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cv2
import pupil_apriltags
from datetime import datetime
import mpl_toolkits.mplot3d.art3d
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

# matplotlib.use('GTK3Agg')
matplotlib.use('Qt5Agg')

INCH_TO_METERS = 0.0254

thickness = 0.02*2  # thickness of wand
ring_r_inner = 0.075/2  # inner radius of the ring (m)
ring_r_outer = 0.045  # outer radius of the ring (m)
handle_length = 0.130  # handle length
handle_width = 0.03  # handle width


def detect_ar_tag(img, apriltag_detector, estimate_tag_pose=False, camera_params=None, tag_size=None):
    start = datetime.now()
    tags = apriltag_detector.detect(img, estimate_tag_pose=estimate_tag_pose, camera_params=camera_params,
                                    tag_size=tag_size)
    # print((datetime.now() - start).total_seconds())
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


def draw_wand(fig, background, ax: Axes3D, ring: Line3DCollection, handle: mpl_toolkits.mplot3d.art3d.Line3D, spline_midpoints: np.ndarray,
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
    # ring.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])
    ring_segments = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    ring.set_segments(ring_segments)

    pts_midpoints = (pts[:-1] + pts[1:])/2
    # distances = [np.linalg.norm(spline_midpoint - pts_midpoint) for spline_midpoint, pts_midpoint in
    #              zip(spline_midpoints, pts_midpoints)]
    distances = [np.min([np.linalg.norm(spline_midpoint - pts_midpoint) for spline_midpoint in spline_midpoints]) for pts_midpoint in pts_midpoints]
    pos_swapped = np.matmul(swap, pos).flatten()
    distances_to_center = np.min([np.linalg.norm(spline_midpoint - pos_swapped) for spline_midpoint in spline_midpoints])
    inside = distances_to_center < ring_r_inner
    colors = []
    for d in distances:
        # colors.append((np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
        if d > ring_r_inner*2/3 and inside:
            colors.append((0, 1, 0))
        elif d > ring_r_inner*1/3 and inside:
            colors.append((1, 1, 0))
        else:
            colors.append((1, 0, 0))
        # colors.append((int(d*20), int(d*20), int(d*20)))
    print(distances, distances_to_center, inside)
    print(colors)
    print([np.shape(spline_midpoint) for spline_midpoint in spline_midpoints])
    print(np.shape(pos))
    ring.set_colors(colors)
    # print(np.mean(pts, axis=0))

    # update handle
    pts = [(ring_r_inner, 0, 0), (ring_r_outer + handle_length, 0, 0)]
    pts = np.reshape(pts, (2, 3))
    pts = np.transpose(np.matmul(R, np.transpose(pts))) + np.ndarray.flatten(pos)
    if change_perspective:
        pts = np.transpose(np.matmul(swap, np.transpose(pts)))
    handle.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])

    # this method is based on https://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
    # https://stackoverflow.com/questions/40126176/fast-live-plotting-in-matplotlib-pyplot
    fig.canvas.restore_region(background)
    ax.draw_artist(ring)
    ax.draw_artist(handle)
    fig.canvas.update()
    # fig.canvas.blit(ax.bbox)
    fig.canvas.flush_events()

    return ring, handle


if __name__ == "__main__":
    # define a video capture object
    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # width, height = 1920, 1080  # 640x480 = default width of camera, up to 1920x1080
    # width, height = 640*1, 360*1  # 640x480 = default width of camera, up to 1920x1080
    # width, height = 640, 480
    # width, height = 424, 240
    width, height = 352, 288
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
    # camera_params = [958.9126, 956.1364, 957.4814, 557.8223]  # from matlab calibration, 1920x1080
    # camera_params = [443.8266, 443.4999, 320.3827, 247.3580]  # from matlab calibration, 640x480
    # camera_params = [233.4269, 232.5352, 214.9525, 123.1879]  # from matlab calibration, 424x240
    camera_params = [263.5568, 269.5951, 179.0278, 147.3135]  # from matlab calibration, 352x288
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
    curve_midpoints = (curve[:-1] + curve[1:])/2
    # print(curve)

    # define helper variables
    print_every = 50
    start_time = datetime.now()
    num_loops = 0
    lastTime = datetime.now()
    fps_average_interval = 100  # should be > print_every
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    # cv2.setWindowProperty('Camera Feed', cv2.WND_PROP_TOPMOST, 1)

    # Setup plot
    plt.rcParams["figure.figsize"] = [15.00, 10]
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.grid(False)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ax.set_xlim(0, 1.5)
    ax.set_ylim(-0.2, 0.2)
    ax.set_zlim(-0.2, 0.2)
    # ring, = plt.plot([], [], lw=3)  # , lw=(ring_r_outer-ring_r_inner)/2)

    N = 15
    ring_r_avg = (ring_r_outer + ring_r_inner)/2
    ring_pts = [(ring_r_avg*np.cos(t), ring_r_avg*np.sin(t), 0) for t in np.linspace(0, 2*np.pi, N)]
    ring_segments = [(ring_pts[i], ring_pts[i + 1]) for i in range(len(ring_pts) - 1)]
    colors = [(0, 255, 0) for _ in range(len(ring_segments))]
    ring = Line3DCollection(ring_segments, colors=colors, linewidths=3)
    ax.add_collection(ring)
    handle, = plt.plot([], [], lw=3)

    # handle, = plt.plot([], [], lw=3)
    spline, = plt.plot(curve[:, 0], curve[:, 1], curve[:, 2], lw=5)
    plt.tight_layout()

    fig.canvas.draw()
    background = fig.canvas.copy_from_bbox(ax.bbox)
    plt.show(block=False)

    times = []
    count = 0

    # manager = plt.get_current_fig_manager()
    # manager.full_screen_toggle()

    while True:
        ret, frame = vid.read()  # Capture the video frame by frame
        greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detect_ar_tag(greyscale, apriltag_detector, estimate_tag_pose, camera_params, tag_size)

        for tag in tags:
            corners = np.array(tag.corners).astype("int")
            for corner in corners:
                frame = cv2.circle(frame, corner, 10, BLUE)
            frame = cv2.polylines(frame, [corners], isClosed=True, color=BLUE, thickness=4)

        # cv2.imshow('Camera Feed', cv2.resize(frame, (640, 360)))
        cv2.imshow('Camera Feed', frame)

        if len(tags) > 0:
            ring, handle = draw_wand(fig, background, ax, ring, handle, curve_midpoints, tags[0].pose_t, tags[0].pose_R, N=N, change_perspective=True)
            # print(tags[0].pose_t)
        # plt.draw()
        plt.pause(0.001)

        # the 'q' button is set as the quitting button
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        num_loops += 1

        currTime = datetime.now()
        times.append((currTime - lastTime).total_seconds())
        lastTime = currTime
        if times[-1] > 0.33:
            count += 1

        if num_loops == print_every:
            print("Avg. FPS:", np.mean(times), np.std(times), np.min(times), np.sort(times)[-10:], count)
        # #     print("Avg. FPS:", print_every/(datetime.now() - lastTime).total_seconds())
        # #     lastTime = datetime.now()
            num_loops = 0

    vid.release()
    cv2.destroyAllWindows()
