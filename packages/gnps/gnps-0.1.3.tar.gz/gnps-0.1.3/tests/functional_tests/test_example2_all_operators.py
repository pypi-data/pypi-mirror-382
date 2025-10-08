from pathlib import Path
from sequence_test import SequenceTest
from gnps import GnpsSystem


def test_example1():
    p = Path(__file__).resolve().parent
    gnps = GnpsSystem.from_yaml(f"{p}/test_example2.yaml")

    expected_values = {
        "E": [0, 1, 2, 3, 4,  5,  6, 7],
    }

    input_values = {
    }

    test = SequenceTest(gnps, expected_values, input_values)

    test.run()


if __name__ == '__main__':
    test_example1()  # pragma: no cover
