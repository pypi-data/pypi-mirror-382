# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for iot service requests
"""
import json
import logging
import sys
import pandas as pd
import requests
from .._utils._utils import ApiInputs


class PlatformIOTService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        consoleHandler = logging.StreamHandler(stream=sys.stdout)
        consoleHandler.setLevel(logging.INFO)
        self.logger.addHandler(consoleHandler)
        formatter = logging.Formatter('%(asctime)s  %(name)s.%(funcName)s  %(levelname)s: %(message)s',
                                      datefmt='%Y-%m-%dT%H:%M:%S')
        consoleHandler.setFormatter(formatter)

    def execute_reader(self, api_inputs: ApiInputs, command, nb_retry, parameters, command_timeout_sec=10):
        dt = None
        error = ""

        try:
            payload = {
                "Command": command,
                "CommandTimeout": command_timeout_sec,
                "Parameters": parameters,
                "RetryCount": nb_retry
            }

            headers = api_inputs.api_headers.default
            url = f"{api_inputs.iot_url}/api/gateway/core/sql/executereader"

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            resp = response.text

            if resp and resp.strip().startswith('['):
                obj = json.loads(resp)
                if obj:
                    dt = pd.DataFrame(obj)
                    self.logger.info(f'Dataframe rows count: {len(dt)}')
                else:
                    error = f"No data. Resp: {resp}"
        except Exception as ex:
            error = str(ex)

        return dt, error
