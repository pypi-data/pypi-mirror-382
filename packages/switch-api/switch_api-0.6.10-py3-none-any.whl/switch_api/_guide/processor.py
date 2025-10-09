# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for .....
"""
import inspect
import logging
import sys
import pathlib
import importlib

from .._utils._utils import ApiInputs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.handlers = []
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


class RequestProcessor:

    def __init__(self, api_inputs: ApiInputs, script_path: str, data: dict) -> None:
        self.data = data
        self._api_inputs = api_inputs
        self._script_path = script_path

    def process(self):

        try:
            driver_module = self._get_module(self._script_path)

            execution_method = getattr(
                driver_module.task, self.data['execute'])

            parameters = inspect.signature(execution_method).parameters
            parameter_names = [param.lower() for param in parameters]

            # Check if 'api_inputs' is in parameter_names (case-insensitive)
            if 'api_inputs' in parameter_names:
                response = execution_method(
                    self._api_inputs, self.data["data"])
            else:
                response = execution_method(self.data["data"])

            return response

        except Exception as e:
            logger.error('Exception: ' + str(e))
            return False

    def _get_module(self, driver_code_file):
        module_name = pathlib.Path(driver_code_file).stem
        module = importlib.import_module(module_name)
        return importlib.import_module(module_name)
