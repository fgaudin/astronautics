from cmath import cos
from collections import namedtuple
from datetime import timedelta
import math
from multiprocessing.dummy import current_process
from kmath import PI, Angle, Vector
from orbit import Orbit, period

from utils import tracked

Maneuver = namedtuple('Maneuver', 'dv duration time_to_maneuver')


@tracked
def hohmann_transfer(initial_orbit: Orbit, target_orbit: Orbit):
    r0 = initial_orbit.radius
    r1 = target_orbit.radius
    major_axis_transfer = r0 + r1
    v0 = initial_orbit.velocity.magnitude
    epsilon_transfer = - initial_orbit.body.gravitational_parameter / (major_axis_transfer)
    v_transfer = math.sqrt(2 * (initial_orbit.body.gravitational_parameter/r0 + epsilon_transfer))
    dv1 = abs(v_transfer - v0)
    dv2 = None

    time_of_flight = period(major_axis_transfer/2, initial_orbit.body.gravitational_parameter)/2

    return dv1, dv2, time_of_flight


@tracked
def time_to_maneuver(initial_orbit: Orbit, target_orbit: Orbit, cos_nu1, time_of_flight):
    nu0 = 0
    nu1 = math.acos(cos_nu1)
    angular_velocity_orbiter = 2 * PI / initial_orbit.period
    angular_velocity_target = 2 * PI / target_orbit.period
    phase_angle_at_departure = Angle(nu1 - nu0 - angular_velocity_target * time_of_flight)
    u_o = initial_orbit.true_longitude
    u_t = target_orbit.true_longitude
    current_phase_angle = u_t - u_o
    if current_phase_angle < 0:
        current_phase_angle += 2 * PI
    angle_to_travel = current_phase_angle - phase_angle_at_departure
    if angle_to_travel < 0:
        angle_to_travel += 2 * PI

    return angle_to_travel / (angular_velocity_orbiter - angular_velocity_target)


@tracked
def eccentric_anomaly(eccentricity, cos_true_anomaly):
    return (eccentricity + cos_true_anomaly)/(1 + eccentricity * cos_true_anomaly)


@tracked
def injection_burn(initial_orbit: Orbit, target_orbit: Orbit, max_duration=None):
    """
    max_duration in seconds
    """
    # assume initial circular orbit
    assert initial_orbit.eccentricity <= 0.002

    # Hohmann transfer, low energy, longer time
    dv1, dv2, max_tof = hohmann_transfer(initial_orbit, target_orbit)
    dv = dv1

    tof = max_tof

    if max_duration:
        v0 = initial_orbit.velocity.magnitude
        r1 = target_orbit.radius

        while tof > max_duration:
            dv = dv * 1.001
            v_transfer = dv + v0

            velocity_increase_ratio = v_transfer / v0
            v_transfer_vector = initial_orbit.velocity * velocity_increase_ratio
            transfer_orbit = Orbit(initial_orbit.orbiter, initial_orbit.body, initial_orbit.position, v_transfer_vector)

            e = transfer_orbit.eccentricity
            cos_nu0 = 1  #transfer_orbit.true_anomaly(cosine=True)
            cos_E0 = eccentric_anomaly(e, cos_nu0)
            E0 = math.acos(cos_E0)
            cos_nu1 = transfer_orbit.true_anomaly_at(r1, cosine=True)
            cos_E1 = eccentric_anomaly(e, cos_nu1)
            E1 = math.acos(cos_E1)

            a = transfer_orbit.semi_major_axis
            mu = transfer_orbit.body.gravitational_parameter
            tof = math.sqrt(a**3/mu) * ((E1 - e * math.sin(E1)) - (E0 - e * math.sin(E0)))


    ttm = time_to_maneuver(initial_orbit, target_orbit, cos_nu1, tof)

    return Maneuver(dv, timedelta(seconds=tof), ttm)