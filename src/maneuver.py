import math
from orbit import Orbit, period

from utils import tracked

@tracked
def injection_burn(body, initial_orbit: Orbit, target_orbit: Orbit):
    r1 = initial_orbit.radius
    r2 = target_orbit.radius
    major_axis_transfer = r1 + r2
    epsilon1 = initial_orbit.velocity.magnitude ** 2 / 2 - body.gravitational_parameter / r1
    v1 = math.sqrt(2 * (body.gravitational_parameter / r1 + epsilon1))
    epsilon_transfer = - body.gravitational_parameter / (major_axis_transfer)
    v_transfer = math.sqrt(2 * (body.gravitational_parameter/r1 + epsilon_transfer))
    dv = abs(v_transfer - v1)

    tof = period(major_axis_transfer/2, body.gravitational_parameter)/2
    return dv