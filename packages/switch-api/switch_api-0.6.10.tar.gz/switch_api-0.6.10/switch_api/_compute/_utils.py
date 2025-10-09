# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for compute utility methods
"""
import uuid


def safe_uuid(value: str, default: uuid.UUID = uuid.UUID(int=0)) -> uuid.UUID:
    try:
        return uuid.UUID(value) if value else default
    except ValueError:
        return default
