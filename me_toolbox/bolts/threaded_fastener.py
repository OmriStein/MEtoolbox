"""module containing the ThreadedFastener class used for strength analysis"""
from me_toolbox.bolts import Bolt


class ThreadedFastener:
    def __init__(self, bolt, grip_length):
        """Initialize threaded fastener with a nut
        :param Bolt bolt: A bolt object
        :param float grip_length: Length of all material squeezed
            between face of bolt and face of nut
        """
        self.bolt = bolt
        self.grip_length = grip_length

    @classmethod
    def threaded_plate(cls, bolt, plate_thickness, h):
        """Create threaded fastener with threaded plate
        :param Bolt bolt: Bolt object
        :param float plate_thickness: threaded section length
        :param float h: thickness of all materials squeezed between
            the face of the bolt and the face of the threaded plate
        """
        t2 = plate_thickness
        grip_length = h + 0.5 * t2 if t2 < bolt.diameter else h + 0.5 * bolt.diameter
        return ThreadedFastener(bolt, grip_length)

    @property
    def grip_threads(self):
        """threaded section in grip"""
        return self.grip_length - self.bolt.unthreaded_length

    @property
    def fastener_stiffness(self):
        """fastener stiffness (Kb)"""
        bolt = self.bolt
        Ad = bolt.nominal_area
        At = bolt.stress_area
        E = bolt.elastic_modulus
        lt = self.grip_length
        ld = bolt.unthreaded_length
        return (Ad*At*E)/((Ad*lt)+(At*ld))
