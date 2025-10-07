from typing import Dict, Any, List

import jsonschema
from cirro_api_client.v1.models import FormSchema


def _get_fields_in_schema(schema: Dict, parent_path='') -> List['Parameter']:
    # This breaks for more advanced json schema usages such as the if/then
    fields = []

    for [field_key, field_spec] in schema.items():
        field_path = field_key if parent_path == '' else f'{parent_path}.{field_key}'
        field = Parameter(field_key, field_spec, field_path)
        fields.append(field)

        if 'properties' in field_spec:
            fields.extend(_get_fields_in_schema(field_spec['properties'], field_path))

    return fields


class ParameterSpecification:
    """
    Used to describe parameters used in a process (uses JSONSchema)
    """
    def __init__(self, form_schema: FormSchema):
        self._form_spec_raw: Dict = form_schema.form.additional_properties
        self._form_spec_ui: Dict = form_schema.ui.additional_properties
        self.form_spec = _get_fields_in_schema(self._form_spec_raw.get('properties') or {})

    @property
    def form_spec_json(self) -> dict:
        """
        Returns the JSON schema of the form specification
        """
        return self._form_spec_raw

    def validate_params(self, params: Dict):
        """
        Validates that the given parameters conforms to the specification
        """
        try:
            jsonschema.validate(instance=params, schema=self._form_spec_raw)
        except jsonschema.ValidationError as e:
            raise RuntimeError(f'Parameter at {e.json_path} error: {e.message}') from e

    def print(self):
        """
        Prints out a user-friendly view of the parameters
        """
        print("Parameters:")
        for field in self.form_spec:
            tab_prefix = '\t' * (field.path.count('.') + 1)
            print(tab_prefix + str(field))


class Parameter:
    def __init__(self, key: str, spec: Dict[str, Any], path: str):
        self.spec = spec
        self.key = key
        self.path = path

    @property
    def is_group(self):
        return self.spec.get('type') == 'object'

    def __str__(self):
        display_value = ''
        additional_data = ''

        if self.spec.get('title'):
            display_value += f'{self.spec.get("title")}'
            additional_data += f'key={self.key}, '
        else:
            display_value += self.key

        for prop in ['default', 'type', 'enum', 'description']:
            if prop_value := self.spec.get(prop):
                additional_data += f'{prop}={prop_value}, '

        if additional_data and not self.is_group:
            display_value += f' ({additional_data.rstrip(", ")})'

        if self.is_group:
            display_value += ' (Group)'
        return display_value
