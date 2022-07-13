import math


class Sequence:
    def __init__(self, function, pos=1):
        if not callable(function):
            raise TypeError("Sequence requires callable object")
        self._function = function
        self._pos = pos

    def get(self, i):
        return self._function(self._pos + i - 1)

    def sum(self, n):
        return sum(self.limit(n))

    def product(self, n):
        result = 1
        for i in self.limit(n):
            result *= i
        return result

    def product_slice(self, n, m):
        result = 1
        for i in self[n: m + 1]:
            result *= i
        return result

    def __iter__(self):
        while True:
            cursor = 1
            yield self.get(cursor)
            cursor += 1

    def limit(self, n):
        for i in range(1, n + 1):
            yield self.get(i)

    def map(self, function):
        return Sequence(lambda x: function(self._function(x)), pos=self._pos)

    def __neg__(self):
        return Sequence(lambda x: -self._function(x), pos=self._pos)

    def __pos__(self):
        return Sequence(lambda x: +self._function(x), pos=self._pos)

    def __add__(self, other):
        other_func = lambda x: other._function(x) if not callable(other) else other(x)
        return Sequence(lambda x: self._function(x) + other_func(x), pos=self._pos)

    def __mul__(self, other):
        other_func = lambda x: other._function(x) if not callable(other) else other(x)
        return Sequence(lambda x: self._function(x) * other_func(x), pos=self._pos)

    def __div__(self, other):
        other_func = lambda x: other._function(x) if not callable(other) else other(x)
        return Sequence(lambda x: self._function(x) / other_func(x), pos=self._pos)

    def __pow__(self, other):
        other_func = lambda x: other._function(x) if not callable(other) else other(x)
        return Sequence(lambda x: self._function(x) ** other_func(x), pos=self._pos)

    def __radd__(self, other):
        other_func = lambda x: other._function(x) if not callable(other) else other(x)
        return Sequence(lambda x: self._function(x) + other_func(x), pos=self._pos)

    def __rmul__(self, other):
        other_func = lambda x: other._function(x) if not callable(other) else other(x)
        return Sequence(lambda x: self._function(x) * other_func(x), pos=self._pos)

    def __rdiv__(self, other):
        other_func = lambda x: other._function(x) if not callable(other) else other(x)
        return Sequence(lambda x: other / self._function(x), pos=self._pos)

    def __lt__(self, other):
        raise NotImplementedError

    def __le__(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        raise NotImplementedError

    def __gt__(self, other):
        raise NotImplementedError

    def __ge__(self, other):
        raise NotImplementedError

    def __len__(self):
        return float('inf')

    def __repr__(self):
        return '[{}, {}, {}...]'.format(self[1], self[2], self[3])

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.get(item)
        elif isinstance(item, slice):
            start = 0 if item.start is None else item.start
            end = float("inf") if item.stop is None else item.stop
            step = 1 if item.step is None else item.step
            if end == float("inf"):
                return Sequence(self._function, pos=self._pos)
            else:
                iterable = []
                for i in range(start, end, step):
                    iterable.append(self.get(i))
                return iterable
        else:
            raise TypeError("Required int or slice, not {}".format(type(item).__name__))


class ArithmethicProgression(Sequence):
    def __init__(self, d, a0=0, offset=0):
        super().__init__(lambda n: a0 + d * (n - 1), pos=offset)
        self._d = d

    def sum(self, n):
        return ((self[0] + self[n]) / 2) * n

    @property
    def d(self):
        return self._d

    def __repr__(self):
        return "{" + f"A[d={self.d}]:" + super().__repr__() + '}'

    def find_nearest(self, el):
        return math.floor((el - self[0] + self.d) / self.d)

    def find(self, el):
        n = el - self[0] + self.d
        if n % self.d == 0:
            n = n // self.d
            if self[n] == el:
                return n
        return None

    def __contains__(self, key):
        return self.find(key) is not None

    @classmethod
    def from_sequence(cls, iterable):
        if len(iterable) > 1:
            d = iterable[1] - iterable[0]
            a0 = iterable[0]
            result = cls(d, a0)
            for i, item in enumerate(iterable[2:]):
                if result[i] != item:
                    raise ValueError("Impossible to create ArithmethicProgression from given sequence")
        else:
            raise ValueError("Not enough information to create ArithmethicProgression")


class GeometricProgression(Sequence):
    def __init__(self, q, b0=0, offset=0):
        super().__init__(lambda n: b0 * q ** (n - 1), pos=offset)
        self._q = q

    def sum(self, n):
        return self[0] * ((1 - self.q ** n) / (1 - self.q))

    def product(self, n, m):
        return (self[0] * self[n]) ** (n / 2)

    def product_slice(self, n, m):
        return self.product(m) / self.product(n - 1)

    @property
    def q(self):
        return self._q

    def __repr__(self):
        return "{" + f"G[q={self.q}]:" + super().__repr__() + '}'

    def find_nearest(self, el):
        return round(math.log(el / self[0], self.q) + 1)

    def find(self, el):
        n = round(math.log(el / self[0], self.q) + 1)
        if self[n] == el:
            return n
        else:
            return None

    def __contains__(self, key):
        return self.find(key) is not None

    @classmethod
    def from_sequence(cls, iterable):
        if len(iterable) > 1:
            q = iterable[1] / iterable[0]
            a0 = iterable[0]
            result = cls(q, a0)
            for i, item in enumerate(iterable[2:]):
                if result[i] != item:
                    raise ValueError("Impossible to create GeometricProgression from given sequence")
        else:
            raise ValueError("Not enough information to create GeometricProgression")
