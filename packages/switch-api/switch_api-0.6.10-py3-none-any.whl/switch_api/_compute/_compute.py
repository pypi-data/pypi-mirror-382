# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for compute.
"""

import json
import logging
import sys
import uuid
import pandas as pd
from typing import List
from datetime import datetime

import requests

from .._utils._utils import ApiInputs

from ._models import (CarbonCacheInfo, LocationInfo)
from ._iotservice import PlatformIOTService
from ._commands import (COMMAND_INSTALLATION_LOCATION_DETAIL,
                        COMMAND_CARBON_CALCULATION_EXPRESSION)
from ._utils import safe_uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  %(name)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def get_carbon_calculation_expression(df: pd.DataFrame, api_inputs: ApiInputs) -> pd.DataFrame:
    """
    Retrieves the Carbon Calculation Expression for calculating Carbon.

    Returns
    -------
    pd.DataFrame
        DataFrame containing sensor details including the carbon calculation expression,
        or an empty DataFrame if no data is found.
    """
    if df.empty:
        logger.info('Input DataFrame is empty.')
        return pd.DataFrame()
    
    data_frame = df.copy()
    
    obj_prop_ids = data_frame['ObjectPropertyId'].str.lower().unique().tolist()
    unique_years = data_frame['TimestampLocal'].dt.year.unique().tolist()

    logger.info('Retrieving carbon calculation expressions.')

    query_carbon = COMMAND_CARBON_CALCULATION_EXPRESSION(
        year_list=unique_years,
        obj_prop_ids=obj_prop_ids
    )

    response_carbon = _execute_iot_sql_query(api_inputs, query_carbon)
    
    if response_carbon is None or not response_carbon.text:
        logger.info("No carbon calculation expressions returned from SQL.")
        return pd.DataFrame()

    try:
        carbon_calculations_df = pd.read_json(response_carbon.text, orient='records')

        if carbon_calculations_df.empty:
            logger.info('Carbon calculations expressions DataFrame is empty.')
            return pd.DataFrame()
        
        logger.info('Successfully retrieved %d carbon calculation expressions.', len(carbon_calculations_df))
        return carbon_calculations_df
    except ValueError as e:
        logger.error("Failed to parse JSON for carbon calculations: %s", e)
        return pd.DataFrame()

def _execute_iot_sql_query(api_inputs: ApiInputs, query: str) -> requests.Response:
    """Helper function to execute an SQL query via the IOT service."""

    url = f"{api_inputs.iot_url}/api/gateway/core/sql/executereader"
    headers = api_inputs.api_headers.default

    payload = {
        "Command": query,
        "CommandTimeout": 10,
        "Parameters": [],
        "RetryCount": 3
    }
    
    try:
        logger.info(f"Sending request: POST {url}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response
    except requests.exceptions.RequestException as e:
        logger.error("API Call failed: %s", e)
        return None
