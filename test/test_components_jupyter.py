import copy
from unittest import TestCase
from unittest import mock
from schema import SchemaError

import skelebot as sb
import argparse

class TestJupyter(TestCase):

    jupyter = {
        "port": 123,
        "folder": "test"
    }

    def test_addParsers(self):
        jupyter = sb.components.jupyter.Jupyter(port=1127, folder="notebooks/")

        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        subparsers = parser.add_subparsers(dest="job")
        subparsers = jupyter.addParsers(subparsers)

        self.assertNotEqual(subparsers.choices["jupyter"], None)

    @mock.patch('skelebot.components.jupyter.docker')
    def test_execute_R(self, mock_docker):
        mock_docker.build.return_value = 0
        config = sb.objects.config.Config(language="R")
        args = argparse.Namespace()

        jupyter = sb.components.jupyter.Jupyter(port=1127, folder="notebooks/")
        jupyter.execute(config, args)

        expectedCommand = "jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --notebook-dir=notebooks/"

        mock_docker.build.assert_called_with(config)
        mock_docker.run.assert_called_with(config, expectedCommand, "i", ["1127:8888"], ".", "jupyter")

    @mock.patch('skelebot.components.jupyter.docker')
    def test_execute_Python(self, mock_docker):
        mock_docker.build.return_value = 0
        config = sb.objects.config.Config(language="Python")
        args = argparse.Namespace()

        jupyter = sb.components.jupyter.Jupyter(port=1127, folder="notebooks/")
        jupyter.execute(config, args)

        expectedCommand = "jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --notebook-dir=notebooks/"

        mock_docker.build.assert_called_with(config)
        mock_docker.run.assert_called_with(config, expectedCommand, "i", ["1127:8888"], ".", "jupyter")

    def test_validate_valid(self):
        try:
            sb.components.jupyter.Jupyter.validate(self.jupyter)
        except:
            self.fail("Validation Raised Exception Unexpectedly")

    def validate_error(self, attr, reset, expected):
        jupyter = copy.deepcopy(self.jupyter)
        jupyter[attr] = reset

        try:
            sb.components.jupyter.Jupyter.validate(jupyter)
        except SchemaError as error:
            self.assertEqual(error.code, "Jupyter '{attr}' must be a{expected}".format(attr=attr, expected=expected))

    def test_invalid(self):
        self.validate_error('port', "abc", 'n Integer')
        self.validate_error('folder', 123, ' String')

if __name__ == '__main__':
    unittest.main()
