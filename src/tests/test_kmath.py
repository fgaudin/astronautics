from math import pi
from unittest import TestCase

from kmath import Angle, Vector


class AngleTest(TestCase):
    def test_new_angle(self):
        angle = Angle(pi/2)
        self.assertEqual('rad: 1.5707963267948966 - deg: 90.0', str(angle))

    def test_degree(self):
        self.assertEqual(0, Angle(0).deg)
        self.assertEqual(90, Angle(pi/2).deg)
        self.assertEqual(180, Angle(pi).deg)
        self.assertEqual(270, Angle(3 * pi/2).deg)
        self.assertEqual(360, Angle(2 * pi).deg)
        self.assertEqual(450, Angle(5 * pi/2).deg)

    def test_add_angles(self):
        self.assertEqual(Angle(3 * pi / 2), Angle(pi) + Angle(pi/2))
        self.assertEqual(Angle(pi / 2), Angle(-pi / 2) + Angle(pi))

    def test_subtract_angles(self):
        self.assertEqual(Angle(3 * pi / 2), Angle(2 * pi) - Angle(pi/2))
        self.assertEqual(Angle(- pi / 2), Angle(0) - Angle(pi/2))

    def test_multiply_angle(self):
        self.assertEqual(Angle(pi), 2 * Angle(pi/2))

    def test_absolute_value(self):
        self.assertEqual(Angle(pi/2), abs(Angle(-pi / 2)))

    def test_angles_are_floats(self):
        self.assertEqual(pi, Angle(pi))


class VectorTestCase(TestCase):
    def test_new_vector(self):
        vector = Vector(1, 2, 3)
        self.assertEqual('(1, 2, 3)', str(vector))

    def test_magnitude(self):
        self.assertEqual(13, Vector(3, 4, 12).magnitude)
        self.assertEqual(13, Vector(-3, -4, -12).magnitude)
        self.assertEqual(3, Vector(3, 0, 0).magnitude)
        self.assertEqual(3, Vector(0, 3, 0).magnitude)
        self.assertEqual(3, Vector(0, 0, 3).magnitude)

    def test_add(self):
        self.assertEqual(Vector(-1, 4, 5), Vector(1, 3, -1) + Vector(-2, 1, 6))

    def test_subtract(self):
        self.assertEqual(Vector(3, 2, -7), Vector(1, 3, -1) - Vector(-2, 1, 6))

    def test_multiply(self):
        self.assertEqual(Vector(-4, 8, -12), -4 * Vector(1, -2, 3))
        self.assertEqual(Vector(-4, 8, -12), Vector(1, -2, 3) * -4)

    def test_divide(self):
        self.assertEqual(Vector(1, -2, 3), Vector(-4, 8, -12) / -4)

    def test_dot_product(self):
        self.assertEqual(-4, Vector(1, -2, 3).dot(Vector(-6, 5, 4)))
        self.assertEqual(-4, Vector(-6, 5, 4).dot(Vector(1, -2, 3)))

    def test_cross_product(self):
        self.assertEqual(Vector(-37, -13, -1), Vector(1, -3, 2).cross(Vector(-4, 11, 5)))
        self.assertEqual(Vector(37, 13, 1), Vector(-4, 11, 5).cross(Vector(1, -3, 2)))


