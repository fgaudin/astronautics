import math
from kmath import Vector
from utils import track


G = 6.674 * 10**-11  # Gravitational constant


class Body:
    def __init__(self, mass: float) -> None:
        self.mass = mass

    @property
    @track
    def gravitational_parameter(self):
        """
        μ (km3/s2)
        """
        return G * self.mass / (1000 ** 3)


class Orbit:
    def __init__(self, orbiter: Body, body: Body, orbiter_position: Vector, orbiter_velocity: Vector) -> None:
        self.orbiter = orbiter
        self.body = body
        self.position = orbiter_position  # (km)
        self.velocity = orbiter_velocity  # (km/s)

    def __str__(self) -> str:
        return f'{self.velocity.magnitude} - {self.position.magnitude}'

    @property
    def I(self):
        return Vector(1, 0, 0)
    
    @property
    def J(self):
        return Vector(0, 1, 0)

    @property
    def K(self):
        return Vector(0, 0 ,1)

    @property
    @track
    def potential_energy(self):
        """
        PE (kg km2/s2)
        """
        return - self.orbiter.mass * self.body.gravitational_parameter / self.position.magnitude

    @property
    @track
    def kinetic_energy(self):
        return 0.5 * self.orbiter.mass * self.velocity.magnitude ** 2

    @property
    @track
    def mechanical_energy(self):
        return self.potential_energy + self.kinetic_energy

    @property
    @track
    def specific_mechanical_energy(self):
        return self.mechanical_energy / self.orbiter.mass

    @property
    @track
    def major_axis(self):
        return - self.body.gravitational_parameter / self.specific_mechanical_energy

    @property
    @track
    def semi_major_axis(self):
        return self.major_axis / 2

    @property
    @track
    def eccentricity(self) -> Vector:
        return ((self.velocity.magnitude ** 2 - self.body.gravitational_parameter/self.position.magnitude) * self.position - (self.position.dot(self.velocity) * self.velocity)) / self.body.gravitational_parameter

    @property
    @track
    def specific_angular_momentum(self):
        return self.position.cross(self.velocity)

    @property
    @track
    def inclination(self):
        h = self.specific_angular_momentum
        angle = math.degrees(math.acos(self.K.dot(h)/(self.K.magnitude * h.magnitude)))
        return min(angle, 360 - angle)

    @property
    @track
    def ascending_node(self) -> Vector:
        return self.K.cross(self.specific_angular_momentum)

    @property
    @track
    def right_ascention(self):
        n = self.ascending_node
        angle = math.degrees(math.acos(self.I.dot(n) / (self.I.magnitude * n.magnitude)))
        
        if n.y >= 0:
            return min(angle, 360 - angle)
        else:
            return max(angle, 360 - angle)

    @property
    @track
    def argument_of_periapsis(self):
        n = self.ascending_node
        e = self.eccentricity
        angle = math.degrees(math.acos(n.dot(e)/ (n.magnitude * e.magnitude)))

        if e.z >= 0:
            return min(angle, 360 - angle)
        else:
            return max(angle, 360 - angle)

    @property
    @track
    def true_anomaly(self):
        e = self.eccentricity
        angle = math.degrees(math.acos(e.dot(self.position)/ (e.magnitude * self.position.magnitude)))

        if self.position.dot(self.velocity) >= 0:
            return min(angle, 360 - angle)
        else:
            return max(angle, 360 - angle)

    @property
    @track
    def period(self):
        return 2 * math.pi * math.sqrt(self.semi_major_axis ** 3 / self.body.gravitational_parameter)
