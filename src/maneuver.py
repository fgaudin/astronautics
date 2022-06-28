from cmath import cos
from collections import namedtuple
from datetime import timedelta
from math import asin, cos, acos, sin, sqrt, pi
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
    v_transfer = sqrt(2 * (initial_orbit.body.gravitational_parameter/r0 + epsilon_transfer))
    dv1 = abs(v_transfer - v0)
    dv2 = None

    time_of_flight = period(major_axis_transfer/2, initial_orbit.body.gravitational_parameter)/2

    return dv1, dv2, time_of_flight


@tracked
def time_to_maneuver(initial_orbit: Orbit, target_orbit: Orbit, cos_nu1, phase_angle_at_arrival, time_of_flight):
    nu0 = 0
    nu1 = acos(cos_nu1)
    angular_velocity_orbiter = 2 * PI / initial_orbit.period
    angular_velocity_target = 2 * PI / target_orbit.period
    # γ0
    phase_angle_at_departure = Angle(nu1 - nu0 - phase_angle_at_arrival - angular_velocity_target * time_of_flight)
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


def compute(orbit_of_target: Orbit, target_sphere_of_influence, lambda1, r0, v0, phi0):
        mu = orbit_of_target.body.gravitational_parameter
        
        E = v0 ** 2 / 2 - mu / r0
        h0 = r0 * v0 * cos(phi0)

        p = h0 ** 2 / mu
        a0 = -mu / (2 * E)
        e0 = sqrt(1 - p/a0)
        Rs = target_sphere_of_influence
        

        r1 = sqrt(orbit_of_target.radius ** 2 + Rs ** 2  - 2 * orbit_of_target.radius * Rs * cos(lambda1))
        v1 = sqrt(2 * (E + mu/r1))
        phi1 = acos(h0 / (r1 * v1))

        cos_nu0 = (p - r0) / (r0 * e0)
        nu0 = acos(round(cos_nu0, 9))
        cos_nu1 = (p - r1) / (r1 * e0)
        nu1 = acos(cos_nu1)
        cos_E0 = (e0 + cos_nu0) / (1 + e0 * cos_nu0)
        E0 = acos(cos_E0)
        cos_E1 = (e0 + cos_nu1) / (1 + e0 * cos_nu1)
        E1 = acos(cos_E1)

        gamma1 = asin(sin(lambda1) * Rs / r1)

        vt = orbit_of_target.velocity.magnitude
        
        v2 = sqrt(v1 ** 2 + vt ** 2 - 2 * v1 * vt * cos(phi1 - gamma1))
        epsilon2 = Angle(asin((vt * cos(lambda1) - v1 * cos(lambda1 + gamma1 - phi1)) / v2))
        # print(epsilon2.deg)

        mu_t = orbit_of_target.orbiter.gravitational_parameter
        r2 = Rs
        E = v2 ** 2 /2 - mu_t / r2
        h = r2 * v2 * sin(epsilon2)
        p = h ** 2 / mu_t
        e = sqrt(1 + 2 * E * h ** 2 / mu_t ** 2)
        #print(e)
        rp = p / (1 + e)
        #print(rp)

        return rp, a0, e0, E0, E1, nu0, nu1, gamma1


@tracked
def injection_burn(initial_orbit: Orbit, target_orbit: Orbit, max_duration: timedelta = None, periapsis=None):
    """
    max_duration in seconds
    periapsis in m from center of body
    """
    # assume initial circular orbit
    assert initial_orbit.eccentricity <= 0.002

    Rs = target_orbit.sphere_of_influence
    # angle between Target/reference body line and point when crossing sphere of influence
    lambda1 = Angle(deg=60).rad   # initial random value

    # Hohmann transfer, low energy, longer time
    dv1, dv2, max_tof = hohmann_transfer(initial_orbit, target_orbit)
    dv = dv1

    dv = dv * 1.03

    tof = max_tof

    # if max_duration:
    #     v0 = initial_orbit.velocity.magnitude

    #     while tof > max_duration.total_seconds():
    #         dv = dv * 1.001
    #         v_transfer = dv + v0

    #         velocity_increase_ratio = v_transfer / v0
    #         v_transfer_vector = initial_orbit.velocity * velocity_increase_ratio
    #         transfer_orbit = Orbit(initial_orbit.orbiter, initial_orbit.body, initial_orbit.position, v_transfer_vector)

    #         e = transfer_orbit.eccentricity
    #         cos_nu0 = 1  #transfer_orbit.true_anomaly(cosine=True)
    #         cos_E0 = eccentric_anomaly(e, cos_nu0)
    #         E0 = acos(cos_E0)
    #         cos_nu1 = transfer_orbit.true_anomaly_at(r1, cosine=True)
    #         cos_E1 = eccentric_anomaly(e, cos_nu1)
    #         E1 = acos(cos_E1)

    #         a = transfer_orbit.semi_major_axis
    #         mu = transfer_orbit.body.gravitational_parameter

    #         tof = sqrt(a**3/mu) * ((E1 - e * sin(E1)) - (E0 - e * sin(E0)))
    

    v0 = initial_orbit.velocity.magnitude + dv
    r0 = initial_orbit.position.magnitude
    mu = initial_orbit.body.gravitational_parameter
    phi0 = Angle(0)
    
    rp = Rs

    if periapsis:
        periapsis_km = periapsis / 1000
        result = None
        previous_result = None
        while rp >= periapsis_km:
            previous_result = result
            lambda1 -= Angle(deg=0.1).rad
            result = compute(target_orbit, Rs, lambda1, r0, v0, phi0)
            rp, a0, e0, E0, E1, nu0, nu1, gamma1 = result

        rp, a0, e0, E0, E1, nu0, nu1, gamm1 = previous_result

            
        angular_velocity_target = 2 * PI / target_orbit.period
        tof = sqrt(a0 ** 3 / mu) * ((E1 - e0 * sin(E1)) - (E0 - e0 * sin(E0)))
        # phase angle at departure
        gamma0 = nu1 - nu0 - gamma1 - angular_velocity_target * tof
        print(Angle(gamma0))
        print(dv)


    ttm = time_to_maneuver(initial_orbit, target_orbit, cos(nu1), gamma1, tof)

    return Maneuver(dv, timedelta(seconds=tof), ttm)