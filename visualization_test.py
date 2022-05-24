import mpl_toolkits.mplot3d.art3d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

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


def draw_wand(ax: Axes3D, ring: Line3DCollection, handle: mpl_toolkits.mplot3d.art3d.Line3D,
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
    # ring.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])
    ring_segments = [(pts[i], pts[i + 1]) for i in range(len(ring_pts) - 1)]
    print(ring_segments)
    ring.set_segments(ring_segments)
    colors = [(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)) for _ in range(len(ring_segments))]
    ring.set_colors(colors)

    # update handle
    pts = [(0, -ring_r_inner, 0), (0, -ring_r_outer - handle_length, 0)]
    pts = np.reshape(pts, (2, 3))
    pts = np.transpose(np.matmul(R, np.transpose(pts))) + pos
    handle.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])

    return ring, handle


def closestDistanceBetweenLines(a0, a1, b0, b1, clampAll=False, clampA0=False, clampA1=False, clampB0=False,
                                clampB1=False):
    """
    Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
    Returns the closest points on each segment and their distance
    Source: https://stackoverflow.com/questions/2824478/shortest-distance-between-two-line-segments

    :param a0:
    :param a1:
    :param b0:
    :param b1:
    :param clampAll:
    :param clampA0:
    :param clampA1:
    :param clampB0:
    :param clampB1:
    :return:
    """

    # If clampAll=True, set all clamps to True
    if clampAll:
        clampA0 = True
        clampA1 = True
        clampB0 = True
        clampB1 = True

    # Calculate denomitator
    A = a1 - a0
    B = b1 - b0
    magA = np.linalg.norm(A)
    magB = np.linalg.norm(B)

    _A = A/magA
    _B = B/magB

    cross = np.cross(_A, _B)
    denom = np.linalg.norm(cross)**2

    # If lines are parallel (denom=0) test if lines overlap.
    # If they don't overlap then there is a closest point solution.
    # If they do overlap, there are infinite closest positions, but there is a closest distance
    if not denom:
        d0 = np.dot(_A, (b0 - a0))

        # Overlap only possible with clamping
        if clampA0 or clampA1 or clampB0 or clampB1:
            d1 = np.dot(_A, (b1 - a0))

            # Is segment B before A?
            if d0 <= 0 >= d1:
                if clampA0 and clampB1:
                    if np.absolute(d0) < np.absolute(d1):
                        return a0, b0, np.linalg.norm(a0 - b0)
                    return a0, b1, np.linalg.norm(a0 - b1)


            # Is segment B after A?
            elif d0 >= magA <= d1:
                if clampA1 and clampB0:
                    if np.absolute(d0) < np.absolute(d1):
                        return a1, b0, np.linalg.norm(a1 - b0)
                    return a1, b1, np.linalg.norm(a1 - b1)

        # Segments overlap, return distance between parallel segments
        return None, None, np.linalg.norm(((d0*_A) + a0) - b0)

    # Lines criss-cross: Calculate the projected closest points
    t = (b0 - a0)
    detA = np.linalg.det([t, _B, cross])
    detB = np.linalg.det([t, _A, cross])

    t0 = detA/denom
    t1 = detB/denom

    pA = a0 + (_A*t0)  # Projected closest point on segment A
    pB = b0 + (_B*t1)  # Projected closest point on segment B

    # Clamp projections
    if clampA0 or clampA1 or clampB0 or clampB1:
        if clampA0 and t0 < 0:
            pA = a0
        elif clampA1 and t0 > magA:
            pA = a1

        if clampB0 and t1 < 0:
            pB = b0
        elif clampB1 and t1 > magB:
            pB = b1

        # Clamp projection A
        if (clampA0 and t0 < 0) or (clampA1 and t0 > magA):
            dot = np.dot(_B, (pA - b0))
            if clampB0 and dot < 0:
                dot = 0
            elif clampB1 and dot > magB:
                dot = magB
            pB = b0 + (_B*dot)

        # Clamp projection B
        if (clampB0 and t1 < 0) or (clampB1 and t1 > magB):
            dot = np.dot(_A, (pB - a0))
            if clampA0 and dot < 0:
                dot = 0
            elif clampA1 and dot > magA:
                dot = magA
            pA = a0 + (_A*dot)

    return pA, pB, np.linalg.norm(pA - pB)


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
    # ring, = plt.plot([], [])  # , lw=(ring_r_outer-ring_r_inner)/2)

    N = 10
    ring_r_avg = (ring_r_outer + ring_r_inner)/2
    ring_pts = [(ring_r_avg*np.cos(t), ring_r_avg*np.sin(t), 0) for t in np.linspace(0, 2*np.pi, N)]
    ring_segments = [(ring_pts[i], ring_pts[i + 1]) for i in range(len(ring_pts) - 1)]
    colors = [(0, 255, 0) for _ in range(len(ring_segments))]
    ring = Line3DCollection(ring_segments, colors=colors, linewidths=2)
    ax.add_collection(ring)
    handle, = plt.plot([], [])

    # Plot spline curve
    # ax.plot(curve[:, 0], curve[:, 1], curve[:, 2])
    pos = np.array([0, 0, 1])
    R = np.eye(3)
    ring, handle = draw_wand(ax, ring, handle, pos, R, N=N)

    print(type(ring))

    # plt.show()

    while True:
        ring, handle = draw_wand(ax, ring, handle, pos, R, N=N)
        plt.draw()
        plt.pause(0.01)

    # Show plot
    # plt.tight_layout()
