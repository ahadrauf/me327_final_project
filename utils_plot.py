import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Line3D
from scipy.spatial.distance import cdist
from typing import Tuple, List, Callable
from enum import Enum

matplotlib.use('Qt5Agg')


class GamePhase(Enum):
    Exploring = 1
    NavigatingToOrigin = 2
    Playing = 3


def setup_plot() -> Tuple[plt.Figure, Tuple[Axes3D, plt.Axes, plt.Axes, plt.Axes]]:
    # plt.rcParams["figure.figsize"] = [10, 7.5]
    plt.rcParams["figure.figsize"] = [12.5, 7.5]
    fig = plt.figure()
    ax_3d = fig.add_subplot(121, projection='3d')
    ax_xy = fig.add_subplot(322)
    ax_yz = fig.add_subplot(324)
    ax_xz = fig.add_subplot(326)

    for ax in [ax_3d, ax_xy, ax_yz, ax_xz]:
        ax.grid(False)

    # Setup 3D plot
    # ax_3d.set_title("3D Projection")
    ax_3d.set_xlabel("X (m)")
    ax_3d.set_ylabel("Y (m)")
    ax_3d.set_zlabel("Z (m)")
    ax_3d.set_xlim(0, 1.5)
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
    ax_xy.set_xlim(0, 1.5)
    ax_xy.set_ylim(-0.2, 0.2)
    ax_yz.set_xlim(-0.2, 0.2)
    ax_yz.set_ylim(-0.2, 0.2)
    ax_xz.set_xlim(0, 1.5)
    ax_xz.set_ylim(-0.2, 0.2)
    # ax_xy.view_init(azim=270, elev=90)
    # ax_yz.view_init(azim=90, elev=90)
    # ax_xz.view_init(azim=270, elev=0)

    return fig, (ax_3d, ax_xy, ax_yz, ax_xz)


def initialize_plot_objects(fig: plt.Figure, axs: Tuple[Axes3D, plt.Axes, plt.Axes, plt.Axes], curve: np.ndarray):
    """
     -> \
        Tuple[Tuple[Line3DCollection, LineCollection, LineCollection, LineCollection],
        Tuple[Line3D, plt.Line2D, plt.Line2D, plt.Line2D],
        Tuple[Line3D, plt.Line2D, plt.Line2D, plt.Line2D],
        plt.Text]
    :param fig:
    :param axs:
    :param curve: (Nx3) Curve array
    :return:
    """
    ax_3d, ax_xy, ax_yz, ax_xz = axs
    rings = (Line3DCollection([], colors=[], linewidths=3), LineCollection([], colors=[], linewidths=3),
             LineCollection([], colors=[], linewidths=3), LineCollection([], colors=[], linewidths=3))
    for ax, ring in zip(axs, rings):
        ax.add_collection(ring)
    handles = [ax.plot([], [], lw=3)[0] for ax in axs]
    # splines = [ax_3d.plot(curve[:, 0], curve[:, 1], curve[:, 2], lw=5)[0],
    #            ax_xy.plot(curve[:, 0], curve[:, 1], lw=5)[0],
    #            ax_yz.plot(curve[:, 1], curve[:, 2], lw=5)[0],
    #            ax_xz.plot(curve[:, 0], curve[:, 2], lw=5)[0]]
    splines = [ax.plot([], [], lw=5)[0] for ax in axs]
    status_text = plt.gcf().text(0.02, 0.95, "", fontsize=14, color="black")
    update_text = plt.gcf().text(0.02, 0.9, "", fontsize=14, color="black")
    plt.tight_layout()

    fig.canvas.draw()
    backgrounds = [fig.canvas.copy_from_bbox(ax.bbox) for ax in axs]
    update_curve(splines, curve)
    plt.show(block=False)
    return rings, handles, splines, status_text, update_text, backgrounds


def update_curve(splines: Tuple[Line3D, plt.Line2D, plt.Line2D, plt.Line2D], curve: np.ndarray) -> None:
    splines[0].set_data_3d(curve[:, 0], curve[:, 1], curve[:, 2])
    splines[1].set_data(curve[:, 0], curve[:, 1])
    splines[2].set_data(curve[:, 1], curve[:, 2])
    splines[3].set_data(curve[:, 0], curve[:, 2])
    print("Updated Curve")


def segment_pts(pts: np.ndarray) -> Tuple[List, List, List, List]:
    """
    Break up an 3xN points array into the segments required for plotting via the LineCollection matplotlib objects
    Returns 4 lists, one for the 3D plot, and three for each of the xy, yz, and xz 2D projections
    :param pts: Points array (3xN)
    :return: (segments_3d, segments_xy, segments_yz, segments_xz)
    """
    segments_3d = [(pts[:, i], pts[:, i + 1]) for i in range(pts.shape[1] - 1)]
    segments_xy = [(pts[[True, True, False], i], pts[[True, True, False], i + 1]) for i in range(pts.shape[1] - 1)]
    segments_yz = [(pts[[False, True, True], i], pts[[False, True, True], i + 1]) for i in range(pts.shape[1] - 1)]
    segments_xz = [(pts[[True, False, True], i], pts[[True, False, True], i + 1]) for i in range(pts.shape[1] - 1)]
    return segments_3d, segments_xy, segments_yz, segments_xz


