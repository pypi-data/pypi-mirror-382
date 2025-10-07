from . import _native as ccdexplorer_schema_parser
import json


class Schema:
    def __init__(self, source, version=None):
        """Construct a new schema by extracting it from a module source. The
        module source can be either provided as a serialized versioned module,
        or a pair of a Wasm module together with a version (which can be either
        0 or 1). If the optional `version` argument is supplied then this
        assumes that the `source` is only the Wasm module.

        """
        if version is not None:
            try:
                self.schema = ccdexplorer_schema_parser.extract_schema_pair_ffi(
                    version, source
                )
            except ValueError:
                self.schema = None
        else:
            try:
                self.schema = ccdexplorer_schema_parser.extract_schema_ffi(source)
            except ValueError:
                self.schema = None

    def event_to_json(self, contractName, eventData):
        try:
            response = ccdexplorer_schema_parser.parse_event_ffi(
                self.schema, contractName, eventData
            )
            return json.loads(response)
        except TypeError:
            return None

    def parameter_to_json(self, contractName, functionName, parameterData):
        try:
            response = ccdexplorer_schema_parser.parse_parameter_ffi(
                self.schema, contractName, functionName, parameterData
            )
            return json.loads(response)
        except TypeError:
            return None

    def return_value_to_json(self, contractName, functionName, returnValueData):
        response = ccdexplorer_schema_parser.parse_return_value_ffi(
            self.schema, contractName, functionName, returnValueData
        )
        return json.loads(response)

    def extract_schema(self):
        try:
            response = ccdexplorer_schema_parser.extract_schema_template_ffi(
                self.schema
            )
            return response
        except ValueError:
            return None

    def extract_init_error_schema(self, contractName: str):
        try:
            response = ccdexplorer_schema_parser.extract_init_error_schema_template_ffi(
                self.schema, contractName
            )
            return response
        except ValueError:
            return None

    def extract_init_param_schema(self, contractName: str):
        try:
            response = ccdexplorer_schema_parser.extract_init_param_schema_template_ffi(
                self.schema, contractName
            )
            return response
        except ValueError:
            return None

    def extract_receive_error_schema(self, contractName: str, functionName: str):
        try:
            response = (
                ccdexplorer_schema_parser.extract_receive_error_schema_template_ffi(
                    self.schema, contractName, functionName
                )
            )
            return response
        except ValueError:
            return None

    def extract_receive_param_schema(self, contractName: str, functionName: str):
        try:
            response = (
                ccdexplorer_schema_parser.extract_receive_param_schema_template_ffi(
                    self.schema, contractName, functionName
                )
            )
            return response
        except ValueError:
            return None

    def extract_receive_return_value_schema(self, contractName: str, functionName: str):
        try:
            response = ccdexplorer_schema_parser.extract_receive_return_value_schema_template_ffi(
                self.schema, contractName, functionName
            )
            return response
        except ValueError:
            return None

    def extract_event_schema(self, contractName: str):
        try:
            response = ccdexplorer_schema_parser.extract_event_schema_template_ffi(
                self.schema, contractName
            )
            return response
        except ValueError:
            return None
