import numpy as np
import matplotlib.pyplot as plt


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


if __name__ == "__main__":
    control_pts = [[0, 0, 0],
                   [1, 2, 0],
                   [2, -2, 0],
                   [3, 2, 0],
                   [4, 1, 0],
                   [5, 0, 0],
                   [6, 0, 0]]
    tangents = [[1, 0, 0]]*len(control_pts)  # every tangent = in z-direction

    # Compute spline curve
    num_points_per_spline = 10
    curve = []
    for i in range(len(control_pts) - 1):
        for t in np.linspace(0, 1, num_points_per_spline)[:-1]:
            curve += [hermite_interpolation(t, np.array(control_pts[i]), np.array(control_pts[i + 1]),
                                            np.array(tangents[i]), np.array(tangents[i + 1]))]
    curve += [np.array(control_pts[-1])]
    curve = np.array(curve)

    # Plot
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.plot(curve[:, 0], curve[:, 1], curve[:, 2])
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    plt.show()
