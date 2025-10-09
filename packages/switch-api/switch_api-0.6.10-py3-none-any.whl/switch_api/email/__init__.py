# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for sending emails to active users within a Portfolio in the Switch Platform.
"""

from .email_sender import send_email

__all__ = ['send_email']