def initialize_ring(radius, N) -> np.ndarray:
    ring_pts = np.zeros((3, N))
    for i, t in enumerate(np.linspace(0, 2*np.pi, N)):
        ring_pts[:, i] = [radius*np.cos(t), radius*np.sin(t), 0]
    return ring_pts


def initialize_handle(radius, handle_length) -> np.ndarray:
    handle_pts = np.zeros((3, 2))
    handle_pts[:, 0] = [radius, 0, 0]
    handle_pts[:, 1] = [radius + handle_length, 0, 0]
    return handle_pts


def initialize_curve(x_min: float, x_max: float, curve_y: Callable, curve_z: Callable, N: int) -> Tuple[
    np.ndarray, np.ndarray]:
    """
    Initialize the curve, using the functions curve_y(x) and curve_z(x)
    :param x_min: Minimum
    :param x_max:
    :param curve_y:
    :param curve_z:
    :param N: number of points
    :return:
    """
    curve = np.zeros((N, 3))
    for i, x in enumerate(np.linspace(x_min, x_max, N)):
        curve[i, :] = [x, curve_y(x - x_min), curve_z(x - x_min)]
    curve_midpoints = (curve[:-1] + curve[1:])/2
    return curve, curve_midpoints


def update_ring(rings: Tuple[Line3DCollection, LineCollection, LineCollection, LineCollection], pos: np.ndarray,
                R: np.ndarray, ring_pts: np.ndarray, curve_midpoints: np.ndarray, camera2World: np.ndarray,
                ring_radius: float) -> bool:
    """
    Updates the 3D visualization for the ring
    :param rings: 3D line collections used to draw the rings
    :param pos: (3x1) Location of the center of the ring in the camera frame
    :param R: Rotation matrix in the camera frame
    :param ring_pts: (3xNring) matrix of the
    :param curve_midpoints: (Ncurvex3) Midpoints of the spline, for distance measurements
    :param camera2World: Mapping matrix from the camera frame to the world frame for plotting
    :param ring_radius: radius of ring
    :return: Whether the curve is inside the ring
    """
    pts = np.matmul(camera2World, np.matmul(R, ring_pts) + pos)  # 3xN
    pts_midpoints = (pts[:, :-1] + pts[:, 1:])/2
    distances_to_ring = np.min(cdist(pts_midpoints.T, curve_midpoints), axis=1)  # (Nring, )
    pos_swapped = np.matmul(camera2World, pos).reshape(1, 3)
    distances_to_center = cdist(pos_swapped, curve_midpoints)[0]
    distance_to_center_idx = np.argmin(distances_to_center)  # float
    distance_to_center = distances_to_center[distance_to_center_idx]
    vector_to_center = pos_swapped - curve_midpoints[distance_to_center_idx, :]

    # this technically doesn't map the distance to the plane of the ring, but it's sufficient for the relatively small
    # angles we expect users to tilt the handle too
    inside = distance_to_center < ring_radius
    if not inside:
        distances_to_ring -= np.min(distances_to_ring)

    # Color Mapping
    colors = np.zeros((len(distances_to_ring), 3))
    for i, d in enumerate(distances_to_ring):
        if d > ring_radius*2/3:
            colors[i, :] = (0, 1, 0)
        elif (d > 0 and inside) or (d > ring_radius*1/3 and not inside):
            colors[i, :] = (1, 1, 0)
        else:
            colors[i, :] = (1, 0, 0)

    # Set ring points and colors
    segments = segment_pts(pts)
    for ring, segment in zip(rings, segments):
        ring.set_segments(segment)
        ring.set_colors(colors)

    return inside


def update_handle(handles: Tuple[Line3D, plt.Line2D, plt.Line2D, plt.Line2D], pos: np.ndarray,
                  R: np.ndarray, handle_pts: np.ndarray, camera2World: np.ndarray, inside: bool) -> None:
    """
    Updates the 3D visualization for the handle
    :param handles: 3D line collections used to draw the rings
    :param pos: (3x1) Location of the center of the ring in the camera frame
    :param R: Rotation matrix in the camera frame
    :param handle_pts: (3xNring) matrix of the
    :param camera2World: Mapping matrix from the camera frame to the world frame for plotting
    :param inside: Whether the ring is inside the curve or not
    :return: None
    """
    pts = np.matmul(camera2World, np.matmul(R, handle_pts) + pos)  # 3xN
    color = (0, 1, 0) if inside else (1, 0, 0)

    # Set ring points and colors
    handles[0].set_data_3d(pts[0, :], pts[1, :], pts[2, :])
    handles[1].set_data(pts[0, :], pts[1, :])
    handles[2].set_data(pts[1, :], pts[2, :])
    handles[3].set_data(pts[0, :], pts[2, :])
    for handle in handles:
        handle.set_color(color)
