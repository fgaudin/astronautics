from datetime import timedelta
from unittest import TestCase
from kmath import Vector

from maneuver import injection_burn
from orbit import Body, Orbit


class InjectionManeuverTest(TestCase):
    def test_injection_maneuver(self):
        spacecraft = Body('Ship', 807.5)
        planet = Body('Kerbin', 5.291515641178033e+22)
        moon = Body('Mun', 9.759906267399235e+20)

        initial_position = Vector(429.6251323595451, -1014.5603320588696, 3.0461176250847237)
        initial_velocity = Vector(1.6487583925017983, 0.696902929205686, -0.01960474216076428)
        initial_orbit = Orbit(spacecraft, planet, initial_position, initial_velocity)

        moon_position = Vector(8362.608479599083, 8606.20586652083, 0.0)
        moon_velocity = Vector(-0.38906809228381334, 0.37805557735157685, 0.0)
        orbit_of_target = Orbit(moon, planet, moon_position, moon_velocity)

        max_duration = timedelta(hours=4)
        periapsis = 200000 + 20000
        maneuver = injection_burn(initial_orbit, orbit_of_target, max_duration, periapsis)

        expected_dv = 0.6520162499578012
        expected_duration = timedelta(hours=3, minutes=41, seconds=45, microseconds=368227)
        expected_time_to_maneuver = 3950.688208174463
        
        self.assertEqual(expected_dv, maneuver.dv)
        self.assertEqual(expected_duration, maneuver.duration)
        self.assertEqual(expected_time_to_maneuver, maneuver.time_to_maneuver)
