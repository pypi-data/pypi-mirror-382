# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for sending control request of sensors.
"""

from .controls import submit_control, set_control_variables, submit_control_continue, add_control_component

__all__ = ['submit_control', 'set_control_variables',
           'submit_control_continue', 'add_control_component']
