# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum


class ControlStatus(Enum):
    NoControlRequired = 0
    ControlSuccessful = 1
    ControlFailed = 2
    NotSentToService = 3
    ControlResent = 4
