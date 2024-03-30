"""module containing the bolts base class Bolt"""
from collections import namedtuple
from math import sqrt, pi
from mpmath import sec

from me_toolbox.tools import print_atributes
from me_toolbox.fatigue import EnduranceLimit


class Bolt:
    """Bolt class containing basic geometry attributes"""
    angle = 60

    def __repr__(self):
        return f"Bolt(diameter={self.diameter}, pitch={self.pitch}, length={self.length}, " \
               f"thread_length={self.thread_length}, yield_strength={self.yield_strength}, " \
               f"tensile_strength={self.tensile_strength}, proof_strength={self.proof_strength}, " \
               f"elastic_modulus={self.elastic_modulus}, Kf={self.Kf})"

    def __str__(self):
        return f"Bolt({self.diameter}x{self.pitch}x{self.length})"

    def __init__(self, diameter, pitch, length, thread_length,
                 yield_strength, tensile_strength, proof_strength, elastic_modulus, Kf=None):
        """Initialise Bolt object
        :param float diameter: Nominal diameter
        :param float pitch: Thread's pitch
        :param float length: Bolt's length
        :param float thread_length: Bolt's length
        :param float yield_strength: Bolt's yield strength
        :param float tensile_strength: Bolt's tensile strength
        :param float proof_strength: Bolt's proof strength (if unknown use 85% of yield strength)
        :param float elastic_modulus: Bolt's elastic modulus
        :param float Kf: Dynamic stress concentration factor
        """
        self.diameter = diameter
        self.pitch = pitch
        self.length = length
        self.thread_length = thread_length

        self.yield_strength = yield_strength
        self.tensile_strength = tensile_strength
        self.proof_strength = proof_strength
        self.elastic_modulus = elastic_modulus
        self.Kf = Kf

    def get_info(self):
        """print all the bolt's properties"""
        print_atributes(self)

    @property
    def height(self):
        """Height of fundamental triangle (H)"""
        return self.pitch * sqrt(3) / 2

    @property
    def minor_diameter(self):
        """Minor diameter (dr) as calculated in Table 8-1 of Shigley"""
        return self.diameter - 1.226869 * self.pitch

    @property
    def mean_diameter(self):
        """Mean diameter(dm) of the nominal and root diameters(dr)"""
        # return self.diameter - (5 / 8) * self.height
        return 0.5 * (self.diameter + self.minor_diameter)

    @property
    def pitch_diameter(self):
        """Pitch diameter(dp) as calculated in Table 8-1 of Shigley"""
        return self.diameter - 0.649519 * self.pitch

    @property
    def head_diameter(self):
        """Estimated diameter of bolt head (D)"""
        return 1.5 * self.diameter

    @property
    def shank_length(self):
        """The unthreaded section of the bolt (ld)"""
        return self.length - self.thread_length

    @property
    def nominal_area(self):
        """Area of the bolt's nominal diameter (Ad)"""
        return 0.25 * pi * self.diameter ** 2

    @property
    def minor_area(self):
        """Area of the bolt's root or minor diameter (Ar)"""
        return 0.25 * pi * self.minor_diameter ** 2

    @property
    def proof_load(self):
        """Proof load of the bolt (Fp)"""
        return self.proof_strength * self.stress_area

    @property
    def stress_area(self):
        """Tensile stress area (At)"""
        dt = 0.5 * (self.minor_diameter + self.pitch_diameter)
        return 0.25 * pi * dt ** 2

    def estimate_preload(self, reused):
        """Estimated Pre-Load(Fi) for both static and fatigue loading
                :param bool reused: True for reused fastener or False for a permanent joint
                """
        return 0.75 * self.proof_load if reused else 0.90 * self.proof_load

    def preload2torque(self, preload, thread_friction, collar_friction):
        """calculating tightening torque from preload"""
        Fi, d, dm = preload, self.diameter, self.mean_diameter
        length = self.pitch  # for single start
        tanG = length / (pi * dm)
        alpha = self.angle
        return Fi * d * ((dm / (2 * d)) *
                         ((tanG + thread_friction * sec(alpha)) /
                          (1 - thread_friction * tanG * sec(alpha))) + 0.625*collar_friction)

    def torque2preload(self, torque):
        pass

    def endurance_limit(self, unmodified_Se, surface_finish, temp, reliability):
        """Calls the EnduranceLimit class with the right parameters for a bolt
        :param float unmodified_Se: Unmodified endurance strength
        :param string surface_finish: the bolt's surface finish
            options:['ground', 'machined', 'cold-drawn', 'hot-rolled', 'as forged']
        :param float temp: The bolt's operating temperature in deg C
        :param float reliability: bolt's reliability

        :returns: An endurance limit object
        :rtype: EnduranceLimit
        """
        finishes = ['ground', 'machined', 'cold-drawn', 'hot-rolled', 'as forged']

        if surface_finish not in finishes:
            raise Exception(f"The surface finish({surface_finish}) is not one of the acceptable"
                            f"surface finishes[{finishes}]")

        Se = EnduranceLimit(unmodified_Se, Sut=self.tensile_strength, surface_finish=surface_finish,
                            rotating=False, max_normal_stress=1, max_bending_stress=0,
                            stress_type='multiple', temp=temp,
                            reliability=reliability,
                            diameter=sqrt((4*self.stress_area)/pi))
        return Se

    @staticmethod
    def get_strength_prop(diameter, grade):
        """Returns the proof strength, tensile strength and yield strength
            of the bolt in accordance with its grade
            :param float diameter: Bolt's diameter
            :param string grade: Bolt's grade or class
            options: ['4.6', '4.8', '5.8', '8.8', '9.8', '10.9', '12.9']

            :returns: Proof-Strength, Ultimate-tensile-strength, Yield-strength
            :rtype: list
            """
        grade_prop = namedtuple('Grade', ['low', 'high', 'Sp', 'Sut', 'Sy'])
        grade_list = {'4.6': grade_prop(5, 36, 225, 400, 240),
                      '4.8': grade_prop(1.6, 16, 310, 420, 340),
                      '5.8': grade_prop(5, 24, 380, 520, 420),
                      '8.8': grade_prop(16, 36, 600, 830, 660),
                      '9.8': grade_prop(1.6, 16, 650, 900, 720),
                      '10.9': grade_prop(5, 36, 830, 1040, 940),
                      '12.9': grade_prop(1.6, 36, 970, 1220, 1100)}
        if not isinstance(grade, str):
            raise KeyError(f"The grade should be a string")
        if diameter < grade_list[grade].low or diameter > grade_list[grade].high:
            raise Exception(f"Diameter({diameter}) not in range([{grade_list[grade].low},"
                            f"{grade_list[grade].high}]) for this grade({grade})")
        else:
            return [grade_list[grade].Sy, grade_list[grade].Sut, grade_list[grade].Sp]
