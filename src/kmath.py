import math


class Angle(float):
    def __new__(cls, rad=None, deg=None):
        if rad is None and deg is None:
            raise Exception('Either rad or deg needs to be provided')

        if rad is not None:
            return float.__new__(cls, rad)
        else:
            return float.__new__(cls, math.radians(deg))
    
    @property
    def rad(self):
        return self

    @property
    def deg(self):
        return math.degrees(self)

    def __repr__(self):
        return f'rad: {super().__repr__()} - deg: {self.deg}'

    def __str__(self) -> str:
        return self.__repr__()

    def __sub__(self, __x: float) -> 'Angle':
        return Angle(super().__sub__(__x))

    def __rsub__(self, __x: float) -> 'Angle':
        return Angle(super().__rsub__(__x))

    def __add__(self, __x: float) -> float:
        return Angle(super().__add__(__x))

    def __radd__(self, __x: float) -> float:
        return Angle(super().__radd__(__x))

    def __mul__(self, __x: float) -> float:
        return Angle(super().__mul__(__x))

    def __rmul__(self, __x: float) -> float:
        return Angle(super().__rmul__(__x))

    def __abs__(self) -> float:
        return Angle(super().__abs__())


PI = Angle(math.pi)


class Vector:
    def __init__(self,x ,y, z) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return str((self.x, self.y, self.z))

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def __add__(self, other: 'Vector'):
        return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector'):
        return self.__class__(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return self.__class__(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.__class__(self.x / other, self.y / other, self.z / other)

    def dot(self, other: 'Vector'):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vector'):
        return self.__class__(
            self.y * other.z - self.z * other.y, 
            self.z * other.x - self.x * other.z, 
            self.x * other.y - self.y * other.x
        )
        
 