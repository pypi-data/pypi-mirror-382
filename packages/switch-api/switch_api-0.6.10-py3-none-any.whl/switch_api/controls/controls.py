# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for sending control request of sensors.
"""

import json
import logging
import os
import sys
import time
from typing import Dict, List, Union, Optional
import uuid
import pandas
import requests

from ._enums import ControlStatus
from ._constants import (IOT_RESPONSE_ERROR, IOT_RESPONSE_SUCCESS, WS_DEFAULT_PORT, WS_MQTT_CONNECTION_TIMEOUT,
                         WS_MQTT_DEFAULT_MAX_TIMEOUT, COL_CONTROL_DEFAULT_CONTROL_VALUE, COL_OBJECT_PROPERTY_ID, COL_CONTROL_NAME,
                         COL_CONTROL_LABEL, COL_CONTROL_VALUE, COL_CONTROL_CONTINUE_VALUE, COL_CONTROL_TTL, COL_CONTROL_PRIORITY,
                         COL_CONTROL_INSTALLATION_ID, COL_CONTROL_STATUS, COL_CONTROL_TIMESTAMP, COL_CONTROL_TIMESTAMP_LOCAL,
                         COL_CONTROL_PIVOTKEY, COL_CONTROL_INFOCOLUMNS, COL_CONTROL_IS_EXTENDED_CONTROL, COL_CONTROL_EXISTS_IN_CONTROL_CACHE)
from ._mqtt import SwitchMQTT
from .._utils._utils import ApiInputs, _with_func_attrs, is_valid_uuid
from ..cache.cache import get_cache, set_cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  %(name)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)

global _control_api_endpoint
global _control_ws_host
global _control_ws_port
global _control_ws_username
global _control_ws_password
global _control_ws_max_timeout

_control_api_endpoint = ''
_control_ws_host = ''
_control_ws_port = WS_DEFAULT_PORT
_control_ws_username = ''
_control_ws_password = ''
_control_ws_max_timeout = WS_MQTT_DEFAULT_MAX_TIMEOUT

global _control_components

_control_components = {}


def set_control_variables(api_endpoint: str, ws_host: str, user_name: str, password: str,
                          ws_port: int = WS_DEFAULT_PORT, max_timeout: int = WS_MQTT_DEFAULT_MAX_TIMEOUT, bypass_username_password: bool = False):
    """Set Control Variables

    Set Control Variables needed to enable control request to MQTT Broker when running locally.

    In Production, these are pulled from the deployment environment variables.

    Parameters
    ----------
    api_endpoint : str
        Platform IoT API Endpoint.
    host : str
        Host URL for MQTT connection. This needs to be datacenter specfic URL.
    port : int
        MQTT message broker port. Defaults to 443.
    user_name : str
        Username for MQTT connection
    password: str
        Password for MQTT connection
    max_timeout : int
        Max timeout set for the controls module. Defaults to 30 seconds.
    """
    global _control_api_endpoint
    global _control_ws_host
    global _control_ws_port
    global _control_ws_username
    global _control_ws_password
    global _control_ws_max_timeout

    # Check if endpoint is a valid URL
    if not api_endpoint.startswith('https://'):
        raise ValueError(
            "Invalid IoT API Endpoint. The IoT host should start with 'https://'.")

    # # Check if host is a valid URL
    if not ws_host.startswith('wss://'):
        raise ValueError(
            "Invalid IoT Websocket MQTT Host. The IoT host should start with 'wss://'.")

    # Check if user_name and password are not empty
    if not bypass_username_password:
        if not user_name:
            raise ValueError("user_name cannot be empty.")
        if not password:
            raise ValueError("password cannot be empty.")

    # Check if max_timeout is greated than 0
    if max_timeout < 1:
        raise ValueError("max_timeout should be greater than 0.")

    # Set global variables
    _control_api_endpoint = api_endpoint
    _control_ws_host = ws_host
    _control_ws_port = ws_port
    _control_ws_username = user_name
    _control_ws_password = password
    _control_ws_max_timeout = max_timeout


def submit_control_continue(api_inputs: ApiInputs, data: pandas.DataFrame, information_columns: list = [], is_send_control: bool = True, ws_timeout_in_seconds: int = WS_MQTT_CONNECTION_TIMEOUT):
    """Submit control of sensor(s)

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    data : pandas.DataFrame
        List of Sensors for control request.
        Containing columns that are present in `add_control_component` function
    information_columns: list[str]
        List of dataframe column names that serves as a metadata when results are arranged.
    is_send_control: bool
        Defaults to True.
        Flag wether to send actual control request or not.
        Response is a mock that the request is successfully controlled.
    ws_timeout_in_seconds : int, Optional:
        Default value is 180 seconds. Value must be between 1 and max control timeout set in the control variables.
            When value is set to 0 it defaults to max timeout value.
            When value is above max timeout value it defaults to max timeout value.


    Returns
    -------
    Dataframe
        control_response  = is the list of sensors that were controlled or not
    """
    global _control_components
    control_results = []

    # Validate Information Columns if existing
    missing_columns = [
        col for col in information_columns if col not in data.columns]

    if missing_columns:
        logger.error(
            f"These columns are not in the DataFrame: {missing_columns}")
        raise ValueError(
            f"These columns are not in the DataFrame: {missing_columns}")

    for name, value in _control_components.items():

        logger.info(f'Processing Control Component: {name}')

        column_with_object_installation_id = value[0]
        column_with_object_property_id = value[1]
        column_with_label = value[2]
        column_with_value = value[3]
        column_with_continue = value[4]
        column_with_default_value = value[5]
        timeout_in_seconds = value[6]
        priority = value[7]

        if column_with_object_property_id not in data.columns:
            logger.error(
                f"ObjectPropertyId column {column_with_object_property_id} not found in the DataFrame")
            raise ValueError(
                f"ObjectPropertyId column {column_with_object_property_id} not found in the DataFrame")
        elif column_with_label not in data.columns:
            logger.error(
                f"Label column {column_with_label} not found in the DataFrame")
            raise ValueError(
                f"Label column {column_with_label} not found in the DataFrame")
        elif column_with_value not in data.columns:
            logger.error(
                f"Value column {column_with_value} not found in the DataFrame")
            raise ValueError(
                f"Value column {column_with_value} not found in the DataFrame")
        elif column_with_object_installation_id not in data.columns:
            logger.error(
                f"InstallationId column {column_with_object_installation_id} not found in the DataFrame")
            raise ValueError(
                f"InstallationId column {column_with_object_installation_id} not found in the DataFrame")
        elif COL_CONTROL_TIMESTAMP_LOCAL not in data.columns:
            logger.error(
                f"TimestampLocal not found in the DataFrame")
            raise ValueError(
                f"TimestampLocal not found in the DataFrame")
        elif column_with_continue not in data.columns:
            logger.error(
                f"Continue column {column_with_continue} not found in the DataFrame")
            raise ValueError(
                f"Continue column {column_with_continue} not found in the DataFrame")
        elif column_with_default_value != None and column_with_default_value not in data.columns:
            logger.error(
                f"Default Value column {column_with_default_value} not found in the DataFrame")
            raise ValueError(
                f"Default Value column {column_with_default_value} not found in the DataFrame")

        data[column_with_value] = pandas.to_numeric(
            data[column_with_value], errors='coerce')

        grouped = data.groupby(column_with_object_installation_id)

        for installation_id, group in grouped:

            control_df = pandas.DataFrame()
            group[COL_CONTROL_NAME] = name

            if column_with_default_value == None:
                control_df = pandas.DataFrame({
                    COL_CONTROL_NAME: group[COL_CONTROL_NAME],
                    COL_OBJECT_PROPERTY_ID: group[column_with_object_property_id],
                    COL_CONTROL_LABEL: group[column_with_label],
                    COL_CONTROL_VALUE: group[column_with_value],
                    COL_CONTROL_CONTINUE_VALUE: group[column_with_continue],
                    COL_CONTROL_TTL: timeout_in_seconds,
                    COL_CONTROL_PRIORITY: priority
                })
            else:
                control_df = pandas.DataFrame({
                    COL_CONTROL_NAME: group[COL_CONTROL_NAME],
                    COL_OBJECT_PROPERTY_ID: group[column_with_object_property_id],
                    COL_CONTROL_LABEL: group[column_with_label],
                    COL_CONTROL_VALUE: group[column_with_value],
                    COL_CONTROL_CONTINUE_VALUE: group[column_with_continue],
                    COL_CONTROL_DEFAULT_CONTROL_VALUE: group[column_with_default_value],
                    COL_CONTROL_TTL: timeout_in_seconds,
                    COL_CONTROL_PRIORITY: priority
                })

            try:
                control_result_df = group.copy()

                if control_df.empty:
                    logger.warning("Control Dataframe is Empty.")
                    control_result_df[COL_CONTROL_STATUS] = ControlStatus.NoControlRequired.value
                else:
                    control_result_df = __send_control(
                        api_inputs=api_inputs,
                        df=control_df,
                        installation_id=installation_id,
                        has_priority=True,
                        session_id=uuid.uuid4(),
                        control_name=name,
                        timeout=ws_timeout_in_seconds,
                        is_send_control=is_send_control
                    )

                if not is_send_control or control_df.empty:
                    control_result_df = control_result_df.rename(
                        columns={column_with_object_property_id: COL_OBJECT_PROPERTY_ID, column_with_value: COL_CONTROL_VALUE})

                control_result_df = pandas.merge(group, control_result_df[[
                    COL_OBJECT_PROPERTY_ID, COL_CONTROL_VALUE, COL_CONTROL_STATUS]], left_on=column_with_object_property_id, right_on=COL_OBJECT_PROPERTY_ID, how='left')

                new_order = [COL_CONTROL_NAME, COL_CONTROL_INSTALLATION_ID,
                             COL_CONTROL_TIMESTAMP_LOCAL, COL_CONTROL_PIVOTKEY, COL_CONTROL_STATUS, COL_CONTROL_INFOCOLUMNS]

                control_result_df[COL_CONTROL_STATUS].fillna(0, inplace=True)
                control_result_df[COL_CONTROL_STATUS] = control_result_df[COL_CONTROL_STATUS].astype(
                    int)

                # We Transform NaN and None to zeros
                def transform_info_columns(row, info_cols):
                    info_dict = {col: row[col] if pandas.notna(
                        row[col]) else 0 for col in info_cols}

                    return json.dumps(info_dict)

                # Apply the transformation
                control_result_df[COL_CONTROL_INFOCOLUMNS] = control_result_df.apply(
                    lambda row: transform_info_columns(row, information_columns), axis=1)

                # Reindex the DataFrame
                control_result_df = control_result_df.reindex(
                    columns=new_order)
                control_result_df.drop(control_result_df.columns.difference(
                    new_order), axis=1, inplace=True)

                control_result_df = control_result_df.rename(
                    columns={COL_CONTROL_TIMESTAMP_LOCAL: COL_CONTROL_TIMESTAMP})

                # Add Empty Column Space here after PivotKey column
                insert_position = control_result_df.columns.get_loc(
                    COL_CONTROL_PIVOTKEY)
                control_result_df.insert(insert_position + 1, 'Blank', '')

                control_results.append(control_result_df)

            except Exception as e:
                logger.info(
                    f"An unexpected error occurred: {e}")

    _control_components = {}

    return pandas.concat(control_results, ignore_index=True)


@_with_func_attrs(df_required_columns=['ObjectPropertyId', 'Value', 'TTL'])
@_with_func_attrs(df_optional_columns=['DefaultControlValue'])
def __send_control(api_inputs: ApiInputs, installation_id: Union[uuid.UUID, str], df: pandas.DataFrame, has_priority: bool, session_id: uuid.UUID,
                   control_name: str, is_send_control: bool = True, timeout: int = WS_MQTT_CONNECTION_TIMEOUT):
    """Submit control of sensor(s)

    Required fields are:

    - ObjectPropertyId
    - Value
    - TTL

    Optional fields are:
    - DefaultControlValue : if this column is present, after TTL, the sensor will turn into this value.

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    df : pandas.DataFrame
        List of Sensors for control request.
    has_priority : bool
        Flag if dataframe passes contains has_priority column.
    session_id : uuid.UUID., Optional
        Session Id to reuse when communicating with IoT Endpoint and MQTT Broker
    timeout : int, Optional:
        Default value is 180 seconds. Value must be between 1 and max control timeout set in the control variables.
            When value is set to 0 it defaults to max timeout value.
            When value is above max timeout value it defaults to max timeout value.

    Returns
    -------
    Dataframe
        control_response  = is the list of sensors that were request to be controlled with status labelling if it was successful or not by the MQTTT message broker
    """
    global _control_api_endpoint
    global _control_ws_host
    global _control_ws_port
    global _control_ws_username
    global _control_ws_password
    global _control_ws_max_timeout

    data_frame = df.copy()
    control_cache_key = f"{api_inputs.api_project_id}-{installation_id}-{control_name}-submit-control-cache"
    switch_mqtt = SwitchMQTT(host_address=_control_ws_host, host_port=_control_ws_port,
                             username=_control_ws_username, password=_control_ws_password,
                             session_id=session_id, client_id=api_inputs.data_feed_id, email=api_inputs.email_address,
                             project_id=api_inputs.api_project_id, installation_id=str(installation_id))

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using the API.")
        return pandas.DataFrame()

    if not is_valid_uuid(installation_id):
        logger.error("Installation Id is not a valid UUID.")
        return pandas.DataFrame()

    if data_frame.empty:
        logger.error("Dataframe is empty.")
        return pandas.DataFrame()

    if timeout < 0:
        logger.error(
            f"Invalid timeout value. Timeout should be between 0 and {_control_ws_max_timeout}. Setting to zero will default to max timeout.")
        return pandas.DataFrame()

    if timeout > _control_ws_max_timeout:
        logger.critical(
            f'Timeout is greater than Max Timeout value. Setting timeout to Max Timeout Value instead.')
        timeout = _control_ws_max_timeout

    if timeout == 0:
        timeout = _control_ws_max_timeout

    if not is_valid_uuid(session_id):
        session_id = uuid.uuid4()

    required_columns = getattr(submit_control, 'df_required_columns')
    proposed_columns = data_frame.columns.tolist()

    if not set().issubset(data_frame.columns):
        logger.exception('Missing required column(s): %s', set(
            required_columns).difference(proposed_columns))
        return 'control.submit_control(): dataframe must contain the following columns: ' + ', '.join(
            required_columns), pandas.DataFrame()

    control_cache_df = get_control_cache(
        api_inputs=api_inputs, key=control_cache_key, scope_id=api_inputs.api_project_id)

    if control_cache_df.empty:
        logger.error('Cache is empty.')
        control_cache_df = pandas.DataFrame(columns=[COL_OBJECT_PROPERTY_ID])

    logger.info(control_cache_df)

    # Check if Input Dataframe sensors is present in the Cache (Dictionary of Records)
    data_frame['NormalizedObjectPropertyId'] = data_frame[COL_OBJECT_PROPERTY_ID].str.lower()
    control_cache_df['NormalizedObjectPropertyId'] = control_cache_df[COL_OBJECT_PROPERTY_ID].str.lower()
    # Check if each row's ObjectPropertyId in data_frame is in control_cache_df
    data_frame[COL_CONTROL_EXISTS_IN_CONTROL_CACHE] = data_frame['NormalizedObjectPropertyId'].isin(
        control_cache_df['NormalizedObjectPropertyId'])
    data_frame.drop(columns=['NormalizedObjectPropertyId'], inplace=True)
    control_cache_df.drop(columns=['NormalizedObjectPropertyId'], inplace=True)

    data_frame[COL_CONTROL_IS_EXTENDED_CONTROL] = (data_frame[COL_CONTROL_EXISTS_IN_CONTROL_CACHE] == True) & (
        data_frame[COL_CONTROL_CONTINUE_VALUE] > -1)
    data_frame[COL_CONTROL_STATUS] = ControlStatus.NoControlRequired.value

    # Set Filter Conditions
    send_condition = ((data_frame[COL_CONTROL_EXISTS_IN_CONTROL_CACHE] == False) & (data_frame[COL_CONTROL_VALUE] > -1)) | \
        ((data_frame[COL_CONTROL_EXISTS_IN_CONTROL_CACHE] == True)
         & (data_frame[COL_CONTROL_CONTINUE_VALUE] > -1))
    relinquish_condition = ((data_frame[COL_CONTROL_EXISTS_IN_CONTROL_CACHE] == True) & (
        data_frame[COL_CONTROL_CONTINUE_VALUE] <= -1))

    df_matrix = data_frame.copy()

    send_df = df_matrix[send_condition]
    # If IsExtendControl, we swap ContinueValue to Value Column
    send_df.loc[(send_df[COL_CONTROL_IS_EXTENDED_CONTROL] == True),
                COL_CONTROL_VALUE] = send_df[COL_CONTROL_CONTINUE_VALUE]

    relinquish_df = df_matrix[relinquish_condition]
    
    if COL_CONTROL_DEFAULT_CONTROL_VALUE in df_matrix.columns:
        relinquish_df[COL_CONTROL_VALUE] = relinquish_df[COL_CONTROL_DEFAULT_CONTROL_VALUE]
    else:
        relinquish_df[COL_CONTROL_VALUE] = 'null'
    relinquish_df[COL_CONTROL_TTL] = 0

    control_request_df = pandas.concat([send_df, relinquish_df])

    if control_request_df.empty:
        logger.info("No controls to be sent.")
        return df_matrix

    acknowledgement_df = control_request_df.copy()
    acknowledgement_df = format_acknowledgement_payload_df(
        df=acknowledgement_df, required_columns=required_columns, has_priority=has_priority)

    if is_send_control:
        _, result_df = log_control_request(
            api_inputs=api_inputs, df=acknowledgement_df, session_id=session_id, installation_id=installation_id)
        if result_df.empty:
            df_matrix[COL_CONTROL_STATUS] = ControlStatus.NotSentToService.value
            return df_matrix

    control_request_df = control_request_df.copy()
    control_request_df = format_control_payload_df(
        required_columns=required_columns, has_priority=has_priority, df=control_request_df)

    def process_paged_request(df, page_size: int = 20):
        paged_results = pandas.DataFrame()
        total_rows = len(df)
        num_pages = (total_rows + page_size - 1) // page_size

        for page_num in range(num_pages):
            start_idx = page_num * page_size
            end_idx = min((page_num + 1) * page_size, total_rows)

            # Get the data for the current page
            page_data = df.iloc[start_idx:end_idx]

            result = send_control(page_data)
            paged_results = pandas.concat([paged_results, result])

        return paged_results

    def send_control(page_data):
        retry_count = 0
        max_retries = 3
        success_results = pandas.DataFrame()
        missing_results = pandas.DataFrame()

        dataframe_to_control = page_data.copy()

        while retry_count < max_retries:
            success_response, missing_response = switch_mqtt.send_control_request(
                sensors=dataframe_to_control.to_dict(orient='records'))

            if not isinstance(success_response, pandas.DataFrame):
                logger.error(success_response)
                retry_count += 1
                time.sleep(1)
                continue

            if not success_response.empty:
                logger.info("Sensors that were successful in control request:")
                logger.info(success_response.to_string(index=False))
                success_results = pandas.concat(
                    [success_results, success_response])

            if not missing_response.empty:
                logger.error(
                    "Sensors that aren't successful in control request.")
                logger.info(missing_response.to_string(index=False))
                missing_results = pandas.concat(
                    [missing_results, missing_response])

            if missing_response.empty:
                break

            # Discount the successful control requests from the ones going for a retry
            if not success_response.empty:
                dataframe_to_control = dataframe_to_control[~dataframe_to_control['sensorId'].isin(
                    success_response['sensorId'])]

            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)

        if missing_results.empty:
            success_results['status'] = True
            success_results['writeStatus'] = 'Complete'
            control_result = success_results.copy()
        else:
            control_result = pandas.merge(page_data, missing_results, left_on='sensorId',
                                          right_on='sensorId', how='left', suffixes=('_df1', '_df2'))

            control_result['status'] = control_result['writeStatus'].isnull()

            columns_to_drop = ['controlValue_df2', 'duration_df2',
                               'priority_df2', 'defaultControlValue_df2']

            # Filter columns that exist in the dataframe
            existing_columns_to_drop = [
                col for col in columns_to_drop if col in control_result.columns]

            if existing_columns_to_drop:
                control_result.drop(
                    existing_columns_to_drop, axis=1, inplace=True)

            control_result['status'] = control_result['status'].fillna(True)

            control_result = control_result.rename(columns={
                'controlValue_df1': 'controlValue',
                'duration_df1': 'duration',
                'priority_df1': 'priority',
                'defaultControlValue_df1': 'defaultControlValue'
            })

        logger.info(control_result)
        return control_result

    if is_send_control:
        is_connected = switch_mqtt.connect(timeout=timeout)

        if not is_connected:
            logger.info("Could not connect to MQTT Broker.")
            return 'Could not connect to MQTT Broker.', pandas.DataFrame()

        control_results = process_paged_request(control_request_df)
        control_results = control_results.rename(
            columns={'sensorId': COL_OBJECT_PROPERTY_ID})
        control_results = pandas.merge(control_results, df_matrix[[
            COL_OBJECT_PROPERTY_ID, COL_CONTROL_IS_EXTENDED_CONTROL, COL_CONTROL_EXISTS_IN_CONTROL_CACHE]], on=COL_OBJECT_PROPERTY_ID, how='left')

        switch_mqtt.disconnect()
    else:
        control_results = control_request_df.copy()
        control_results['status'] = True
        control_results['writeStatus'] = "Complete"

    control_results = rename_control_results_column_df(
        result_df=control_results)

    # Set Control Status based on returned results from the Submit Control response dataframe
    control_results[COL_CONTROL_STATUS] = control_results[COL_CONTROL_STATUS].apply(
        lambda x: ControlStatus.ControlSuccessful.value if pandas.notna(x) else ControlStatus.ControlFailed.value)

    df_matrix.set_index(COL_OBJECT_PROPERTY_ID, inplace=True)
    control_results.set_index(COL_OBJECT_PROPERTY_ID, inplace=True)

    df_matrix.update(control_results[[COL_CONTROL_STATUS]])

    df_matrix.reset_index(inplace=True)
    control_results.reset_index(inplace=True)

    df_matrix.loc[(df_matrix[COL_CONTROL_IS_EXTENDED_CONTROL] == True) &
                  (df_matrix[COL_CONTROL_STATUS] == True), COL_CONTROL_STATUS] = ControlStatus.ControlResent.value
    df_matrix.loc[(df_matrix[COL_CONTROL_EXISTS_IN_CONTROL_CACHE] == True) &
                  (df_matrix[COL_CONTROL_IS_EXTENDED_CONTROL] == False) &
                  (df_matrix[COL_CONTROL_STATUS] == True), COL_CONTROL_STATUS] = ControlStatus.NotSentToService.value

    # Update Cache With Results
    update_control_cache(api_inputs=api_inputs, control_cache_key=control_cache_key,
                         control_cache_df=control_cache_df, control_results_df=df_matrix)

    df_matrix.drop(
        columns=[COL_CONTROL_IS_EXTENDED_CONTROL, COL_CONTROL_EXISTS_IN_CONTROL_CACHE], inplace=True)

    if not is_send_control:
        df_matrix.drop(
            columns=[COL_CONTROL_CONTINUE_VALUE, COL_CONTROL_NAME], inplace=True)

    if has_priority and 'priority' in df_matrix:
        df_matrix = df_matrix.rename(
            columns={'priority': COL_CONTROL_PRIORITY})

    return df_matrix


@ _with_func_attrs(df_required_columns=['ObjectPropertyId', 'Value', 'TTL'])
@ _with_func_attrs(df_optional_columns=['DefaultControlValue'])
def submit_control(api_inputs: ApiInputs, installation_id: Union[uuid.UUID, str], df: pandas.DataFrame, has_priority: bool, session_id: uuid.UUID, timeout: int = WS_MQTT_CONNECTION_TIMEOUT):
    """Submit control of sensor(s)

    Required fields are:

    - ObjectPropertyId
    - Value
    - TTL
    - DefaultControlValue (Optional)

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    df : pandas.DataFrame
        List of Sensors for control request.
    has_priority : bool
        Flag if dataframe passes contains has_priority column.
    session_id : uuid.UUID., Optional
        Session Id to reuse when communicating with IoT Endpoint and MQTT Broker
    timeout : int, Optional:
        Default value is 30 seconds. Value must be between 1 and max control timeout set in the control variables.
            When value is set to 0 it defaults to max timeout value.
            When value is above max timeout value it defaults to max timeout value.

    Returns
    -------
    tuple
        control_response  = is the list of sensors that were request to be controlled with status labelling if it was successful or not by the MQTTT message broker
    """
    global _control_api_endpoint
    global _control_ws_host
    global _control_ws_port
    global _control_ws_username
    global _control_ws_password
    global _control_ws_max_timeout

    default_control_value_column = 'DefaultControlValue'

    data_frame = df.copy()

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using the API.")
        return 'Invalid api_inputs.', pandas.DataFrame()

    if not is_valid_uuid(installation_id):
        logger.error("Installation Id is not a valid UUID.")
        return 'Invalid installation_id.', pandas.DataFrame()

    if data_frame.empty:
        logger.error("Dataframe is empty.")
        return 'Empty dataframe.', pandas.DataFrame()

    if timeout < 0:
        logger.error(
            f"Invalid timeout value. Timeout should be between 0 and {_control_ws_max_timeout}. Setting to zero will default to max timeout.")
        return 'Invalid timeout.', pandas.DataFrame()

    if timeout > _control_ws_max_timeout:
        logger.critical(
            f'Timeout is greater than Max Timeout value. Setting timeout to Max Timeout Value instead.')
        timeout = _control_ws_max_timeout

    if timeout == 0:
        timeout = _control_ws_max_timeout

    if not is_valid_uuid(session_id):
        session_id = uuid.uuid4()

    required_columns = getattr(submit_control, 'df_required_columns')
    proposed_columns = data_frame.columns.tolist()

    if not set().issubset(data_frame.columns):
        logger.exception('Missing required column(s): %s', set(
            required_columns).difference(proposed_columns))
        return 'control.submit_control(): dataframe must contain the following columns: ' + ', '.join(
            required_columns), pandas.DataFrame()

    control_columns_required = ['ObjectPropertyId',
                                COL_CONTROL_VALUE, 'TTL', 'Priority']
    data_frame.drop(data_frame.columns.difference(
        control_columns_required), axis=1, inplace=True)

    # We convert these columns to the required payload property names
    data_frame = data_frame.rename(columns={'ObjectPropertyId': 'id',
                                            COL_CONTROL_VALUE: 'v', 'TTL': 'dsecs'})

    if has_priority:
        if not 'Priority' in data_frame:
            logger.error(
                f"has_priority is set to True, but the dataframe does not have the column 'Priority'.")
            return 'Missing Priority column', pandas.DataFrame()
        else:
            data_frame = data_frame.rename(columns={'Priority': 'p'})

    json_payload = {
        "sensors": data_frame.to_dict(orient='records'),
        "email": api_inputs.email_address,
        "userid": api_inputs.user_id,
        "sessionId": str(session_id)
    }

    url = f"{_control_api_endpoint}/api/gateway/{str(installation_id)}/log-control-request"

    headers = api_inputs.api_headers.default

    logger.info("Sending Control Request to IoT API: POST %s", url)
    logger.info("Control Request Session Id: %s", str(session_id))
    logger.info("Control Request for User: %s=%s",
                api_inputs.email_address, api_inputs.user_id)

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    response_object = json.loads(response.text)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.",
                     response.status_code, response.reason)
        logger.error(response_object[IOT_RESPONSE_ERROR])
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s',
                     response.request.url)
        return response_status, pandas.DataFrame()

    if not response_object[IOT_RESPONSE_SUCCESS]:
        logger.error(response_object[IOT_RESPONSE_ERROR])
        return response_object[IOT_RESPONSE_SUCCESS], pandas.DataFrame()

    # Proceeds when the control request is successful
    logger.info('IoT API Control Request is Successful.')

    data_frame = df.copy()

    if default_control_value_column in data_frame.columns:
        control_columns_required.append(default_control_value_column)

    data_frame = data_frame.rename(columns={'ObjectPropertyId': 'sensorId',
                                            COL_CONTROL_VALUE: 'controlValue', 'TTL': 'duration', 'DefaultControlValue': 'defaultControlValue'})

    if has_priority:
        if not 'Priority' in data_frame:
            logger.error(
                f"The dataframe does not have the column 'Priority'.")
        else:
            data_frame = data_frame.rename(columns={'Priority': 'priority'})

    switch_mqtt = SwitchMQTT(host_address=_control_ws_host, host_port=_control_ws_port,
                             username=_control_ws_username, password=_control_ws_password,
                             session_id=session_id, client_id=api_inputs.data_feed_id, email=api_inputs.email_address,
                             project_id=api_inputs.api_project_id, installation_id=str(installation_id))

    is_connected = switch_mqtt.connect(timeout=timeout)

    if not is_connected:
        logger.info("Could not connect to MQTT Broker.")
        return 'Could not connect to MQTT Broker.', pandas.DataFrame()

    def process_paged_request(df, page_size: int = 20):
        paged_results = pandas.DataFrame()
        total_rows = len(df)
        num_pages = (total_rows + page_size - 1) // page_size

        for page_num in range(num_pages):
            start_idx = page_num * page_size
            end_idx = min((page_num + 1) * page_size, total_rows)

            # Get the data for the current page
            page_data = df.iloc[start_idx:end_idx]

            result = send_control(page_data)
            paged_results = pandas.concat([paged_results, result])

        return paged_results

    def send_control(page_data):
        retry_count = 0
        max_retries = 3
        success_results = pandas.DataFrame()
        missing_results = pandas.DataFrame()

        dataframe_to_control = page_data.copy()

        while retry_count < max_retries:
            success_response, missing_response = switch_mqtt.send_control_request(
                sensors=dataframe_to_control.to_dict(orient='records'))

            if not isinstance(success_response, pandas.DataFrame):
                logger.error(success_response)
                retry_count += 1
                time.sleep(1)
                continue

            if not success_response.empty:
                logger.info("Sensors that were successful in control request:")
                logger.info(success_response.to_string(index=False))
                success_results = pandas.concat(
                    [success_results, success_response])

            if not missing_response.empty:
                logger.error(
                    "Sensors that aren't successful in control request.")
                logger.info(missing_response.to_string(index=False))
                missing_results = pandas.concat(
                    [missing_results, missing_response])

            if missing_response.empty:
                break

            # Discount the successful control requests from the ones going for a retry
            if not success_response.empty:
                dataframe_to_control = dataframe_to_control[~dataframe_to_control['sensorId'].isin(
                    success_response['sensorId'])]

            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)

        if missing_results.empty:
            success_results['status'] = True
            success_results['writeStatus'] = 'Complete'
            control_result = success_results.copy()
        else:
            control_result = pandas.merge(page_data, missing_results, left_on='sensorId',
                                          right_on='sensorId', how='left', suffixes=('_df1', '_df2'))

            control_result['status'] = control_result['writeStatus'].isnull()

            columns_to_drop = ['controlValue_df2', 'duration_df2',
                               'priority_df2', 'defaultControlValue_df2']

            # Filter columns that exist in the dataframe
            existing_columns_to_drop = [
                col for col in columns_to_drop if col in control_result.columns]

            if existing_columns_to_drop:
                control_result.drop(
                    existing_columns_to_drop, axis=1, inplace=True)

            control_result['status'] = control_result['status'].fillna(True)

            control_result = control_result.rename(columns={
                'controlValue_df1': 'controlValue',
                'duration_df1': 'duration',
                'priority_df1': 'priority',
                'defaultControlValue_df1': 'defaultControlValue'
            })

        logger.info(control_result)
        return control_result

    control_results = process_paged_request(data_frame)

    switch_mqtt.disconnect()

    return control_results


def get_control_cache(api_inputs: ApiInputs, key: str, scope_id: str) -> pandas.DataFrame:
    """Gets Control Cache based on Portfolio.

    Parameters
    ----------
    api_inputs: ApiInputs
        Object returned by initialize() function.
    key: str
        Cache key
    scope_id: UUID
        UUID in relation to the scope that was set. Used as well when retrieving the data later on.
        For Task scope provide TaskId (self.id when calling from the driver)
        For DataFeed scope provide UUID4 for local testing.
            api_inputs.data_feed_id will be used when running in the cloud.
        For Portfolio scope, scope_id will be ignored and api_inputs.api_project_id will be used.

    Returns
    -------
    Dataframe
        Cache content
    """
    try:
        control_cache_res = get_cache(
            api_inputs=api_inputs, scope="Portfolio", key=key, scope_id=scope_id)

        if control_cache_res['success'] == True:
            cache_data = json.loads(control_cache_res['data'])
            df_from_records = pandas.DataFrame.from_records(
                cache_data)
            return df_from_records
        return pandas.DataFrame()
    except Exception as e:
        logger.error(
            f"An unexpected error occurred in getting Control cache: {e}")
        return pandas.DataFrame()


def set_control_cache(api_inputs: ApiInputs, key: str, scope_id: str, data: any):
    """Sets Control Cache based on Portfolio.

    Parameters
    ----------
    api_inputs: ApiInputs
        Object returned by initialize() function.
    key: str
        Cache key
    scope_id: UUID
        UUID in relation to the scope that was set. Used as well when retrieving the data later on.
        For Task scope provide TaskId (self.id when calling from the driver)
        For DataFeed scope provide UUID4 for local testing.
            api_inputs.data_feed_id will be used when running in the cloud.
        For Portfolio scope, scope_id will be ignored and api_inputs.api_project_id will be used.

    Returns
    -------
        N/A
    """

    try:
        return set_cache(api_inputs=api_inputs, scope="Portfolio", key=key, val=data, scope_id=scope_id)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred in setting Control cache: {e}")
        return pandas.DataFrame()


def add_control_component(name: str, column_with_object_installation_id: str, column_with_object_property_id: str, column_with_label: str, column_with_value: str, column_with_continue: str = None, column_with_default_value: str = None, timeout_in_seconds: int = 0, priority: int = 8):
    """Add Control Components similar to batching the dataframe with named columns.

    Parameters
    ----------
        name: str
            Name of the Control Component
        column_with_object_installation_i: str
            Column name for the InstallationId
        column_with_object_property_id (str):
            Column name for the ObjectPropertyId
        column_with_label (str):
            Column name for the Sensor Label
        column_with_value (str):
            Column name for the Control Value
        column_with_continue (str, optional):
            Column name for the Control Continue Value Defaults to None.
        column_with_default_value (str, optional):
            Column name for the Control Default Value Defaults to None.
        timeout_in_seconds (int, optional):
            Time until relinquish happens in seconds. Defaults to 0.
            Setting value to 0 means the control will not relinquish.
            If there's value > 0 then it will always relinquish control.
        priority (int, optional):
            Priority value for the control write command. Defaults to 8.

    Returns
    -------
        N/A
    """

    global _control_components

    # Validate required parameters
    if not name:
        raise ValueError("The 'name' parameter cannot be None or empty.")
    if not column_with_object_installation_id:
        raise ValueError(
            "The 'column_with_object_installation_id' parameter cannot be None or empty.")
    if not column_with_object_property_id:
        raise ValueError(
            "The 'column_with_object_property_id' parameter cannot be None or empty.")
    if not column_with_label:
        raise ValueError(
            "The 'column_with_label' parameter cannot be None or empty.")
    if not column_with_value:
        raise ValueError(
            "The 'column_with_value' parameter cannot be None or empty.")

    # Optional parameters can be None, so only check if they are not None and empty
    if column_with_continue is not None and column_with_continue == "":
        raise ValueError(
            "The 'column_with_continue' parameter cannot be an empty string.")
    if column_with_default_value is not None and column_with_default_value == "":
        raise ValueError(
            "The 'column_with_default_value' parameter cannot be an empty string.")

    # Validate timeout_in_seconds and priority
    if not isinstance(timeout_in_seconds, int) or timeout_in_seconds < 0:
        raise ValueError(
            "The 'timeout_in_seconds' parameter must be a non-negative integer.")
    if not isinstance(priority, int) or priority < 0:
        raise ValueError(
            "The 'priority' parameter must be a non-negative integer.")

    _control_components[name] = (
        column_with_object_installation_id,
        column_with_object_property_id,
        column_with_label,
        column_with_value,
        column_with_continue,
        column_with_default_value,
        timeout_in_seconds,
        priority)


def log_control_request(api_inputs: ApiInputs, df: pandas.DataFrame, session_id: uuid.UUID, installation_id: uuid.UUID):
    """Add Control Components similar to batching the dataframe with named columns.

    Parameters
    ----------
    api_inputs : ApiInputs
        Object returned by initialize() function.
    df : pandas.DataFrame
        List of Sensors for control request.
    session_id : uuid.UUID
        Session Id to reuse when communicating with IoT Endpoint and MQTT Broker
    installation_id : UUID:
        Installation Id

    Return
    ------
    Tuple : Status, Dataframe
        Status Code string, Data frame as sent
    """

    json_payload = {
        "sensors": df.to_dict(orient='records'),
        "email": api_inputs.email_address,
        "userid": api_inputs.user_id,
        "sessionId": str(session_id)
    }

    url = f"{_control_api_endpoint}/api/gateway/{str(installation_id)}/log-control-request"

    headers = api_inputs.api_headers.default

    logger.info("Sending Control Request to IoT API: POST %s", url)
    logger.info("Control Request Session Id: %s", str(session_id))
    logger.info("Control Request for User: %s=%s",
                api_inputs.email_address, api_inputs.user_id)

    response = requests.post(url, json=json_payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    response_object = json.loads(response.text)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.",
                     response.status_code, response.reason)
        logger.error(response_object[IOT_RESPONSE_ERROR])
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s',
                     response.request.url)
        return response_status, pandas.DataFrame()

    if not response_object[IOT_RESPONSE_SUCCESS]:
        logger.error(response_object[IOT_RESPONSE_ERROR])
        return response_object[IOT_RESPONSE_SUCCESS], pandas.DataFrame()

    logger.info('IoT API Control Request is Successful.')

    return response_status, df


def update_control_cache(api_inputs: ApiInputs, control_cache_key: str, control_cache_df: pandas.DataFrame, control_results_df: pandas.DataFrame):
    """Update control cache

    Parameters
    ----------
    api_inputs: ApiInputs
        Object returned by initialize() function.
    control_cache_key: str
        Cache key
    control_cache_df: pandas.DataFrame
        Dataframe from control cache as base.
    control_results_df: pandas.DataFrame
        Dataframe to add or remove from control_cache.

    Return
    ------
        N/A
    """

    df = control_results_df.copy()

    control_sensors_sent = df[
        (df[COL_CONTROL_STATUS] == ControlStatus.ControlSuccessful.value) |
        (df[COL_CONTROL_STATUS] == ControlStatus.ControlResent.value)]

    # Filter out the entries that are already in control_cache_df with the ones in control_sensors_sent that was sent
    new_entries = pandas.DataFrame()
    if control_cache_df.empty:
        new_entries = control_sensors_sent
    elif not control_sensors_sent.empty:
        new_entries = control_sensors_sent[~control_sensors_sent[COL_OBJECT_PROPERTY_ID].isin(
            control_cache_df[COL_OBJECT_PROPERTY_ID])]

    if not new_entries.empty:
        new_entries.drop(new_entries.columns.difference(
            [COL_OBJECT_PROPERTY_ID]), axis=1, inplace=True)
        control_cache_df = pandas.concat(
            [control_cache_df, new_entries], ignore_index=True)

    # Get Sensors with Control Status of NotSentToService, these are the sensors candidate for Relinquish
    control_sensors_for_relinquish = df[
        df[COL_CONTROL_STATUS] == ControlStatus.NotSentToService.value]

    if not control_cache_df.empty:
        # We Remove the ones for relinquish in control_cache_df
        if not control_sensors_for_relinquish.empty:
            sensors_to_relinquish = control_sensors_for_relinquish[
                COL_OBJECT_PROPERTY_ID] if not control_sensors_for_relinquish.empty else []
            control_cache_df = control_cache_df[~control_cache_df[COL_OBJECT_PROPERTY_ID].isin(
                sensors_to_relinquish)]

    df_cache_cleaned = control_cache_df[control_cache_df[COL_OBJECT_PROPERTY_ID].notna() & (
        control_cache_df[COL_OBJECT_PROPERTY_ID] != '')]

    logger.info('Set Cache:')
    logger.info(df_cache_cleaned)
    set_control_cache(api_inputs=api_inputs, key=control_cache_key,
                      scope_id=api_inputs.api_project_id, data=df_cache_cleaned.to_dict(orient='records'))


def format_control_payload_df(df: pandas.DataFrame, required_columns: List[str], has_priority: bool) -> pandas.DataFrame:
    """ Formats control request payload

    Parameters:
    ----------
        df: pandas.DataFrame
            Dataframe to turn into request payload.
        required_columns: List[str]
            List of required columns for request payload.
        has_priority: bool
            Flag if the DataFrame has Priority column

    Returns:
    --------
    Dataframe
        Formatted control request payload
    """
    if COL_CONTROL_DEFAULT_CONTROL_VALUE in df.columns:
        required_columns.append(COL_CONTROL_DEFAULT_CONTROL_VALUE)

    if has_priority:
        required_columns.append(COL_CONTROL_PRIORITY)

    df.drop(df.columns.difference(
        required_columns), axis=1, inplace=True)

    df = df.rename(columns={COL_OBJECT_PROPERTY_ID: 'sensorId',
                            COL_CONTROL_VALUE: 'controlValue',
                            COL_CONTROL_TTL: 'duration',
                            COL_CONTROL_DEFAULT_CONTROL_VALUE: 'defaultControlValue'})

    if has_priority:
        if not COL_CONTROL_PRIORITY in df:
            logger.error(
                f"has_priority is set to True, but the dataframe does not have the column 'Priority'.")
        else:
            df = df.rename(
                columns={COL_CONTROL_PRIORITY: 'priority'})

    return df


def format_acknowledgement_payload_df(df: pandas.DataFrame, required_columns: List[str], has_priority: bool) -> pandas.DataFrame:
    """ Formats acknowledgement request payload

    Parameters
    ----------
        df: pandas.DataFrame
            Dataframe to turn into request payload.
        required_columns: List[str]
            List of required columns for request payload.
        has_priority: bool
            Flag if the DataFrame has Priority column

    Returns:
    --------
    Dataframe
        Formatted acknowledgement request payload
    """
    if has_priority:
        required_columns.append(COL_CONTROL_PRIORITY)

    df.drop(df.columns.difference(
        required_columns), axis=1, inplace=True)

    df = df.rename(columns={COL_OBJECT_PROPERTY_ID: 'id',
                            COL_CONTROL_VALUE: 'v',
                            COL_CONTROL_TTL: 'dsecs'})

    if has_priority:
        if not COL_CONTROL_PRIORITY in df.columns:
            logger.error(
                f"has_priority is set to True, but the dataframe does not have the column 'Priority'.")
        else:
            df = df.rename(
                columns={COL_CONTROL_PRIORITY: 'p'})

    return df


def rename_control_results_column_df(result_df: pandas.DataFrame) -> pandas.DataFrame:
    """Renames control results columns

    Parameters
    ----------
        result_df: pandas.DataFrame
            Dataframe to modify column names to appropriate ones.

    Returns
    -------
    Dataframe
        Renamed dataframe columns
    """
    result_df = result_df.rename(
        columns={
            'sensorId': COL_OBJECT_PROPERTY_ID,
            'status': COL_CONTROL_STATUS,
            'writeStatus': 'WriteStatus',
            'controlValue': COL_CONTROL_VALUE,
            'duration': COL_CONTROL_TTL})

    return result_df
