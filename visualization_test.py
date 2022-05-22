import mpl_toolkits.mplot3d.art3d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

thickness = 0.02*2  # thickness of wand
ring_r_inner = 0.075/2  # inner radius of the ring (m)
ring_r_outer = 0.045  # outer radius of the ring (m)
handle_length = 0.130  # handle length
handle_width = 0.03  # handle width


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
              pos: np.ndarray, R: np.ndarray, N: int = 10):
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
    # update ring points
    ring_r_avg = (ring_r_outer + ring_r_inner)/2
    pts = [(ring_r_avg*np.cos(t), ring_r_avg*np.sin(t), 0) for t in np.linspace(0, 2*np.pi, N)]
    pts = np.reshape(pts, (N, 3))
    pts = np.transpose(np.matmul(R, np.transpose(pts))) + pos
    ring.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])

    # update handle
    pts = [(0, -ring_r_inner, 0), (0, -ring_r_outer - handle_length, 0)]
    pts = np.reshape(pts, (2, 3))
    pts = np.transpose(np.matmul(R, np.transpose(pts))) + pos
    handle.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])

    return ring, handle


if __name__ == "__main__":
    control_pts = [[0, 0, 0], [1, 2, 0], [2, -2, 0], [3, 2, 0], [4, 1, 0], [5, 0, 0], [6, 0, 0]]
    tangents = [[1, 0, 0]]*len(control_pts)  # every tangent = in x-direction

    # Compute spline curve
    num_points_per_spline = 20
    curve = []
    for i in range(len(control_pts) - 1):
        for t in np.linspace(0, 1, num_points_per_spline, endpoint=False):
            curve += [hermite_interpolation(t, np.array(control_pts[i]), np.array(control_pts[i + 1]),
                                            np.array(tangents[i]), np.array(tangents[i + 1]))]
    curve += [np.array(control_pts[-1])]
    curve = np.array(curve)

    # Setup plot
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.grid(False)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ring, = plt.plot([], [])  # , lw=(ring_r_outer-ring_r_inner)/2)
    handle, = plt.plot([], [])

    # Plot spline curve
    # ax.plot(curve[:, 0], curve[:, 1], curve[:, 2])
    ring, handle = draw_wand(ax, ring, handle, np.array([0, 0, 1]), np.eye(3))
    print(type(ring))

    plt.show()

    while True:
        plt.draw()
        plt.pause(0.01)

    # Show plot
    # plt.tight_layout()
