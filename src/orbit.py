import math
from kmath import PI, Angle, Vector
from utils import tracked, tracked_property


G = 6.674 * 10**-11  # Gravitational constant


class Body:
    def __init__(self, name, mass: float) -> None:
        self.name = name
        self._mass = mass

    @tracked_property
    def mass(self):
        return self._mass

    @tracked_property
    def gravitational_parameter(self):
        """
        μ (km3/s2)
        """
        return G * self.mass / (1000 ** 3)


@tracked
def period(semi_major_axis, gravitational_parameter):
    return 2 * math.pi * math.sqrt(semi_major_axis ** 3 / gravitational_parameter)


class Orbit:
    def __init__(self, orbiter: Body, body: Body, orbiter_position: Vector, orbiter_velocity: Vector) -> None:
        self.orbiter = orbiter
        self.body = body
        self._position = orbiter_position  # (km)
        self._velocity = orbiter_velocity  # (km/s)

    def __str__(self) -> str:
        true_anomaly = self.true_anomaly
        if true_anomaly and true_anomaly > 180:
            true_anomaly -= 360

        coe = {
            'a': self.semi_major_axis,
            'e': self.eccentricity,
            'i': self.inclination,
            'Ω': self.right_ascention,
            'ω': self.argument_of_periapsis,
            'ν': true_anomaly
        }
        return "\n".join([f'{k}: {v}' for k, v in coe.items()])

    @tracked_property
    def position(self) -> Vector:
        """
        r
        """
        return self._position

    @tracked_property
    def radius(self) -> float:
        return self.position.magnitude

    @tracked_property
    def velocity(self) -> Vector:
        """
        v
        """
        return self._velocity

    @property
    def I(self):
        """
        Unit vector through vernal equinox
        """
        return Vector(1, 0, 0)
    
    @property
    def J(self):
        """
        Unit vector
        """
        return Vector(0, 1, 0)

    @property
    def K(self):
        """
        Unit vector through north pole
        """
        return Vector(0, 0 ,1)

    @tracked_property
    def potential_energy(self):
        """
        PE (kg km2/s2)
        """
        return - self.orbiter.mass * self.body.gravitational_parameter / self.radius

    @tracked_property
    def kinetic_energy(self):
        return (self.orbiter.mass * self.velocity.magnitude ** 2) / 2

    @tracked_property
    def mechanical_energy(self):
        return self.potential_energy + self.kinetic_energy

    @tracked_property
    def specific_mechanical_energy(self):
        return self.mechanical_energy / self.orbiter.mass

    @tracked_property
    def major_axis(self):
        return - self.body.gravitational_parameter / self.specific_mechanical_energy

    @tracked_property
    def semi_major_axis(self):
        """
        a
        """
        return self.major_axis / 2

    @tracked_property
    def eccentricity_vector(self) -> Vector:
        return ((self.velocity.magnitude ** 2 - self.body.gravitational_parameter/self.radius) * self.position - (self.position.dot(self.velocity) * self.velocity)) / self.body.gravitational_parameter

    @tracked_property
    def eccentricity(self) -> float:
        """
        e
        """
        return self.eccentricity_vector.magnitude

    @tracked_property
    def parameter(self):
        """
        p

        also called semi latus rectum
        witdh of curve at focus
        """
        return self.specific_angular_momentum.magnitude ** 2 / self.body.gravitational_parameter

    def radius_at_true_anomaly(self, true_anomaly: Angle):
        return self.parameter / (1 + self.eccentricity * math.cos(true_anomaly.rad))


    @tracked_property
    def radius_at_periapsis(self):
        return self.semi_major_axis * (1 - self.eccentricity)

    @tracked_property
    def radius_at_apoapsis(self):
        return self.semi_major_axis * (1 + self.eccentricity)

    @tracked_property
    def specific_angular_momentum(self) -> Vector:
        """
        h
        """
        return self.position.cross(self.velocity)

    @tracked_property
    def node_vector(self):
        return self.K.cross(self.specific_angular_momentum)

    @tracked_property
    def flight_path_angle(self) -> Angle:
        """
        φ (phi)
        """
        h = self.specific_angular_momentum.magnitude
        rv = self.radius * self.velocity.magnitude
        sign = 1 if self.position.dot(self.velocity) >= 0 else -1
        phi = math.acos(h/rv) * sign
        return Angle(phi)

    @tracked_property
    def inclination(self) -> Angle:
        """
        i
        """
        h = self.specific_angular_momentum
        angle = Angle(math.acos(round(self.K.dot(h)/(self.K.magnitude * h.magnitude), 9)))
        return min(angle, 2 * PI - angle)

    @tracked_property
    def ascending_node(self) -> Vector:
        return self.K.cross(self.specific_angular_momentum)

    @tracked_property
    def right_ascention(self):
        n = self.ascending_node
        if n.magnitude == 0:
            return None
        angle = Angle(math.acos(self.I.dot(n) / (self.I.magnitude * n.magnitude)))
        
        if n.y >= 0:
            return min(angle, 2 * PI - angle)
        else:
            return max(angle, 2 * PI - angle)

    @tracked_property
    def argument_of_periapsis(self) -> Angle:
        n = self.ascending_node
        e = self.eccentricity_vector

        if n.magnitude == 0 or e.magnitude == 0:
            return None

        angle = Angle(math.acos(n.dot(e)/ (n.magnitude * e.magnitude)))

        if e.z >= 0:
            return min(angle, 2 * PI - angle)
        else:
            return max(angle, 2 * PI - angle)

    @tracked
    def true_anomaly(self, cosine=False) -> Angle:
        """
        Angle of the spacecraft with the periapsis
        """
        e = self.eccentricity_vector
        if round(e.magnitude, 4) == 0:
            return None
        val_cos = e.dot(self.position)/ (e.magnitude * self.radius)
        if cosine:
            return val_cos
        angle = Angle(math.acos(round(val_cos, 9)))

        if self.position.dot(self.velocity) >= 0:
            return min(angle, 2 * PI - angle)
        else:
            return max(angle, 2 * PI - angle)

    @tracked
    def true_anomaly_at(self, radius, cosine=False) -> Angle:
        cos_nu = (self.parameter - radius) / (self.eccentricity * radius)
        if cosine:
            return cos_nu
        true_anomaly = math.acos(round(cos_nu, 9))
        return Angle(true_anomaly)

    @property
    def period(self):
        return period(self.semi_major_axis, self.body.gravitational_parameter)

    @tracked
    def circular_velocity(self, radius):
        """
        velocity in circular orbit
        """
        return math.sqrt(self.body.gravitational_parameter / radius)

    @tracked
    def escape_velocity(self, radius):
        return math.sqrt(2 * self.body.gravitational_parameter / radius)


    @tracked_property
    def sphere_of_influence(self):
        return self.semi_major_axis * (self.orbiter.mass / self.body.mass) ** (2/5)

    @tracked_property
    def mean_motion(self):
        """
        n (rad/s)
        """
        return math.sqrt(self.body.gravitational_parameter/self.semi_major_axis**3)

    @tracked_property
    def true_longitude(self) -> Angle:
        cos_theta = self.I.dot(self.position) / (self.I.magnitude * self.position.magnitude)
        acos_theta = math.acos(cos_theta)
        if self.J.dot(self.position) < 0:
            acos_theta = 2 * math.pi - acos_theta
        return Angle(acos_theta)



@tracked
def hohmann_transfer(orbit1: Orbit, orbit2: Orbit):
    pass