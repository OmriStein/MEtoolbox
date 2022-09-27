"""module containing the BoltPattern class used for bolt pattern strength analysis"""
from numpy import array, cross, dot, sqrt
from numpy.linalg import norm

# from me_toolbox.fatigue import EnduranceLimit, FatigueAnalysis
# from me_toolbox.fasteners import MetricBolt, UNBolt, ThreadedFastener
from me_toolbox.tools import print_atributes


class BoltPattern:
    def __init__(self, fasteners, fasteners_locations, force, force_location, tilting_edge):
        """Initialize threaded fastener with a nut"""

        self.bolts = [fastener.bolt for fastener in fasteners]
        self.preloads = [bolt.preload for bolt in self.bolts]
        self.fasteners_locations = fasteners_locations
        self.bolts_x_locations = [bolt[0] for bolt in self.fasteners_locations]
        self.bolts_y_locations = [bolt[1] for bolt in self.fasteners_locations]
        self.bolts_z_locations = [bolt[2] for bolt in self.fasteners_locations]
        self.bolts_stiffness = [fastener.bolt_stiffness for fastener in fasteners]
        self.substrates_stiffness = [fastener.substrate_stiffness for fastener in fasteners]
        self.fasteners_stiffness = [fastener.fastener_stiffness for fastener in fasteners]
        self.total_stiffness = [i + j for i, j in
                                zip(self.substrates_stiffness, self.bolts_stiffness)]
        self.force = force
        self.force_location = force_location
        self.bolt_shank_area = [bolt.nominal_area for bolt in self.bolts]
        self.bolt_stress_area = [bolt.stress_area for bolt in self.bolts]
        # TODO: use stress_area if the shear stress is in the threaded section or nominal_area if
        #  the shear stress is in the shank section and generalise for multiple layers
        self.tilting_edge = tilting_edge
        # TODO: Think about how to make the force parametric

    def get_info(self):
        """print all the fastener properties"""
        print_atributes(self)

    @property
    def shear_stress(self):
        return [norm(i) / j for i, j in zip(self.shear_force, self.bolt_shank_area)]

    @property
    def shear_force(self):
        """the total shear force on bolt from the external force and resulting torque"""
        return [i + j for i, j in zip(self.external_shear_force, self.torque_shear_force)]

    @property
    def external_shear_force(self):
        """shear forces directly from the external force (Fvi)"""
        force = array(self.force)

        # zeroing forces in the z direction (because they don't cause shear)
        force[2] = 0

        return [(force * area) / sum(self.bolt_shank_area) for area in self.bolt_shank_area]

    @property
    def torque_shear_force(self):
        """shear forces from the resulting torque (FGi)"""

        # calculating center of rotation (G)
        Gx, Gy, Gz = 0, 0, 0
        for area, location in zip(self.bolt_shank_area, self.bolts_x_locations):
            Gx += (area * location) / sum(self.bolt_shank_area)
        for area, location in zip(self.bolt_shank_area, self.bolts_y_locations):
            Gy += (area * location) / sum(self.bolt_shank_area)
        for area, location in zip(self.bolt_shank_area, self.bolts_z_locations):
            Gz += (area * location) / sum(self.bolt_shank_area)

        center_of_rotation = array([Gx, Gy, Gz])
        force_relative_to_G = array(self.force_location) - center_of_rotation
        torque_around_G = cross(force_relative_to_G, array(self.force))

        # zeroing torques not in the z direction (because they don't cause shear)
        torque_around_G[0] = 0
        torque_around_G[1] = 0

        rGi = [array(i) - center_of_rotation for i in self.fasteners_locations]

        force_times_area = [cross(torque_around_G, rGi[i]) * j for i, j in
                            enumerate(self.bolt_shank_area)]
        b = 0
        for i, j in enumerate(self.bolt_shank_area):
            b += j * norm(rGi[i]) ** 2

        return [a / b for a in force_times_area]

    @property
    def normal_stress(self):
        """normal stress in the bolt"""
        return self.bolt_tension / self.bolt_stress_area

    @property
    def bolt_tension(self):
        """tension force in the bolt (Fbj)"""
        return array(self.normal_force) * array(self.fasteners_stiffness) + array(self.preloads)

    @property
    def normal_force(self):
        """the total shear force on bolt from the external force and resulting moments (Pj)"""
        return [i[2] + j[2] for i, j in zip(self.external_normal_force, self.bending_normal_force)]

    @property
    def external_normal_force(self):
        """normal force directly from the external force"""
        normal_force = self.force[2]
        return [array([0, 0, (normal_force * stiffness) / sum(self.total_stiffness)]) for stiffness
                in self.total_stiffness]

    @property
    def bending_normal_force(self):
        """normal force resulting from the bending moment (PjTvV0M0)"""
        # location of the neutral center of tension
        Hx, Hy, Hz = 0, 0, 0
        for stiffness, location in zip(self.total_stiffness, self.bolts_x_locations):
            Hx += (stiffness * location) / sum(self.total_stiffness)
        for stiffness, location in zip(self.total_stiffness, self.bolts_y_locations):
            Hy += (stiffness * location) / sum(self.total_stiffness)
        # Todo: check what if the bolts are not at the same height, i.e if i can add Hz
        # for stiffness, location in zip(self.total_stiffness, self.bolts_z_locations):
        #     Hz += (stiffness * location) / sum(self.total_stiffness)

        # finding resulting moment relative to neutral center
        neutral_center = array([Hx, Hy, 0])
        force_relative_to_H = array(self.force_location) - neutral_center
        moment_around_H = cross(force_relative_to_H, array(self.force))
        # zeroing moment in the z direction (because it doesn't cause tension)
        moment_around_H[2] = 0

        # finding bolts distances from rotation edge
        edge = array(self.tilting_edge)
        edge_direction = edge / norm(edge)
        bolts_distance_from_edge = [edge + dot(r, edge_direction) * edge_direction for r in
                                    array(self.fasteners_locations)]
        force_times_stiffness = [cross(moment_around_H, bolts_distance_from_edge[i]) * j for i, j in
                                 enumerate(self.total_stiffness)]

        b = 0
        for i, j in enumerate(self.total_stiffness):
            b += j * norm(bolts_distance_from_edge[i]) ** 2
        return [a / b for a in force_times_stiffness]

    @property
    def equivalent_stresses(self):
        return [sqrt(normal_stress ** 2 + 3 * shear_stress ** 2) for normal_stress, shear_stress in
                zip(self.normal_stress, self.shear_stress)]

    def load_safety_factor(self, minimal=True):
        """Safety factor for loading (nL)"""
        proof_loads = array([bolt.proof_load for bolt in self.bolts])
        nL = (proof_loads - array(self.preloads)) / (
                    self.equivalent_stresses * array(self.bolt_stress_area) - array(self.preloads))
        return min(nL) if minimal else nL

    def separation_safety_factor(self, minimal=True):
        """Safety factor against fastener separation (n0)"""
        n0 = array(self.preloads) / ((1 - array(self.fasteners_stiffness)) * self.normal_force)
        return min(n0) if minimal else n0

    def proof_safety_factor(self, minimal=True):
        """Safety factor for proof strength (np)"""
        np = [bolt.proof_strength / eq for bolt, eq in zip(self.bolts, self.equivalent_stresses)]
        return min(np) if minimal else np
