import krpc

from kmath import Vector
from orbit import Body, Orbit
from utils import track, track_list


if __name__ == '__main__':
    conn = krpc.connect(name='Hello World')
    vessel = conn.space_center.active_vessel
    bodies = conn.space_center.bodies
    kerbin = bodies['Kerbin']
    body = Body(kerbin.mass)
    reference_frame = bodies['Kerbin'].non_rotating_reference_frame
    velocity_data = vessel.velocity(reference_frame)
    position_data = vessel.position(reference_frame)
    radius = (bodies['Kerbin'].equatorial_radius + vessel.flight().mean_altitude) / 1000
    spacecraft = Body(vessel.mass)
    # Y axis is point to North pole so inverting Y and Z
    position = Vector(position_data[0], position_data[2], position_data[1]) / 1000  # converting to km
    velocity = Vector(velocity_data[0], velocity_data[2], velocity_data[1]) / 1000  # converting to km
    leo = Orbit(spacecraft, body, position, velocity)

    print(leo)
    print(position.magnitude)
    print(velocity.magnitude)
    print(leo.eccentricity.magnitude)
    print(leo.inclination)
    print(leo.right_ascention)
    print(leo.argument_of_periapsis)
    print(leo.true_anomaly)

    # track_list.save()