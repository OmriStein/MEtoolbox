"""module containing the bolts base class Bolt"""
from math import sqrt, pi

from me_toolbox.tools import print_atributes
from me_toolbox.fatigue import EnduranceLimit


class Bolt:
    """Bolt class containing basic geometry attributes
    that are identical in metric and unified national(NU) standard"""
    angle = 60

    def __repr__(self):
        return f"Bolt({self.diameter}, {self.pitch}, {self.length})"

    def __init__(self, diameter, pitch, length, grade, elastic_modulus, endurance_limit,
                 reliability, temp, surface_finish, preload, reused):
        """Initialise Bolt object

        :param float diameter: nominal diameter
        :param float pitch: Thread's pitch
        :param float length: bolt's length
        :param float elastic_modulus: Bolt's elastic modulus
        :param float endurance_limit: Bolt's endurance limit
        :param float reliability: Bolt's reliability (for Se calc)
        :param float temp: Working temp (for Se calc)
        :param str surface_finish: 'machined' or 'hot-rolled' (for Se calc)
        :param float preload: Preload of the bolt
        :param bool reused: is the bolt ment to be reused or permanent
        """
        self.diameter = diameter
        self.pitch = pitch
        self.length = length
        self.grade = grade
        self.elastic_modulus = elastic_modulus
        self.reliability = reliability
        self.temp = temp
        self.surface_finish = surface_finish
        self.endurance_limit = endurance_limit
        self.reused = reused
        self.preload = preload

    def get_info(self):
        """print all the bolt's properties"""
        print_atributes(self)

    @property
    def height(self):
        """Height of fundamental triangle (H)"""
        return self.pitch * sqrt(3) / 2

    @property
    def mean_diam(self):
        "Mean diameter(dm) of the nominal and root diameters(dr)"""
        return self.diameter - (5 / 8) * self.height

    @property
    def root_diam(self):
        """Minor diameter (dr)"""
        return self.diameter - (5 / 4) * self.height

    @property
    def pitch_diam(self):
        """Pitch diameter(dp)"""
        return self.diameter - (3 / 8) * self.height

    @property
    def head_diam(self):
        """Contact area diameter of bolt head (D)"""
        return 1.5 * self.diameter

    @property
    def shank_length(self):
        """the unthreaded section of the bolt (ld)
        Note: the unthreaded length can be zero"""
        return self.length - self.thread_length

    @property
    def nominal_area(self):
        """area of the bolt's nominal diameter (Ad)"""
        return 0.25 * pi * self.diameter ** 2

    @property
    def proof_load(self):
        """The proof load (Fp) the bolt can withstand"""
        try:
            return self.proof_strength * self.stress_area
        except AttributeError as err:
            raise NotImplementedError("proof load is only implemented in child class") from err

    @property
    def preload(self):
        return self._preload

    @preload.setter
    def preload(self, preload):
        if preload is not None:
            try:
                # Estimated Pre-Load(Fi) for both static and fatigue loading
                if self.reused is True:
                    self._preload = 0.75 * self.proof_load  # for reused fasteners
                else:
                    self._preload = 0.90 * self.proof_load  # for permanent connections
            except NotImplementedError:
                raise NotImplementedError("preload *estimation* is only implemented in child class")
        else:
            self._preload = preload

    @property
    def endurance_limit(self):
        return self._endurance_limit

    @endurance_limit.setter
    def endurance_limit(self, Se):
        if Se is None:
            self._endurance_limit = self.calc_endurance_limit()
        else:
            self._endurance_limit = Se

    def calc_endurance_limit(self):
        """Calculate endurance limit"""

        try:
            Se = EnduranceLimit(Sut=self.tensile_strength, surface_finish=self.surface_finish,
                                rotating=False, max_normal_stress=1, max_bending_stress=0,
                                stress_type='multiple', temp=self.temp,
                                reliability=self.reliability, material='steel',
                                diameter=self.stress_area)
        except NotImplementedError:
            raise NotImplementedError("calc_endurance_limit is only implemented in child class")

        se_vals = {'5': (18.6, 16.3), '7': 20.6, '8': 23.2, '8.8': 129, '9.8': 140, '10.9': 162,
                   '12.9': 190}

        grade = self.grade

        if grade in se_vals:
            if grade == '5':
                if 0.25 < self.diameter < 1:
                    return se_vals['5'][0] * Se.Kd * Se.Ke
                else:
                    return se_vals['5'][1] * Se.Kd * Se.Ke
            else:
                return se_vals[grade] * Se.Kd * Se.Ke
        else:
            return Se.modified
