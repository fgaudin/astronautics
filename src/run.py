from datetime import timedelta
import math
from time import sleep
import krpc

from kmath import Vector
from maneuver import injection_burn
from orbit import Body, Orbit
from utils import track_list


if __name__ == '__main__':
    conn = krpc.connect(name='Hello World')
    vessel = conn.space_center.active_vessel
    bodies = conn.space_center.bodies
    ksp_kerbin = bodies['Kerbin']
    ksp_mun = bodies['Mun']
    ksp_minmus = bodies['Minmus']
    
    reference_frame = bodies['Kerbin'].non_rotating_reference_frame
    velocity_data = vessel.velocity(reference_frame)
    position_data = vessel.position(reference_frame)
    
    spacecraft = Body('Ship', vessel.mass)
    kerbin = Body('Kerbin', ksp_kerbin.mass)
    
    # Y axis is point to North pole so inverting Y and Z
    position = Vector(position_data[0], position_data[2], position_data[1]) / 1000  # converting to km
    velocity = Vector(velocity_data[0], velocity_data[2], velocity_data[1]) / 1000  # converting to km

    leo = Orbit(spacecraft, kerbin, position, velocity)

    mun = Body('Mun', ksp_mun.mass)
    mun_position_data = ksp_mun.position(reference_frame)
    mun_velocity_data = ksp_mun.velocity(reference_frame)
    mun_position = Vector(mun_position_data[0], mun_position_data[2], mun_position_data[1]) / 1000
    mun_velocity = Vector(mun_velocity_data[0], mun_velocity_data[2], mun_velocity_data[1]) / 1000
    mun_orbit = Orbit(mun, kerbin, mun_position, mun_velocity)

    minmus = Body('Minmus', ksp_minmus.mass)
    minmus_position_data = ksp_minmus.position(reference_frame)
    minmus_velocity_data = ksp_minmus.velocity(reference_frame)
    minmus_position = Vector(minmus_position_data[0], minmus_position_data[2], minmus_position_data[1]) / 1000
    minmus_velocity = Vector(minmus_velocity_data[0], minmus_velocity_data[2], minmus_velocity_data[1]) / 1000
    minmus_orbit = Orbit(minmus, kerbin, minmus_position, minmus_velocity)

    current_time = conn.space_center.ut

    print(f"max: {timedelta(seconds=20000)}")
    dv_transfer, duration, time_to_maneuver = injection_burn(kerbin, leo, mun_orbit, 20000)
    print(dv_transfer * 1000)
    print(duration)
    node = vessel.control.add_node(current_time + time_to_maneuver, dv_transfer * 1000)

    # track_list.save()