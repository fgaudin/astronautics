import math

class Vector:
    def __init__(self,x ,y, z) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return str((self.x, self.y, self.z))

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
        
 