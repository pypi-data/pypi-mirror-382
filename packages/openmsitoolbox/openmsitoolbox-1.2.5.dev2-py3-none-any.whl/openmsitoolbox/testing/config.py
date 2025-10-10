" Constants used in testing "

# imports
import pathlib
import sys


class TestRoutineConstants:
    """
    Constants used in running tests
    """

    # Paths to locations inside the code base
    TEST_DIR_PATH = (pathlib.Path(__file__).parent.parent.parent / "test").resolve()
    TEST_DATA_DIR_PATH = TEST_DIR_PATH / "data"
    # Version tag to use for separating output locations, consumer group IDs, etc.
    # for concurrently-running tests
    PY_VERSION = f"python_{sys.version.split()[0].replace('.','_')}"


TESTING_CONST = TestRoutineConstants()
