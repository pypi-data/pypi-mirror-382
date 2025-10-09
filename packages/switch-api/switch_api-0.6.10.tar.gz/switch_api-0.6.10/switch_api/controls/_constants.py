# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module containing the constants referenced by methods and functions defined in the controls module. This module
is not directly referenced by end users.
"""

IOT_RESPONSE_SUCCESS = 'success'
IOT_RESPONSE_ERROR = 'error'

WS_DEFAULT_PORT = 443
WS_MQTT_CONNECTION_TIMEOUT = 180
WS_MQTT_DEFAULT_MAX_TIMEOUT = 30
WS_MQTT_WAIT_TIME_INTERVAL = 0.1
WS_MQTT_MESSAGE_WAIT_TIME_INTERVAL = 0.1

CONTROL_REQUEST_ACTION_ACK = 'control-request-ack'
CONTROL_REQUEST_ACTION_RESULT = 'control-result'

COL_CONTROL_DEFAULT_CONTROL_VALUE = "DefaultControlValue"
COL_OBJECT_PROPERTY_ID = "ObjectPropertyId"
COL_CONTROL_NAME = "ControlName"
COL_CONTROL_LABEL = "Label"
COL_CONTROL_VALUE = "Value"
COL_CONTROL_CONTINUE_VALUE = "ContinueValue"
COL_CONTROL_TTL = "TTL"
COL_CONTROL_PRIORITY = "Priority"
COL_CONTROL_STATUS = "ControlStatus"
COL_CONTROL_INSTALLATION_ID = "InstallationId"
COL_CONTROL_TIMESTAMP = "Timestamp"
COL_CONTROL_TIMESTAMP_LOCAL = "TimestampLocal"
COL_CONTROL_PIVOTKEY = "PivotKey"
COL_CONTROL_INFOCOLUMNS = "InfoColumns"
COL_CONTROL_IS_EXTENDED_CONTROL = "IsExtendControl"
COL_CONTROL_EXISTS_IN_CONTROL_CACHE = "ExistsInControlCache"
