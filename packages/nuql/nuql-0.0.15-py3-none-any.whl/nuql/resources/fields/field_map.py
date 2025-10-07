__all__ = ['create_field_map', 'get_field_types']

import inspect
from typing import Dict, List, Type, Any, Callable

import nuql
from nuql import resources, types


def create_field_map(
        fields: Dict[str, 'types.FieldConfig'],
        parent: 'resources.Table',
        field_types: List[Type['types.FieldType']] | None = None
) -> Dict[str, 'types.FieldType']:
    """
    Generates a dict of table field instances for the serialisation process.

    :arg fields: Dict of field configurations.
    :arg parent: Parent Table instance.
    :param field_types: Additional field types that are defined outside the library.
    :return: Field map dict.
    """
    all_field_types = get_field_types(field_types)

    output = {}
    callbacks = []

    def init_callback(fn: Callable[[Dict[str, Any]], None]) -> None:
        callbacks.append(fn)

    for key, config in fields.items():
        if config['type'] not in all_field_types:
            raise nuql.NuqlError(
                code='InvalidFieldType',
                message=f'Field type \'{config["type"]}\' is not defined.'
            )

        field_type = all_field_types[config['type']]

        output[key] = field_type(key, config, parent, init_callback=init_callback)

    # Run any applicable callbacks on the output
    for callback in callbacks:
        callback(output)

    return output


def get_field_types(field_types: List[Type['types.FieldType']] | None = None) -> Dict[str, Type['types.FieldType']]:
    """
    Dynamically generates a dict of all available field types.

    :param field_types: Additional field types that are defined outside the library.
    :return: Field type dict.
    """
    from nuql import fields as builtin_fields

    if not isinstance(field_types, list):
        field_types = []

    output = {}

    def is_valid(_obj: Any) -> bool:
        """Check the provided object is a valid field type."""
        if not inspect.isclass(_obj):
            return False

        if not issubclass(_obj, resources.FieldBase):
            return False

        return True

    # Import built-in field types
    for name in dir(builtin_fields):
        obj = getattr(builtin_fields, name)

        if is_valid(obj):
            output[obj.type] = obj

    # Import custom-defined field types
    for field_type in field_types:
        if is_valid(field_type):
            output[field_type.type] = field_type

    return output
