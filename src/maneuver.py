from cmath import cos
from collections import namedtuple
from datetime import timedelta
import math
from multiprocessing.dummy import current_process
from kmath import Vector
from orbit import Orbit, period

from utils import tracked

Maneuver = namedtuple('Maneuver', 'dv duration')

@tracked
def injection_burn(body, initial_orbit: Orbit, target_orbit: Orbit, max_duration=None):
    """
    max_duration in seconds
    """
    # assume initial circular orbit
    assert initial_orbit.eccentricity <= 0.002

    r0 = initial_orbit.radius
    r1 = target_orbit.radius
    major_axis_transfer = r0 + r1
    epsilon0 = initial_orbit.velocity.magnitude ** 2 / 2 - body.gravitational_parameter / r0
    v0 = math.sqrt(2 * (body.gravitational_parameter / r0 + epsilon0))
    epsilon_transfer = - body.gravitational_parameter / (major_axis_transfer)
    v_transfer = math.sqrt(2 * (body.gravitational_parameter/r0 + epsilon_transfer))
    dv = abs(v_transfer - v0)

    # Hohmann transfer, low energy, longer time
    max_tof = period(major_axis_transfer/2, body.gravitational_parameter)/2

    tof = max_tof
    print(f"first dv: {dv}")
    print(f"max tof: {tof}")

    if max_duration:
        while tof > max_duration:
            dv = dv * 1.001
            v_transfer = dv + v0

            velocity_increase_ratio = v_transfer / v0
            v_transfer_vector = initial_orbit.velocity * velocity_increase_ratio
            transfer_orbit = Orbit(initial_orbit.orbiter, initial_orbit.body, initial_orbit.position, v_transfer_vector)

            e = transfer_orbit.eccentricity
            cos_nu0 = 1  #transfer_orbit.true_anomaly(cosine=True)
            cos_E0 = (e + cos_nu0)/(1 + e * cos_nu0)
            E0 = math.acos(cos_E0)
            cos_nu1 = transfer_orbit.true_anomaly_at(r1, cosine=True)
            cos_E1 = (e + cos_nu1)/(1 + e * cos_nu1)
            E1 = math.acos(cos_E1)

            a = transfer_orbit.semi_major_axis
            mu = transfer_orbit.body.gravitational_parameter
            tof = math.sqrt(a**3/mu) * ((E1 - e * math.sin(E1)) - (E0 - e * math.sin(E0)))
            print(dv)
            print(tof)

        nu0 = 0
        nu1 = math.acos(cos_nu1)
        angular_velocity_orbiter = 2 * math.pi / initial_orbit.period
        angular_velocity_target = 2 * math.pi / target_orbit.period
        phase_angle_at_departure = nu1 - nu0 - angular_velocity_target * tof
        u_o = math.radians(initial_orbit.true_longitude)
        u_t = math.radians(target_orbit.true_longitude)
        current_phase_angle = u_t - u_o
        angle_to_travel = current_phase_angle - phase_angle_at_departure
        if angle_to_travel < 0:
            angle_to_travel += 2 * math.pi

        time_to_maneuver = angle_to_travel / (angular_velocity_orbiter - angular_velocity_target)


    return dv, timedelta(seconds=tof), time_to_maneuver