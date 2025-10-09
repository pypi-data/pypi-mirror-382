# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for providing support for extensions to tasks.
Allows sharing of code between tasks.
"""

from .extensions import (provide, get_extension_fields, replace_extension_imports, 
                         replace_extensions_imports, tokenize_extension_imports)

from .field_meta import FieldMeta

from .helpers import find_cycles_by_field_type, convert_to_serializeable_fields, has_extensions_support

from .pipeline import ExtensionTask

__all__ = ['ExtensionTask', 'provide', 'get_extension_fields', 'replace_extension_imports', 
           'replace_extensions_imports', 'tokenize_extension_imports', 'find_cycles_by_field_type',
           'convert_to_serializeable_fields', 'has_extensions_support', 'FieldMeta']
