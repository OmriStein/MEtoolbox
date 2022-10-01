"""module containing the BoltPattern class used for bolt pattern strength analysis"""
from numpy import array, cross, dot, sqrt
from numpy.linalg import norm

# from me_toolbox.fatigue import EnduranceLimit, FatigueAnalysis
# from me_toolbox.fasteners import Bolt, ThreadedFastener
from me_toolbox.tools import print_atributes


class BoltPattern:
    def __init__(self, fasteners, fasteners_locations, force, preloads, force_location,
                 tilting_edge, shear_location):
        """Initialize threaded fastener with a nut"""
        self.fasteners = fasteners
        self.fasteners_locations = fasteners_locations
        self.force = force
        self.preloads = preloads
        self.force_location = force_location
        self.tilting_edge = tilting_edge
        self.shear_location = shear_location

    def get_info(self):
        """print all the fastener properties"""
        print_atributes(self)

    # @property
    # def bolts(self):
    #     """retrieving bolts objects from fasteners"""
    #     return [fastener.bolt for fastener in self.fasteners]

    @property
    def fasteners_stiffness(self):
        """bolts' fastener stiffness (C)"""
        return [fastener.fastener_stiffness for fastener in self.fasteners]

    @property
    def total_stiffness(self):
        """fasteners' total stiffness list (Kb+Km)"""
        return [fastener.member_stiffness + fastener.bolt_stiffness for fastener in self.fasteners]

    @property
    def bolt_shear_area(self):
        """if the shear stress is in the threaded section the shear area is the stress areas
           if the shear stress is in the shank section the shear area is the shank area"""
        if self.shear_location == 'shank':
            return [fastener.bolt.nominal_area for fastener in self.fasteners]
        elif self.shear_location == 'thread':
            return [fastener.bolt.stress_area for fastener in self.fasteners]
        else:
            raise ValueError("shear_location can be 'shank' or 'thread'")

    @property
    def shear_stress(self):
        """bolts' shear stress"""
        return [norm(i) / j for i, j in zip(self.total_shear_force, self.bolt_shear_area)]

    @property
    def total_shear_force(self):
        """the total shear force on bolt from the direct force and resulting torque (Fi)"""
        return [i + j for i, j in zip(self.direct_shear_force, self.torque_shear_force)]

    @property
    def direct_shear_force(self):
        """shear forces directly from the external force (Fvi)"""
        force = array(self.force)

        # zeroing forces in the z direction (because they don't cause shear)
        force[2] = 0

        return [(force * area) / sum(self.bolt_shear_area) for area in self.bolt_shear_area]

    @property
    def center_of_rotation(self):
        """center of rotation for an off center shear force"""
        bolts_x_locations = [bolt[0] for bolt in self.fasteners_locations]
        bolts_y_locations = [bolt[1] for bolt in self.fasteners_locations]
        bolts_z_locations = [bolt[2] for bolt in self.fasteners_locations]
        # calculating center of rotation (G)
        Gx, Gy, Gz = 0, 0, 0
        for area, location in zip(self.bolt_shear_area, bolts_x_locations):
            Gx += (area * location) / sum(self.bolt_shear_area)
        for area, location in zip(self.bolt_shear_area, bolts_y_locations):
            Gy += (area * location) / sum(self.bolt_shear_area)
        for area, location in zip(self.bolt_shear_area, bolts_z_locations):
            Gz += (area * location) / sum(self.bolt_shear_area)
        return Gx, Gy, Gz

    @property
    def torque_shear_force(self):
        """shear forces from the resulting torque (FGi)"""

        center_of_rotation = array(self.center_of_rotation)
        force_relative_to_G = array(self.force_location) - center_of_rotation
        torque_around_G = cross(force_relative_to_G, array(self.force))

        # zeroing torques not in the z direction (because they don't cause shear)
        torque_around_G[0] = 0
        torque_around_G[1] = 0

        rGi = [array(i) - center_of_rotation for i in self.fasteners_locations]

        force_times_area = [cross(torque_around_G, rGi[i]) * j for i, j in
                            enumerate(self.bolt_shear_area)]
        b = 0
        for i, j in enumerate(self.bolt_shear_area):
            b += j * norm(rGi[i]) ** 2

        return [a / b for a in force_times_area]

    @property
    def normal_stress(self):
        """normal stress in the bolt"""
        bolt_stress_area = [fastener.bolt.stress_area for fastener in self.fasteners]
        return self.bolt_load / bolt_stress_area

    @property
    def bolt_load(self):
        """tension force in the bolt (Fbj)"""
        return array(self.preloads) + (array(self.fastener_load) * array(self.fasteners_stiffness))

    @property
    def fastener_load(self):
        """the total normal force on bolt from the direct force and resulting bending moment (Pj)"""
        return [abs(i[2] + j[2]) for i, j in zip(self.direct_normal_load, self.bending_normal_load)]

    @property
    def direct_normal_load(self):
        """normal force directly from pure tension (PTj)"""
        normal_force = self.force[2]
        return [array([0, 0, (normal_force * stiffness) / sum(self.total_stiffness)]) for stiffness
                in self.total_stiffness]

    @property
    def neutral_point(self):
        """The location of the neutral point of tension"""
        bolts_x_locations = [bolt[0] for bolt in self.fasteners_locations]
        bolts_y_locations = [bolt[1] for bolt in self.fasteners_locations]
        bolts_z_locations = [bolt[2] for bolt in self.fasteners_locations]

        # location of the neutral point of tension
        Hx, Hy, Hz = 0, 0, 0
        for stiffness, location in zip(self.total_stiffness, bolts_x_locations):
            Hx += (stiffness * location) / sum(self.total_stiffness)
        for stiffness, location in zip(self.total_stiffness, bolts_y_locations):
            Hy += (stiffness * location) / sum(self.total_stiffness)
        for stiffness, location in zip(self.total_stiffness, bolts_z_locations):
            Hz += (stiffness * location) / sum(self.total_stiffness)
        return Hx, Hy, Hz

    @property
    def bending_normal_load(self):
        """normal force resulting from the bending moment (PMTVj)"""
        Hx, Hy, Hz = self.neutral_point

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
        """equivalent stresses according to Von-mises"""
        return [sqrt(normal_stress ** 2 + 3 * shear_stress ** 2) for normal_stress, shear_stress in
                zip(self.normal_stress, self.shear_stress)]

    def load_safety_factor(self, minimal=True):
        """Safety factor for loading (nL)"""
        proof_loads = array([fastener.bolt.proof_load for fastener in self.fasteners])
        nL = (proof_loads - array(self.preloads)) / (self.bolt_load - array(self.preloads))
        return min(nL) if minimal else nL

    def separation_safety_factor(self, minimal=True):
        """Safety factor against fastener separation (n0)"""
        n0 = array(self.preloads) / ((1 - array(self.fasteners_stiffness)) * self.fastener_load)
        return min(n0) if minimal else n0

    def proof_safety_factor(self, minimal=True):
        """Safety factor for proof strength (np)"""
        np = [fastener.bolt.proof_strength / eq for fastener, eq in
              zip(self.fasteners, self.equivalent_stresses)]
        return min(np) if minimal else np
