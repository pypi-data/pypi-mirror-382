from pathlib import Path
from sequence_test import SequenceTest
from gnps import GnpsSystem


def test_example1():
    p = Path(__file__).resolve().parent
    gnps = GnpsSystem.from_yaml(f"{p}/test_example1.yaml")

    expected_values = {
        "x": [0, 0, 3, 0, 3,  6,  0, 3],
        "y": [0, 0, 1, 4, 4, 17,  0, 0],
        "E": [0, 1, 2, 3, 4,  5,  6, 7],
        "z": [0, 0, 0, 4, 4,  7,  23, 0],
        "u": [1, 1, 0, 0, 0,  0,  10, 0],
    }

    input_values = {
        "u": [1, 1, 0, 0, 10, 10, 0],
    }

    test = SequenceTest(gnps, expected_values, input_values)

    test.run()


if __name__ == '__main__':
    test_example1()  # pragma: no cover
