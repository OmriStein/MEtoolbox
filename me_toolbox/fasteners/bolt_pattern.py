"""module containing the BoltPattern class used for bolt pattern strength analysis"""
from numpy import array, cross
from numpy.linalg import norm

# from me_toolbox.fatigue import EnduranceLimit, FatigueAnalysis
# from me_toolbox.fasteners import MetricBolt, UNBolt, ThreadedFastener
from me_toolbox.tools import print_atributes


class BoltPattern:
    def __init__(self, bolts, force, force_location):
        """Initialize threaded fastener with a nut"""

        self.bolts = bolts
        self.force = force
        self.force_location = force_location
        self.bolt_area = [bolt[0].nominal_area for bolt in self.bolts]
        # TODO: find-out how to decide if to use At or Ad
        # TODO: Think about how to make the force parametric

    def get_info(self):
        """print all the fastener properties"""
        print_atributes(self)

    @property
    def shear_stress(self):
        return [norm(i) / j for i, j in zip(self.shear_force, self.bolt_area)]

    @property
    def shear_force(self):
        return self.external_shear_force + self.torque_shear_force

    @property
    def external_shear_force(self):
        """shear forces directly from the external force"""
        force = array(self.force)
        Fvi = [(force * bolt[0].nominal_area) / sum(self.bolt_area) for bolt in self.bolts]
        return Fvi

    @property
    def torque_shear_force(self):
        """shear forces from the resulting torque"""

        # calculating center of rotation (G)

        bolts_x_locations = [bolt[1][0] for bolt in self.bolts]
        bolts_y_locations = [bolt[1][1] for bolt in self.bolts]
        bolts_z_locations = [bolt[1][2] for bolt in self.bolts]

        Gx, Gy, Gz = 0, 0, 0
        for area, location in zip(self.bolt_area, bolts_x_locations):
            Gx += (area * location) / sum(self.bolt_area)
        for area, location in zip(self.bolt_area, bolts_y_locations):
            Gy += (area * location) / sum(self.bolt_area)
        for area, location in zip(self.bolt_area, bolts_z_locations):
            Gz += (area * location) / sum(self.bolt_area)

        center_of_rotation = array([Gx, Gy, Gz])
        force_relative_to_G = array(self.force_location) - center_of_rotation
        torque_around_G = cross(force_relative_to_G, array(self.force))

        rGi = [array(j) - center_of_rotation for i, j in self.bolts]
        a = [cross(torque_around_G, rGi[i]) * j for i, j in enumerate(self.bolt_area)]
        b = 0
        for i, j in enumerate(self.bolt_area):
            b += j * norm(rGi[i]) ** 2
        FGi = a / b
        return FGi
