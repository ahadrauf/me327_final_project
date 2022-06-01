import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cv2
import pupil_apriltags
from datetime import datetime
import mpl_toolkits.mplot3d.art3d
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection

# matplotlib.use('GTK3Agg')
matplotlib.use('Qt5Agg')

INCH_TO_METERS = 0.0254

easiness_factor = 1.75

thickness = 0.02*2  # thickness of wand
ring_r_inner = 0.075/2*easiness_factor  # inner radius of the ring (m)
ring_r_outer = 0.045*easiness_factor  # outer radius of the ring (m)
handle_length = 0.130  # handle length
handle_width = 0.03  # handle width

N_ring = 15
ring_r_avg = (ring_r_outer + ring_r_inner)/2
ring_pts = [(ring_r_avg*np.cos(t), ring_r_avg*np.sin(t), 0) for t in np.linspace(0, 2*np.pi, N_ring)]
ring_pts = np.reshape(ring_pts, (N_ring, 3))


def setup_plot():
    fig = plt.figure()
    ax_3d = fig.add_subplot(121, projection='3d')
    ax_xy = fig.add_subplot(322)
    ax_yz = fig.add_subplot(324)
    ax_xz = fig.add_subplot(326)

    for ax in [ax_3d, ax_xy, ax_yz, ax_xz]:
        ax.grid(False)

    # Setup 3D plot
    ax_3d.set_title("3D Projection")
    ax_3d.set_xlabel("X (m)")
    ax_3d.set_ylabel("Y (m)")
    ax_3d.set_zlabel("Z (m)")
    ax_3d.set_xlim(0, 2)
    ax_3d.set_ylim(-0.2, 0.2)
    ax_3d.set_zlim(-0.2, 0.2)

    # Setup x, y, z plots
    ax_xy.set_title("XY Projection")
    ax_yz.set_title("YZ Projection")
    ax_xz.set_title("XZ Projection")
    ax_xy.set_xlabel("X (m)")
    ax_xy.set_ylabel("Y (m)")
    ax_yz.set_xlabel("Y (m)")
    ax_yz.set_ylabel("Z (m)")
    ax_xz.set_xlabel("X (m)")
    ax_xz.set_ylabel("Z (m)")
    ax_xy.set_xlim(0, 2)
    ax_xy.set_ylim(-0.2, 0.2)
    ax_yz.set_xlim(-0.2, 0.2)
    ax_yz.set_ylim(-0.2, 0.2)
    ax_xz.set_xlim(0, 2)
    ax_xz.set_ylim(-0.2, 0.2)
    # ax_xy.view_init(azim=270, elev=90)
    # ax_yz.view_init(azim=90, elev=90)
    # ax_xz.view_init(azim=270, elev=0)

    return fig, (ax_3d, ax_xy, ax_yz, ax_xz)


def segment_pts(pts):
    # segments_3d = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    # segments_xy = [(pts[i, [True, True, False]], pts[i + 1, [True, True, False]]) for i in range(len(pts) - 1)]
    # segments_yz = [(pts[i, [False, True, True]], pts[i + 1, [False, True, True]]) for i in range(len(pts) - 1)]
    # segments_xz = [(pts[i, [True, False, True]], pts[i + 1, [True, False, True]]) for i in range(len(pts) - 1)]
    pts = np.transpose(pts)
    segments_3d = [(pts[:, i], pts[:, i + 1]) for i in range(pts.shape[1] - 1)]
    segments_xy = [(pts[[True, True, False], i], pts[[True, True, False], i + 1]) for i in range(pts.shape[1] - 1)]
    segments_yz = [(pts[[False, True, True], i], pts[[False, True, True], i + 1]) for i in range(pts.shape[1] - 1)]
    segments_xz = [(pts[[True, False, True], i], pts[[True, False, True], i + 1]) for i in range(pts.shape[1] - 1)]
    return segments_3d, segments_xy, segments_yz, segments_xz


def detect_ar_tag(img, apriltag_detector, estimate_tag_pose=False, camera_params=None, tag_size=None):
    # start = datetime.now()
    tags = apriltag_detector.detect(img, estimate_tag_pose=estimate_tag_pose, camera_params=camera_params,
                                    tag_size=tag_size)
    # print((datetime.now() - start).total_seconds())
    return tags


