import numpy as np
from scipy import integrate

from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainterPath, QPen, QFont, QBrush
from PySide6.QtCore import Qt, QPointF, QRectF

from helixpoint import HelixPoint
from helixpoint import ReferencePoint


class PathCurve(QGraphicsItem):
    PAINTING_POINTS: int = 200

    def __init__(self, start, stop, R, scene, parent=None):
        super().__init__(parent)
        self.start = start
        self.stop = stop
        self.scene = scene

        self.t, self.x, self.y, self.z = self.construct_knots()
        self.P_x = self.solve_splines(self.t, self.x)
        self.P_y = self.solve_splines(self.t, self.y)
        self.P_z = self.solve_splines(self.t, self.z)

        self.R = R
        self.translation = np.zeros((3, 1))
        self.helix_knots = {}

        self.hclasses = {}

        self.painting_points, self.T_ijs, self.N_ijs, self.B_ijs = self.solve_painting_points(self.P_x, self.P_y, self.P_z, self.t)
        self.helix_curves = self.construct_helix_curves()
        self.construct_helix_splines(self.t, self.P_x, self.P_y, self.P_z)
        self.target_angles = self.solve_target_angles()
        self.helix_painting_points, self.mod_maps, self.twist_maps, self.twist_maps_num = self.solve_mods(self.P_x, self.P_y, self.P_z, self.t, self.scene.parent().get_parameters()["rho_start"])

    def get_hknots(self):
        return self.helix_knots

    def update_mods(self, rho):
        self.helix_painting_points, self.mod_maps, self.twist_maps, self.twist_maps_num = self.solve_mods(self.P_x, self.P_y, self.P_z, self.t, rho)

    def solve_target_angles(self):
        target_angles = []
        selected_helices = {}
        for item in self.start.get_cs_scene().items():
            if isinstance(item, HelixPoint) and item.has_selection():
                selected_helices[item.get_number()] = item
        for helix_1 in sorted(selected_helices):
            new_row = []
            for helix_2 in sorted(selected_helices):
                neighbours = False
                target_h1 = 0
                target_h2 = 0
                d_lim = self.scene.parent().get_parameters()['hd'] + self.scene.parent().get_parameters()['ihg']
                d_12 = (np.sqrt((selected_helices[helix_1].x() - selected_helices[helix_2].x()) ** 2 + (selected_helices[helix_1].y() - selected_helices[helix_2].y()) ** 2)) / 10
                if d_12 <= d_lim + 0.2 and helix_1 != helix_2:
                    neighbours = True
                    r_1 = np.array([selected_helices[helix_1].x(), selected_helices[helix_1].y()])
                    r_2 = np.array([selected_helices[helix_2].x(), selected_helices[helix_2].y()])
                    r_12 = -r_1 + r_2
                    if helix_1 % 2 == 0:
                        target_h1 = np.abs(np.arccos(np.dot(np.array([1, 0]), r_12) / np.linalg.norm(r_12)))
                        if r_12[1] < 0:
                            target_h1 = 2*np.pi - target_h1
                    else:
                        target_h1 = np.abs(np.arccos(np.dot(np.array([-1, 0]), r_12) / np.linalg.norm(r_12)))
                        if r_12[1] > 0:
                            target_h1 = 2*np.pi - target_h1
                    r_21 = -r_2 + r_1
                    if helix_2 % 2 == 0:
                        target_h2 = np.abs(np.arccos(np.dot(np.array([1, 0]), r_21) / np.linalg.norm(r_21)))
                        if r_21[1] < 0:
                            target_h2 = 2*np.pi - target_h2
                    else:
                        target_h2 = np.abs(np.arccos(np.dot(np.array([-1, 0]), r_21) / np.linalg.norm(r_21)))
                        if r_21[1] > 0:
                            target_h2 = 2*np.pi - target_h2
                new_row.append((neighbours, target_h1, target_h2))
            target_angles.append(new_row)
        return target_angles

    def solve_helix_distance_x(self):
        dists = {}
        selected_helices = {}
        ref_point = False
        found_ref = False
        for item in self.start.get_cs_scene().items():
            if isinstance(item, HelixPoint) and item.has_selection():
                selected_helices[item.get_number()] = item
            if isinstance(item, ReferencePoint):
                ref_point = item
                found_ref = True
        if found_ref:
            for helix in sorted(selected_helices):
                dists[helix] = np.sqrt((ref_point.x() - selected_helices[helix].x()) ** 2) / 10
        return dists

    def get_helices(self):
        selected_helices = {}
        for item in self.start.get_cs_scene().items():
            if isinstance(item, HelixPoint) and item.has_selection():
                pass

    def get_neighbours(self, helix):
        neighbours = []
        selected_helices = {}
        d_lim = self.scene.parent().get_parameters()['hd'] + self.scene.parent().get_parameters()['ihg']
        for item in self.start.get_cs_scene().items():
            if isinstance(item, HelixPoint) and item.has_selection():
                selected_helices[item.get_number()] = item
        for h in sorted(selected_helices):
            d_12 = (np.sqrt((selected_helices[helix].x() - selected_helices[h].x()) ** 2 + (selected_helices[helix].y() - selected_helices[h].y()) ** 2)) / 10
            if d_12 <= d_lim + 0.2 and h != helix:
                neighbours.append(h)
        return neighbours
                    
    def has_mods(self):
        if len(self.mod_maps) >= 1:
            return True
        else:
            return False

    def get_mods(self):
        return self.mod_maps

    def get_twist(self):
        return self.twist_maps

    def get_twist_num(self):
        return self.twist_maps_num

    def construct_helix_splines(self, t, P_x, P_y, P_z):
        i = 1
        for interval in self.helix_curves:
            for helix, details in interval[0].items():
                if len(details) == 4:
                    th = [(t[i - 1], details[0], details[2]), (t[i], details[1], details[3])]
                    th_t = [t[i - 1], t[i]]
                    j = i
                    end = False
                    while not end:
                        try:
                            if helix in self.helix_curves[j][0]:
                                th.append((t[j + 1], self.helix_curves[j][0][helix][1], self.helix_curves[j][0][helix][3]))
                                th_t.append(t[j + 1])
                                j += 1
                            else:
                                end = True
                        except IndexError:
                            end = True
                    xh, yh, zh = self.construct_helix_knots(th, t, P_x, P_y, P_z)
                    self.helix_knots[helix] = [xh, yh, zh]
                    P_xh = self.solve_splines(th_t, xh)
                    P_yh = self.solve_splines(th_t, yh)
                    P_zh = self.solve_splines(th_t, zh)
                    for k in range(i - 1, j):
                        self.helix_curves[k][0][helix].append(P_xh[:, k - (i - 1)])
                        self.helix_curves[k][0][helix].append(P_yh[:, k - (i - 1)])
                        self.helix_curves[k][0][helix].append(P_zh[:, k - (i - 1)])
            i += 1

    def construct_helix_knots(self, th, t, P_x, P_y, P_z):
        xh = []
        yh = []
        zh = []
        ref_N_ij = None
        ref_B_ij = None
        for k in range(len(th)):
            for i in range(len(t)):
                if th[k][0] == t[i]:
                    if i == 0 or i == 1:
                        j = 0
                    else:
                        j = i - 1
                    S_ij = np.array(
                            [P_x[0, j] + P_x[1, j] * (t[i] - P_x[4, j]) + P_x[2, j] * (t[i] - P_x[4, j]) ** 2 + P_x[
                                3, j] * (t[i] - P_x[4, j]) ** 3,
                             P_y[0, j] + P_y[1, j] * (t[i] - P_y[4, j]) + P_y[2, j] * (t[i] - P_y[4, j]) ** 2 + P_y[
                                 3, j] * (t[i] - P_y[4, j]) ** 3,
                             P_z[0, j] + P_z[1, j] * (t[i] - P_z[4, j]) + P_z[2, j] * (t[i] - P_z[4, j]) ** 2 + P_z[
                                 3, j] * (t[i] - P_z[4, j]) ** 3])
                    S_dt_ij = np.array(
                            [P_x[1, j] + 2 * P_x[2, j] * (t[i] - P_x[4, j]) + 3 * P_x[3, j] * (t[i] - P_x[4, j]) ** 2,
                             P_y[1, j] + 2 * P_y[2, j] * (t[i] - P_y[4, j]) + 3 * P_y[3, j] * (t[i] - P_y[4, j]) ** 2,
                             P_z[1, j] + 2 * P_z[2, j] * (t[i] - P_z[4, j]) + 3 * P_z[3, j] * (t[i] - P_z[4, j]) ** 2])
                    T_ij = S_dt_ij
                    if np.linalg.norm(T_ij) != 0:
                        T_ij = (1 / np.linalg.norm(T_ij)) * T_ij
                    if ref_N_ij is None:
                        x = self.scene.get_storage().get_unit_x()
                        y = self.scene.get_storage().get_unit_y()
                        z = self.scene.get_storage().get_unit_z()
                        unit_vecs = [[x, y, z, -x, -y, -z], [y, x, x, -y, -x, x], [z, z, -y, z, z, y]]
                        dots = [np.dot(T_ij, x), np.dot(T_ij, y), np.dot(T_ij, z),
                                np.dot(T_ij, -x), np.dot(T_ij, -y), np.dot(T_ij, -z)]
                        T_base = unit_vecs[0][dots.index(max(dots))]
                        N_base = unit_vecs[1][dots.index(max(dots))]
                        B_base = unit_vecs[2][dots.index(max(dots))]
                        N_ij, B_ij = self.solve_xy_basis(T_ij, T_base, N_base, B_base)
                        if np.dot(N_ij, N_base) < 0:
                            N_ij = - N_ij
                        if np.dot(B_ij, B_base) < 0:
                            B_ij = - B_ij
                        ref_N_ij, ref_B_ij = self.solve_plane_rotation(T_ij, N_ij, B_ij, N_base, B_base)
                    else:
                        N_ij, B_ij = self.solve_xy_basis(T_ij, T_base, N_base, B_base)
                        N_ij, B_ij = self.solve_plane_rotation(T_ij, N_ij, B_ij, ref_N_ij, ref_B_ij)
                        ref_N_ij = N_ij
                        ref_B_ij = B_ij
                    R = th[k][1] / 10
                    theta = th[k][2]
                    h = S_ij + R * np.cos(theta) * N_ij + R * np.sin(theta) * B_ij
                    xh.append(h[0])
                    yh.append(h[1])
                    zh.append(h[2])
        return xh, yh, zh

    def rotate_projection(self, R):
        self.R = np.matmul(R, self.R)

    def translate(self, dx, dy, dz):
        self.translation = self.translation + np.array([[dx], [dy], [dz]])

    def construct_helix_curves(self):
        start = self.start
        stop = self.start.get_next_node()
        helix_curves = []
        closed_curve_end = False
        while stop is not None and not closed_curve_end:
            start_helices = {}
            helices = {}
            for item in start.get_cs_scene().items():
                if isinstance(item, HelixPoint):
                    if item.has_selection():
                        start_helices[item.get_number()] = item
            for item in stop.get_cs_scene().items():
                if isinstance(item, HelixPoint):
                    if item.has_selection() and item.get_number() in start_helices:
                        helices[item.get_number()] = (start_helices[item.get_number()], item)
            interval_details = {}
            for number, helix_pair in helices.items():
                ref_x = start.get_ref_point().x()
                ref_y = start.get_ref_point().y()
                x = helix_pair[0].x()
                y = helix_pair[0].y()
                R_start = np.sqrt((x - ref_x) ** 2 + (y - ref_y) ** 2)
                if (x - ref_x) == 0 and (y - ref_y) == 0:
                    theta_start = 0
                elif (x - ref_x) == 0:
                    if y >= ref_y:
                        theta_start = np.pi / 2
                    else:
                        theta_start = - np.pi / 2
                elif (y - ref_y) == 0:
                    if x >= ref_x:
                        theta_start = 0
                    else:
                        theta_start = np.pi
                elif x > ref_x and y < ref_y:
                    theta_start = - np.arctan(np.abs(y - ref_y) / np.abs(x - ref_x))
                elif x < ref_x and y < ref_y:
                    theta_start = - (np.pi - np.arctan(np.abs(y - ref_y) / np.abs(x - ref_x)))
                elif x < ref_x and y > ref_y:
                    theta_start = (np.pi - np.arctan(np.abs(y - ref_y) / np.abs(x - ref_x)))
                else:
                    theta_start = np.arctan(np.abs(y - ref_y) / np.abs(x - ref_x))
                ref_x = stop.get_ref_point().x()
                ref_y = stop.get_ref_point().y()
                x = helix_pair[1].x()
                y = helix_pair[1].y()
                R_stop = np.sqrt((x - ref_x) ** 2 + (y - ref_y) ** 2)
                if (x - ref_x) == 0 and (y - ref_y) == 0:
                    theta_stop = 0
                elif (x - ref_x) == 0:
                    if y >= ref_y:
                        theta_stop = np.pi / 2
                    else:
                        theta_stop = - np.pi / 2
                elif (y - ref_y) == 0:
                    if x >= ref_x:
                        theta_stop = 0
                    else:
                        theta_stop = np.pi
                elif x > ref_x and y < ref_y:
                    theta_stop = - np.arctan(np.abs(y - ref_y) / np.abs(x - ref_x))
                elif x < ref_x and y < ref_y:
                    theta_stop = - (np.pi - np.arctan(np.abs(y - ref_y) / np.abs(x - ref_x)))
                elif x < ref_x and y > ref_y:
                    theta_stop = (np.pi - np.arctan(np.abs(y - ref_y) / np.abs(x - ref_x)))
                else:
                    theta_stop = np.arctan(np.abs(y - ref_y) / np.abs(x - ref_x))
                interval_details[number] = [R_start, R_stop, theta_start + ((start.get_cs_angle() / 360) * 2 * np.pi),
                                            theta_stop + ((stop.get_cs_angle() / 360) * 2 * np.pi)]
            helix_curves.append([interval_details, ((start.get_cs_angle() / 360) * 2 * np.pi,
                                                    (stop.get_cs_angle() / 360) * 2 * np.pi)])
            start = stop
            stop = stop.get_next_node()
            if start is self.start:
                closed_curve_end = True
        return helix_curves

    def solve_painting_points(self, P_x, P_y, P_z, t):
        painting_points = np.zeros((3, (len(t) - 1) * self.PAINTING_POINTS))
        T_ijs = np.zeros((3, (len(t) - 1) * self.PAINTING_POINTS))
        N_ijs = np.zeros((3, (len(t) - 1) * self.PAINTING_POINTS))
        B_ijs = np.zeros((3, (len(t) - 1) * self.PAINTING_POINTS))
        ref_N_ij = None
        ref_B_ij = None
        for i in range(len(t) - 1):
            for j in range(self.PAINTING_POINTS):
                t_p = t[i] + (j / (self.PAINTING_POINTS - 1)) * (t[i + 1] - t[i])
                ind = i * self.PAINTING_POINTS + j
                painting_points[0, ind] = P_x[0, i] + P_x[1, i] * (t_p - P_x[4, i]) + P_x[2, i] * (
                        t_p - P_x[4, i]) ** 2 + P_x[3, i] * (t_p - P_x[4, i]) ** 3
                painting_points[1, ind] = P_y[0, i] + P_y[1, i] * (t_p - P_y[4, i]) + P_y[2, i] * (
                        t_p - P_y[4, i]) ** 2 + P_y[3, i] * (t_p - P_y[4, i]) ** 3
                painting_points[2, ind] = P_z[0, i] + P_z[1, i] * (t_p - P_z[4, i]) + P_z[2, i] * (
                        t_p - P_z[4, i]) ** 2 + P_z[3, i] * (t_p - P_z[4, i]) ** 3
                S_dt_ij = np.array(
                    [P_x[1, i] + 2 * P_x[2, i] * (t_p - P_x[4, i]) + 3 * P_x[3, i] * (t_p - P_x[4, i]) ** 2,
                     P_y[1, i] + 2 * P_y[2, i] * (t_p - P_y[4, i]) + 3 * P_y[3, i] * (t_p - P_y[4, i]) ** 2,
                     P_z[1, i] + 2 * P_z[2, i] * (t_p - P_z[4, i]) + 3 * P_z[3, i] * (t_p - P_z[4, i]) ** 2])
                T_ij = S_dt_ij
                if np.linalg.norm(T_ij) != 0:
                    T_ij = (1 / np.linalg.norm(T_ij)) * T_ij
                if ref_N_ij is None:
                    x = self.scene.get_storage().get_unit_x()
                    y = self.scene.get_storage().get_unit_y()
                    z = self.scene.get_storage().get_unit_z()
                    unit_vecs = [[x, y, z, -x, -y, -z], [y, x, x, -y, -x, x], [z, z, -y, z, z, y]]
                    dots = [np.dot(T_ij, x), np.dot(T_ij, y), np.dot(T_ij, z),
                            np.dot(T_ij, -x), np.dot(T_ij, -y), np.dot(T_ij, -z)]
                    T_base = unit_vecs[0][dots.index(max(dots))]
                    N_base = unit_vecs[1][dots.index(max(dots))]
                    B_base = unit_vecs[2][dots.index(max(dots))]
                    N_ij, B_ij = self.solve_xy_basis(T_ij, T_base, N_base, B_base)
                    if np.dot(N_ij, N_base) < 0:
                        N_ij = - N_ij
                    if np.dot(B_ij, B_base) < 0:
                        B_ij = - B_ij
                    ref_N_ij, ref_B_ij = self.solve_plane_rotation(T_ij, N_ij, B_ij, N_base, B_base)
                else:
                    N_ij, B_ij = self.solve_xy_basis(T_ij, T_base, N_base, B_base)
                    N_ij, B_ij = self.solve_plane_rotation(T_ij, N_ij, B_ij, ref_N_ij, ref_B_ij)
                    ref_N_ij = N_ij
                    ref_B_ij = B_ij
                T_ijs[0:3, ind] = T_ij
                N_ijs[0:3, ind] = N_ij
                B_ijs[0:3, ind] = B_ij
        return painting_points, T_ijs, N_ijs, B_ijs

    @staticmethod
    def solve_xy_basis(T_ij, T_base, N_base, B_base):
        c = np.linalg.cross(T_base, T_ij)
        d = np.dot(T_base, T_ij)
        if not np.array_equal(c, np.array([0, 0, 0])):
            Z = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
            R = (np.identity(3) + Z + np.matmul(Z, Z) * (1 - d) / (np.linalg.norm(c) ** 2)) / (
                    np.linalg.norm(T_base) ** 2)
        else:
            R = np.sign(d) * (np.linalg.norm(T_ij) / np.linalg.norm(T_base))
        return np.matmul(R, N_base), np.matmul(R, B_base)

    def solve_plane_rotation(self, T_ij, N_ij, B_ij, ref_N_ij, ref_B_ij):
        delta_lim = 0.05
        d_lims = [None, None]
        start_thetas = [n * np.pi / 32 for n in range(0, 65)]
        interval = [None, None]
        for i in range(len(start_thetas)):
            R = self.rotation_matrix_around_axis(T_ij, start_thetas[i])
            d_N = np.linalg.norm(np.matmul(R, N_ij) - ref_N_ij)
            d_B = np.linalg.norm(np.matmul(R, B_ij) - ref_B_ij)
            d = d_N + d_B
            if d_lims[0] is None or d < d_lims[0]:
                interval[0] = start_thetas[i]
                d_lims[0] = d
            elif d_lims[1] is None or d < d_lims[1]:
                interval[1] = start_thetas[i]
                d_lims[1] = d
        delta = 1
        reps = 0
        while delta >= delta_lim and reps < 50:
            half_point_theta = (interval[0] + interval[1]) / (2 ** (reps + 1))
            R = self.rotation_matrix_around_axis(T_ij, half_point_theta)
            d_N = np.linalg.norm(np.matmul(R, N_ij) - ref_N_ij)
            d_B = np.linalg.norm(np.matmul(R, B_ij) - ref_B_ij)
            d = d_N + d_B
            if d_lims[0] is None or d < d_lims[0]:
                interval[0] = half_point_theta
                delta = d_lims[0] - d
                d_lims[0] = d
            elif d_lims[1] is None or d < d_lims[1]:
                interval[1] = half_point_theta
                delta = d_lims[1] - d
                d_lims[1] = d
            else:
                reps += 1
        R = self.rotation_matrix_around_axis(T_ij, interval[0])
        return np.matmul(R, N_ij), np.matmul(R, B_ij)

    @staticmethod
    def rotation_matrix_around_axis(A, theta):
        R = np.array([[A[0] * A[0] * (1 - np.cos(theta)) + np.cos(theta),
                       A[0] * A[1] * (1 - np.cos(theta)) - A[2] * np.sin(theta),
                       A[0] * A[2] * (1 - np.cos(theta)) + A[1] * np.sin(theta)],
                      [A[0] * A[1] * (1 - np.cos(theta)) + A[2] * np.sin(theta),
                       A[1] * A[1] * (1 - np.cos(theta)) + np.cos(theta),
                       A[1] * A[2] * (1 - np.cos(theta)) - A[0] * np.sin(theta)],
                      [A[0] * A[2] * (1 - np.cos(theta)) - A[1] * np.sin(theta),
                       A[1] * A[2] * (1 - np.cos(theta)) + A[0] * np.sin(theta),
                       A[2] * A[2] * (1 - np.cos(theta)) + np.cos(theta)]])
        return R

    def solve_mods(self, P_x, P_y, P_z, t, rho=0):
        accumulated_mod_counts = {}
        mod_maps = {}
        twist_maps = {}
        twist_maps_num = {}
        mod_counts = {}
        offset = {}
        all_helices = []
        checkpoints = []
        right_offsets = []
        helix_painting_points = {}
        nt_length = self.scene.parent().get_parameters()['ntl']
        mod_length = self.scene.parent().get_parameters()['ml']
        turn_length = self.scene.parent().get_parameters()['tl']
        i = 1
        for interval in self.helix_curves:
            for helix in sorted(interval[0]):
                if helix not in all_helices:
                    all_helices.append(helix)
            l_ref = integrate.quad(self.gamma_dt_norm, t[i - 1], t[i], args=(P_x, P_y, P_z, t))
            if i > 1:
                abs_left_offset = nt_length - right_offsets[i - 2]
            else:
                abs_left_offset = 0
            rel_left_offset = (abs_left_offset / l_ref[0]) * (t[i] - t[i - 1])
            abs_right_offset = (l_ref[0] - abs_left_offset) % nt_length
            right_offsets.append(abs_right_offset)
            rel_right_offset = (abs_right_offset / l_ref[0]) * (t[i] - t[i - 1])
            t_values = np.linspace(t[i - 1] + rel_left_offset, t[i] - rel_right_offset,
                                   int((l_ref[0] - abs_left_offset - abs_right_offset) / nt_length) + 1)
            checkpoints.append(t_values)
            i += 1
        all_checkpoints = []
        for interval in checkpoints:
            for i in range(len(interval)):
                t_p = interval[i]
                if t_p not in all_checkpoints:
                    all_checkpoints.append(t_p)
        n = len(all_checkpoints)
        for helix in all_helices:
            mod_maps[helix] = np.zeros((1, n))
            helix_painting_points[helix] = [np.zeros((3, n)), np.zeros((1, n))]
            twist_maps[helix] = [{} for _ in range(n)]
            twist_maps_num[helix] = [{} for _ in range(n)]
            mod_counts[helix] = 0
            offset[helix] = 0
            accumulated_mod_counts[helix] = 0
        i = 1
        end = False
        current_checkpoint = all_checkpoints[1]
        for interval in self.helix_curves:
            while current_checkpoint <= t[i] and not end:
                helix_lengths = {}
                ind = all_checkpoints.index(current_checkpoint) - 1
                hclasses = {}
                for helix, details in interval[0].items():
                    row = self.target_angles[helix]
                    ncount = 0
                    for element in row:
                        if element[0]:
                            ncount += 1
                    hclasses[helix] = ncount
                self.hclasses = hclasses
                for helix, details in interval[0].items():
                    helix_painting_points[helix][0][:, ind] = self.helix_gamma(float(current_checkpoint), details[4], details[5], details[6])
                    helix_painting_points[helix][1][0, ind] = 2
                    l_helix = integrate.quad(self.helix_gamma_dt_norm, t[i - 1], float(current_checkpoint),
                                             args=(details[4], details[5], details[6]))
                    l_ref = integrate.quad(self.gamma_dt_norm, t[i - 1], float(current_checkpoint),
                                           args=(P_x, P_y, P_z, t))
                    if (l_helix[0] + mod_counts[helix] * mod_length + offset[helix]) - l_ref[0] >= mod_length:
                        mod_maps[helix][0, ind] = 1
                        mod_counts[helix] -= 1
                        accumulated_mod_counts[helix] += 1
                        helix_painting_points[helix][1][0, ind] = 1
                    elif (l_helix[0] + mod_counts[helix] * mod_length + offset[helix]) - l_ref[0] <= -mod_length:
                        mod_maps[helix][0, ind] = -1
                        mod_counts[helix] += 1
                        accumulated_mod_counts[helix] -= 1
                        helix_painting_points[helix][1][0, ind] = -1
                    helix_lengths[helix] = ((ind + accumulated_mod_counts[helix]) * nt_length) % (turn_length * nt_length)
                self.check_twist(helix_lengths, twist_maps, twist_maps_num, ind)
                if all_checkpoints.index(current_checkpoint) + 1 <= len(all_checkpoints) - 1:
                    current_checkpoint = all_checkpoints[int((all_checkpoints.index(current_checkpoint) + 1))]
                else:
                    end = True
            for helix, details in interval[0].items():
                try:
                    if helix in self.helix_curves[i]:
                        l_helix = integrate.quad(self.helix_gamma_dt_norm, t[i - 1], t[i],
                                                 args=(details[4], details[5], details[6]))
                        l_ref = integrate.quad(self.gamma_dt_norm, t[i - 1], t[i], args=(P_x, P_y, P_z, t))
                        offset[helix] = (l_helix[0] + mod_counts[helix] * mod_length + offset[helix]) - l_ref[0]
                        mod_counts[helix] = 0
                    else:
                        offset[helix] = 0
                        mod_counts[helix] = 0
                except IndexError:
                    offset[helix] = 0
                    mod_counts[helix] = 0
            i += 1
        return helix_painting_points, mod_maps, twist_maps, twist_maps_num

    def get_hclasses(self):
        return self.hclasses

    def check_twist(self, helix_lengths, twist_maps, twist_maps_num, idx):
        twist_tol = self.scene.parent().get_parameters()['tt_max']
        turn_length = self.scene.parent().get_parameters()['tl']
        nt_length = self.scene.parent().get_parameters()['ntl']
        rad_nm = 2 * np.pi / (turn_length * nt_length)
        for helix_1, length_1 in helix_lengths.items():
            for helix_2, length_2 in helix_lengths.items():
                if helix_1 != helix_2:
                    row = self.target_angles[sorted(helix_lengths).index(helix_1)]
                    element = row[sorted(helix_lengths).index(helix_2)]
                    neighbours = element[0]
                    target_h1 = element[1]
                    target_h2 = element[2]
                    delta_1 = np.abs(length_1 * rad_nm - target_h1)
                    delta_2 = np.abs(length_2 * rad_nm - target_h2)
                    if neighbours:
                        twist_maps_num[helix_1][idx][helix_2] = (delta_1 + delta_2, 0.0)
                        twist_maps_num[helix_2][idx][helix_1] = (delta_1 + delta_2, 0.0)
                    if neighbours and delta_1 < twist_tol and delta_2 < twist_tol:
                        if len(twist_maps[helix_1][idx]) < 1 and len(twist_maps[helix_2][idx]) < 1:
                            twist_maps[helix_1][idx][helix_2] = (True, False)
                            twist_maps[helix_2][idx][helix_1] = (True, False)
                        else:
                            twist_maps[helix_1][idx] = {}
                            twist_maps[helix_2][idx] = {}
                            twist_maps[helix_1][idx][helix_2] = (True, False)
                            twist_maps[helix_2][idx][helix_1] = (True, False)
                    elif neighbours and np.abs(delta_1 - np.pi) < twist_tol and np.abs(delta_2 - np.pi) < twist_tol:
                        if len(twist_maps[helix_1][idx]) < 1 and len(twist_maps[helix_2][idx]) < 1:
                            twist_maps[helix_1][idx][helix_2] = (False, True)
                            twist_maps[helix_2][idx][helix_1] = (False, True)

    @staticmethod
    def gamma_dt_norm(t_p, P_x, P_y, P_z, t):
        for i in range(len(P_x[0, :])):
            if P_x[4, i] <= t_p <= t[i + 1]:
                dx = P_x[1, i] + 2 * P_x[2, i] * (t_p - P_x[4, i]) + 3 * P_x[3, i] * (t_p - P_x[4, i]) ** 2
                dy = P_y[1, i] + 2 * P_y[2, i] * (t_p - P_y[4, i]) + 3 * P_y[3, i] * (t_p - P_y[4, i]) ** 2
                dz = P_z[1, i] + 2 * P_z[2, i] * (t_p - P_x[4, i]) + 3 * P_z[3, i] * (t_p - P_z[4, i]) ** 2
                return np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    @staticmethod
    def gamma(t_p, P_x, P_y, P_z, t):
        for i in range(len(P_x[0, :])):
            if P_x[4, i] <= t_p <= t[i + 1]:
                x = P_x[0, i] + P_x[1, i] * (t_p - P_x[4, i]) + P_x[2, i] * (t_p - P_x[4, i]) ** 2 + P_x[3, i] * (t_p - P_x[4, i]) ** 3
                y = P_y[0, i] + P_y[1, i] * (t_p - P_y[4, i]) + P_y[2, i] * (t_p - P_y[4, i]) ** 2 + P_y[3, i] * (t_p - P_y[4, i]) ** 3
                z = P_z[0, i] + P_z[1, i] * (t_p - P_z[4, i]) + P_z[2, i] * (t_p - P_z[4, i]) ** 2 + P_z[3, i] * (t_p - P_z[4, i]) ** 3
                return np.array([x, y, z])

    @staticmethod
    def gamma_unit_normal(t_p, P_x, P_y, P_z, t):
        for i in range(len(P_x[0, :])):
            if P_x[4, i] <= t_p <= t[i + 1]:
                ddx = 2 * P_x[2, i] + 6 * P_x[3, i] * (t_p - P_x[4, i])
                ddy = 2 * P_y[2, i] + 6 * P_x[3, i] * (t_p - P_x[4, i])
                ddz = 2 * P_z[2, i] + 6 * P_z[3, i] * (t_p - P_x[4, i])
                normal = np.array([ddx, ddy, ddz])
                return normal / np.linalg.norm(normal)            

    @staticmethod
    def helix_gamma_dt_norm(t_p, P_xh, P_yh, P_zh):
        dx = P_xh[1] + 2 * P_xh[2] * (t_p - P_xh[4]) + 3 * P_xh[3] * (t_p - P_xh[4]) ** 2
        dy = P_yh[1] + 2 * P_yh[2] * (t_p - P_yh[4]) + 3 * P_yh[3] * (t_p - P_yh[4]) ** 2
        dz = P_zh[1] + 2 * P_zh[2] * (t_p - P_zh[4]) + 3 * P_zh[3] * (t_p - P_zh[4]) ** 2
        return np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    @staticmethod
    def helix_gamma(t_p, P_xh, P_yh, P_zh):
        x = P_xh[0] + P_xh[1] * (t_p - P_xh[4]) + P_xh[2] * (t_p - P_xh[4]) ** 2 + P_xh[3] * (t_p - P_xh[4]) ** 3
        y = P_yh[0] + P_yh[1] * (t_p - P_yh[4]) + P_yh[2] * (t_p - P_yh[4]) ** 2 + P_yh[3] * (t_p - P_yh[4]) ** 3
        z = P_zh[0] + P_zh[1] * (t_p - P_zh[4]) + P_zh[2] * (t_p - P_zh[4]) ** 2 + P_zh[3] * (t_p - P_zh[4]) ** 3
        return np.array([x, y, z])

    def construct_knots(self):
        t = []
        x = []
        y = []
        z = []
        x.append(self.start.get_pos_3d()[0])
        y.append(self.start.get_pos_3d()[1])
        z.append(self.start.get_pos_3d()[2])
        current_node = self.start.get_next_node()
        x.append(current_node.get_pos_3d()[0])
        y.append(current_node.get_pos_3d()[1])
        z.append(current_node.get_pos_3d()[2])
        while current_node.get_next_node() is not None and current_node is not self.start:
            x.append(current_node.get_next_node().get_pos_3d()[0])
            y.append(current_node.get_next_node().get_pos_3d()[1])
            z.append(current_node.get_next_node().get_pos_3d()[2])
            current_node = current_node.get_next_node()
        for i in range(len(x)):
            t.append(i / (len(x) - 1))
        return t, x, y, z

    @staticmethod
    def solve_splines(x, y):
        count = len(x)
        a = np.copy(y)
        b = np.zeros(count - 1)
        d = np.zeros(count - 1)
        h = np.zeros(count - 1)
        alpha = np.zeros(count - 1)
        for i in range(0, count - 1):
            h[i] = x[i + 1] - x[i]
        for i in range(1, count - 1):
            alpha[i] = (3 / h[i]) * (a[i + 1] - a[i]) - (3 / h[i - 1]) * (a[i] - a[i - 1])
        c = np.zeros(count)
        l = np.zeros(count)
        l[0] = 1
        mu = np.zeros(count)
        z = np.zeros(count)
        for i in range(1, count - 1):
            l[i] = 2 * (x[i + 1] - x[i - 1]) - h[i - 1] * mu[i - 1]
            mu[i] = h[i] / l[i]
            z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i]
        l[count - 1] = 1
        for j in range(count - 2, -1, -1):
            c[j] = z[j] - mu[j] * c[j + 1]
            b[j] = (a[j + 1] - a[j]) / h[j] - (h[j] * (c[j + 1] + 2 * c[j])) / 3
            d[j] = (c[j + 1] - c[j]) / (3 * h[j])
        return np.stack((a[0:count - 1], b[0:count - 1], c[0:count - 1], d[0:count - 1], x[0:count - 1]))

    def boundingRect(self):
        scene_positions = np.matmul(self.R,
                                    self.painting_points + np.repeat(self.translation, len(self.painting_points[0, :]),
                                                                     axis=1))
        return QRectF(QPointF(np.min(scene_positions[0, :]), np.min(scene_positions[2, :])),
                      QPointF(np.max(scene_positions[0, :]), np.max(scene_positions[2, :])))

    def paint(self, painter, option, widget=...):
        painter.scale(2, 2)
        pen_1 = QPen(Qt.GlobalColor.cyan)
        pen_1.setWidthF(0.1)
        pen_2 = QPen(Qt.GlobalColor.black)
        pen_2.setWidthF(0.1)
        pen_3 = QPen(Qt.GlobalColor.red)
        pen_3.setWidthF(0.1)
        pen_4 = QPen(Qt.GlobalColor.blue)
        pen_4.setWidthF(0.1)
        font = QFont()
        font.setPixelSize(1)
        start_point = np.matmul(self.R, self.painting_points[:, 0] + self.translation[:, 0])
        path = QPainterPath(QPointF(float(start_point[0]), float(start_point[2])))
        for i in range(1, len(self.painting_points[0, :])):
            next_point = np.matmul(self.R, self.painting_points[:, i] + self.translation[:, 0])
            path.lineTo(float(next_point[0]), float(next_point[2]))
        painter.setPen(pen_1)
        painter.drawPath(path)
        for helix, knot_lst in self.helix_knots.items():
            for i in range(len(knot_lst[0])):
                painter.setPen(pen_2)
                knot = np.array([knot_lst[0][i], knot_lst[1][i], knot_lst[2][i]])
                knot_point = np.matmul(self.R, knot + self.translation[:, 0])
                text_path = QPainterPath()
                text_path.addText(float(knot_point[0]), float(knot_point[2]), font,
                                  "{:d}".format(helix))
                painter.drawPath(text_path)
                painter.fillPath(text_path, QBrush(Qt.GlobalColor.black))
        for number, array_lst in self.helix_painting_points.items():
            for j in range(len(array_lst[0][0, :])):
                skip = False
                if array_lst[1][0, j] != 0:
                    next_point = np.matmul(self.R, array_lst[0][:, j] + self.translation[:, 0])
                    if j > 0:
                        if np.array_equal(array_lst[0][:, j], array_lst[0][:, j-1]):
                            skip = True
                    if array_lst[1][0, j] == -1 and not skip:
                        painter.setPen(pen_3)
                        painter.setBrush(QBrush(Qt.GlobalColor.red))
                    elif array_lst[1][0, j] == 1 and not skip:
                        painter.setPen(pen_4)
                        painter.setBrush(QBrush(Qt.GlobalColor.blue))
                    elif not skip:
                        painter.setPen(pen_2)
                        painter.setBrush(QBrush(Qt.GlobalColor.black))
                    painter.drawEllipse(QPointF(float(next_point[0]), float(next_point[2])), 0.1, 0.1)
