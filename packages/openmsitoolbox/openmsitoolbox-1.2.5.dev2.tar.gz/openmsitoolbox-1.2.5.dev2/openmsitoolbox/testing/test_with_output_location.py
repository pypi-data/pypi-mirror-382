" Class for any tests that should put output in some location "

# imports
import shutil
import pathlib
from .test_with_logger import TestWithLogger
from .config import TESTING_CONST


class TestWithOutputLocation(TestWithLogger):
    """
    Base class for unittest.TestCase classes that will put output in a directory.
    Also owns an OpenMSIStream Logger.
    """

    def __init__(self, *args, output_dir: pathlib.Path = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.output_dir = output_dir
        self.test_dependent_output_dirs = self.output_dir is None
        self.success = False

    def setUp(self) -> None:
        """
        Create the output location, removing it if it already exists.
        Set success to false before every test.
        """
        # If output directory isn't set, set it to a directory named for the test function
        if self.output_dir is None:
            self.output_dir = (
                TESTING_CONST.TEST_DIR_PATH
                / f"{self._testMethodName}_output_{TESTING_CONST.PY_VERSION}"
            )
        # if output from a previous test already exists, remove it
        if self.output_dir.is_dir():
            self.log_at_info(
                f"Will delete existing output location at {self.output_dir}"
            )
            try:
                shutil.rmtree(self.output_dir)
            except Exception as exc:  # pylint: disable=broad-except
                self.logger.error(
                    f"ERROR: failed to remove existing output at {self.output_dir}!",
                    exc_info=exc,
                )
        # create the directory to hold the output DB
        self.logger.debug(f"Creating output location at {self.output_dir}")
        self.output_dir.mkdir()
        # set the success variable to false
        self.success = False

    def tearDown(self) -> None:
        # if the test was successful, remove the output directory
        if self.success:
            try:
                self.logger.debug(
                    f"Test success={self.success}; removing output in {self.output_dir}"
                )
                if self.output_dir.exists():
                    shutil.rmtree(self.output_dir)
            except Exception as exc:  # pylint: disable=broad-except
                self.logger.error(
                    f"ERROR: failed to remove test output at {self.output_dir}!",
                    exc_info=exc,
                )
        else:
            self.logger.info(
                f"Test success={self.success}; output at {self.output_dir} will be retained."
            )
        # reset the output directory variable if we're using output directories per test
        if self.test_dependent_output_dirs:
            self.output_dir = None