def draw_wand(fig, axs, backgrounds, rings, handles, spline_midpoints: np.ndarray,
              pos: np.ndarray, R: np.ndarray, change_perspective: bool = False):
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
    global ring_pts
    swap = np.array([[0, 0, 1],
                     [-1, 0, 0],
                     [0, -1, 0]])  # change camera perspective to best viewing perspective

    # update ring points
    pts = np.transpose(np.matmul(R, np.transpose(ring_pts))) + np.ndarray.flatten(pos)
    if change_perspective:
        pts = np.transpose(np.matmul(swap, np.transpose(pts)))

    pts_midpoints = (pts[:-1] + pts[1:])/2
    distances = np.array([np.min([np.linalg.norm(spline_midpoint - pts_midpoint) for spline_midpoint in spline_midpoints]) for
                 pts_midpoint in pts_midpoints])
    pos_swapped = np.matmul(swap, pos).flatten()
    distances_to_center = np.min(
        [np.linalg.norm(spline_midpoint - pos_swapped) for spline_midpoint in spline_midpoints])
    inside = distances_to_center < ring_r_inner
    colors = []
    if not inside:
        distances -= np.min(distances)
    print(distances)
    for d in distances:
        # colors.append((np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
        if d > ring_r_inner*2/3:
            colors.append((0, 1, 0))
        elif d > 0 and inside or (d > ring_r_inner*1/3 and not inside):
            colors.append((1, 1, 0))
        else:
            colors.append((1, 0, 0))

    segments = segment_pts(pts)
    for ring, segment in zip(rings, segments):
        ring.set_segments(segment)
        ring.set_colors(colors)
        # if inside:
        #     # ring.set_alpha(0.5)
        #     # ring.set_linewidth(3)
        #     ring.set_linestyle("--")
        # else:
        #     # ring.set_alpha(1)
        #     # ring.set_linewidth(5)
        #     ring.set_linestyle("-")

    # update handle
    pts = [(ring_r_inner, 0, 0), (ring_r_outer + handle_length, 0, 0)]
    pts = np.reshape(pts, (2, 3))
    pts = np.transpose(np.matmul(R, np.transpose(pts))) + np.ndarray.flatten(pos)
    if change_perspective:
        pts = np.transpose(np.matmul(swap, np.transpose(pts)))
    handles[0].set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])
    handles[1].set_data(pts[:, 0], pts[:, 1])
    handles[2].set_data(pts[:, 1], pts[:, 2])
    handles[3].set_data(pts[:, 0], pts[:, 2])

    # this method is based on https://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
    # https://stackoverflow.com/questions/40126176/fast-live-plotting-in-matplotlib-pyplot
    return inside


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
    tag_size = 2.5*INCH_TO_METERS  # 2.875*INCH_TO_METERS # 2.5*INCH_TO_METERS


    # Compute spline curve
    N_curve = 100
    x_min = 0.25
    x_max = 1.5
    curve = []
    # curve_z = lambda x: 0.05*(np.sin(4*x) + np.cos(7*x))
    curve_y = lambda x: 0.0
    # curve_y = lambda x: 0.025*(np.sin(5*x) + np.cos(6*x))
    curve_z = lambda x: 0.075*(np.sin(5*x) + np.cos(6*x))
    for x in np.linspace(x_min, x_max, N_curve):
        curve += [np.array([x, curve_y(x - x_min), curve_z(x - x_min)])]
    curve = np.array(curve)
    curve_midpoints = (curve[:-1] + curve[1:])/2
    print(curve)

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
    # plt.rcParams["figure.figsize"] = [15, 10]
    plt.rcParams["figure.figsize"] = [10, 7.5]
    # plt.ion()
    fig, axs = setup_plot()
    ax_3d, ax_xy, ax_yz, ax_xz = axs
    # ring, = plt.plot([], [], lw=3)  # , lw=(ring_r_outer-ring_r_inner)/2)

    # ring_segments = [(ring_pts[i], ring_pts[i + 1]) for i in range(len(ring_pts) - 1)]
    segments = segment_pts(ring_pts)
    colors = [(0, 1, 0) for _ in range(len(segments[0]))]
    rings = [Line3DCollection([], colors=[], linewidths=3)]
    for i in range(1, 4):
        rings += [LineCollection([], colors=[], linewidths=3)]
    for ax, ring in zip(axs, rings):
        ax.add_collection(ring)
    handles = [ax.plot([], [], lw=3)[0] for ax in axs]
    splines = [ax_3d.plot(curve[:, 0], curve[:, 1], curve[:, 2], lw=5),
               ax_xy.plot(curve[:, 0], curve[:, 1], lw=5),
               ax_yz.plot(curve[:, 1], curve[:, 2], lw=5),
               ax_xz.plot(curve[:, 0], curve[:, 2], lw=5)]
    update_text = plt.gcf().text(0.02, 0.9, "", fontsize=14, color="black")
    plt.tight_layout()

    fig.canvas.draw()
    backgrounds = [fig.canvas.copy_from_bbox(ax.bbox) for ax in axs]
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

        if len(tags) > 0:
            inside = draw_wand(fig, axs, backgrounds, rings, handles, curve_midpoints, tags[0].pose_t, tags[0].pose_R, change_perspective=True)
            if inside:
                update_text.set_text("Good Job!")
                update_text.set_color("black")
            else:
                update_text.set_text("GET BACK IN THE GAME!")
                update_text.set_color("red")

            for background, ax, ring, handle in zip(backgrounds, axs, rings, handles):
                fig.canvas.restore_region(background)
                ax.draw_artist(ring)
                ax.draw_artist(handle)
                fig.canvas.blit(ax.bbox)
            # fig.canvas.update()
            fig.canvas.flush_events()
            plt.draw()
        # cv2.imshow('Camera Feed', cv2.resize(frame, (640, 360)))
        cv2.imshow('Camera Feed', frame)
        key_input = cv2.waitKey(1) & 0xFF
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

        if num_loops == print_every:
            fps = 1./np.array(times)
            print("Avg. FPS:", np.mean(fps), np.std(fps), np.min(fps), np.max(fps), np.sort(times)[:10], count)
            # #     print("Avg. FPS:", print_every/(datetime.now() - lastTime).total_seconds())
            # #     lastTime = datetime.now()
            num_loops = 0

    vid.release()
    cv2.destroyAllWindows()
