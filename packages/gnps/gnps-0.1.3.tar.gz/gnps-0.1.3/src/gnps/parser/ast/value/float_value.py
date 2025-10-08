from .numerical_value import NumericalValue
from functools import singledispatchmethod


class FloatValue(NumericalValue):
    @singledispatchmethod
    def __init__(self, value):
        """Raises a ValueError if the input type is not supported."""
        super().__init__(None)
        raise ValueError(f"unsupported value format: {value}")

    @__init__.register(float)
    def _from_float(self, value: float = 0.0):
        """Initializes the Value from a float."""
        super().__init__(value)

    @__init__.register(int)
    def _from_int(self, value: int):
        """Initializes the Value from an int."""
        super().__init__(float(value))

    @__init__.register(str)
    def _from_str(self, string: str):
        """Initializes the Value from a string."""
        super().__init__(float(string))

    def __repr__(self):
        """
        Returns a string representation of the Value instance.

        Returns
        -------
        str
            a string representation of the Value instance
        """
        return f"FloatValue({self.value})"

    def __str__(self):
        """
        Returns a string representation of the value rounded to 6 decimal places.
        :return:
        """
        return f"{self.value:.6f}".rstrip("0").rstrip(".")
