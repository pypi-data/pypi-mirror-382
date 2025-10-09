import inspect
from typing import List

HasExtensionClsAttributeName = '__has_sw_extension_support__'
"""The name of the attribute that is added to a class that has extensions."""

def get_code(cls):
    """
    Get the code used to create the class.

    (Code was taken from sw.pipeline.Automation._get_task_code function)
    
    Parameters
    ----------
    task : Task
        The custom driver class created from the Abstract Base Class `Task`.

    Returns
    -------
    driver_code : str
        The code used to create the `task`

    """
    task_type = type(cls)
    task_code = ''
    parent_module = inspect.getmodule(task_type)
    for codeLine in inspect.getsource(parent_module).split('\n'):
        task_code += codeLine + '\n'

    task_code += '\n'
    task_code += inspect.getsource(task_type)
    task_code += ''
    task_code += 'task = ' + task_type.__name__ + '()'

    return task_code

def has_extensions_support(cls):
    """Check if the class has extensions.

    Parameters
    ----------
    cls : type
        The class to check for extensions.

    Returns
    -------
    bool
        True if the class has extensions, otherwise False.

    """

    try:
        # extensions are not always part of the cls.__dict__ so we're testing by trying to access it
        getattr(cls, HasExtensionClsAttributeName)
        return True
    except AttributeError:
        return False

def has_annotations(cls):
    """Check if the class has type annotations.

    Parameters
    ----------
    cls : type
        The class to check for type annotations.

    Returns
    -------
    bool
        True if the class has type annotations, otherwise False.

    """

    try:
        # annotations are not always part of the cls.__dict__ so we're testing by trying to access it
        getattr(cls, '__annotations__')
        return True
    except AttributeError:
        return False


def convert_to_serializeable_fields(fields):
    """
    Convert a list of FieldMeta objects to a list of dictionaries.

    Parameters
    ----------

    fields : List[FieldMeta]

    Returns
    -------
    
    List[dict]
        A list of dictionaries containing the fields.
    """

    serializeable_fields = []
    for field in fields:
        serializeable_fields.append(field.to_dict())
    return serializeable_fields


def find_cycles_by_field_type(fields: List[dict]):
    """
    Find cycles in a list of objects that contain a field_type key and a nested_extensions key.
    """

    cycles = []
    visited = set()
    def dfs(obj, ancestors, path):
        if obj["field_type"] in ancestors:
            cycles.append(path + [obj["field_type"]])
        if obj["field_type"] in visited:
            return
        visited.add(obj["field_type"])
        for child in obj["nested_extensions"]:
            dfs(child, ancestors + [obj["field_type"]], path + [obj["field_type"]])
    for obj in fields:
        dfs(obj, [], [])
    return cycles