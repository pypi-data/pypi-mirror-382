# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Module providing support for extensions to the Task classes."""

from typing import List, Tuple, Union, get_type_hints

from .pipeline import ExtensionTask
from .field_meta import FieldMeta
from .helpers import get_code, convert_to_serializeable_fields, find_cycles_by_field_type, has_annotations, HasExtensionClsAttributeName


def provide(field: Union[str, List[str]]):
    """Decorator used to provide an extension to the Task class 
    by setting an attribute on the class matching field

    Parameters
    ----------
    field: str | list
        The field on the class to inject the extension into.

    Returns
    -------
    function
        The decorator function.

    """

    def decorator(cls):
        if not cls or not isinstance(cls, type):
            raise TypeError("The provided class must be a valid class")
        
        if issubclass(cls, ExtensionTask):
            raise TypeError(f"""
                Extensions cannot be provided to other extensions at this time. 
                Please check for nested extensions in class '{cls.__name__}'.
                Nested Extensions are extensions which depend on other extensions.
                """)

        # Load the module from the local file system
        type_hints = get_type_hints(cls)
        
        if isinstance(field, str):
            __provide(cls, type_hints, field)
        elif isinstance(field, list):
            field_list = filter(lambda x: x and isinstance(x, str), field)
            for f in field_list:
                __provide(cls, type_hints, f)

        return cls

    def __provide(cls, type_hints: dict[str, any], inner_field: str):
        if inner_field not in type_hints:
            raise TypeError(f"Provided field '{inner_field}' must exist as a field on the class {cls.__name__}")
        
        module_type = type_hints[inner_field]

        if not issubclass(module_type, ExtensionTask):
            raise TypeError(f"Provided field '{inner_field}' must have a return type that inherits from ExtensionTask")

        module = module_type()

        # Set the module as an attribute of the class
        setattr(cls, inner_field, module)

        # Set attribute on the class to identify that it has extensions
        if not hasattr(cls, HasExtensionClsAttributeName):
            setattr(cls, HasExtensionClsAttributeName, True)

    return decorator


def get_extension_fields(cls):
    """Get a list of the injected fields on the class.
    
    Parameters
    ----------
    cls : type
        The class to get the injected fields from.

    Returns
    -------
    list
        A list of the injected fields on the class.

    """

    injected_fields: list[FieldMeta] = []

    if not has_annotations(cls): # Check if the class has type annotations
        return injected_fields

    for field_name in cls.__annotations__:
        if hasattr(cls, field_name):
            field_type = cls.__annotations__[field_name]

            if issubclass(field_type, ExtensionTask):

                # Add variable called version that returns the version of the injected module
                field = getattr(cls, field_name)
                injected_fields.append(FieldMeta(
                    field_name=field_name,
                    field_type=field_type,
                    extension_name=field_type.__name__, # Extension class name
                    id=getattr(field, "id"),
                    version=getattr(field, "version"),
                    description=getattr(field, "description"),
                    author=getattr(field, "author"),
                    nested_extensions=get_extension_fields(field_type)
                ))

    return injected_fields


def replace_extension_imports(task: ExtensionTask, replacements: List[Tuple[str, str]]) -> str:
    """
    Replace the import statements for the injected extensions given replacements.

    Parameters
    ----------

    task : ExtensionTask

    replacements : List[Tuple[str, str]]
        A list of tuples containing the old path and the new path.
        Example: 
            replacements = [
                ('my_extension.MyExtension', 'my_extension_second')
            ]

    Returns
    -------
    str
        The code of the task with the replaced import statements.
    """


    # Get a list of all the injected fields in the code
    extension_fields = get_extension_fields(task)

    serializeable_fields = convert_to_serializeable_fields(extension_fields)

    cycles = find_cycles_by_field_type(serializeable_fields)

    if cycles:
        raise Exception(f"Found cycles in the extension dependencies: {cycles}")

    # Get the code of the task
    code = get_code(task)

    # Loop through all the replacements and check if any of them match the type of an injected field
    for old_path, new_path in replacements:
        for field in extension_fields:
            field_type = field.field_type
            if field_type.__module__ == old_path:
                # Replace the import statement with the new path
                code = code.replace(f"from {field_type.__module__}", f"from {new_path}")

    return code

def replace_extensions_imports(task: ExtensionTask, extensions_dir: str = 'extensions') -> str:
    """
    Replaces all extensions import statements to the format of <extensions_dir>.<extension_name>

    For example:
        from extensions.SimpleExtension import SimpleExtension

    Parameters
    ----------

    task : ExtensionTask

    extensions_dir : str

    Returns
    -------
    str
        The code of the task with the replaced import statements.
    """


    # Get a list of all the injected fields in the code
    extension_fields = get_extension_fields(task)

    serializeable_fields = convert_to_serializeable_fields(extension_fields)

    cycles = find_cycles_by_field_type(serializeable_fields)

    if cycles:
        raise Exception(f"Found cycles in the extension dependencies: {cycles}")

    replacements = []

    for field in extension_fields:
        field_type = field.field_type

        replacements.append((field_type.__module__, extensions_dir + '.' + field_type.__qualname__))

    return replace_extension_imports(task, replacements)

def tokenize_extension_imports(task: ExtensionTask) -> str:
    """
    Replace the import statements for the injected extensions with tokens to be replaced later.

    Parameters
    ----------

    task : ExtensionTask

    extensions_dir : str

    Returns
    -------
    str
        The code of the task with the tokenized import statements.
    """


    # Get a list of all the injected fields in the code
    injected_fields = get_extension_fields(task)

    # Get the code of the task
    code = get_code(task)

    # Loop through all the replacements and check if any of them match the type of an injected field
    for field in injected_fields:
        field_type = field.field_type

        # Replace the import statement with the new path
        code = code.replace(f"from {field_type.__module__} import {field_type.__qualname__}",
                            f"from {{sw_extensions_base_dir}}.{field_type.__qualname__} import {field_type.__qualname__}")

    return code
