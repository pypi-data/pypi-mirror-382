from gnps import GnpsSystem
from gnps.parser.ast.value import FloatValue

from pathlib import Path



def test_example1():
    p = Path(__file__).resolve().parent
    gnps = GnpsSystem.from_yaml(f"{p}/test_example1.yaml")

    assert len(gnps.cells) == 1
    assert len(gnps.rules) == 4
    assert len(gnps.variables) == 5

    u = gnps.get_variable("u")
    assert u.value.value == 1

    x = gnps.get_variable("x")
    assert x.value.value == 0

    y = gnps.get_variable("y")
    assert y.value.value == 0

    E = gnps.get_variable("E")
    assert E.value.value == 0

    z = gnps.get_variable("z")
    assert z.value.value == 0

    test_x_values = [0, 3, 0, 3,  6,  0, 3]
    test_y_values = [0, 1, 4, 4, 17,  0, 0]
    test_E_values = [1, 2, 3, 4,  5,  6, 7]
    test_z_values = [0, 0, 4, 4,  7, 23, 0]
    test_u_values = [1, 0, 0, 0,  0, 10, 0]

    u_values = [1, 1, 0, 0, 10, 10, 0]
    for i in range(len(u_values)):
        u.value = FloatValue(u_values[i])
        gnps.step()
        assert u.value.value == test_u_values[i]
        assert x.value.value == test_x_values[i]
        assert y.value.value == test_y_values[i]
        assert E.value.value == test_E_values[i]
        assert z.value.value == test_z_values[i]

