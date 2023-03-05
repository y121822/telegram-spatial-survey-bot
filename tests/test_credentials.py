from unittest import main
from engine.utils.utils import credentials
from tests.utils.utils import RunAllTestCase
from tests.utils.data import Data, Result


class CredentialsTest(RunAllTestCase, Data, Result):
    """Test credentials function in
       engine utils utils.py"""
    def test_credentials(self):
        self.expectEqual(credentials(self.data_credentials), self.result_credentials)


if __name__ == "__main__":
    main()
