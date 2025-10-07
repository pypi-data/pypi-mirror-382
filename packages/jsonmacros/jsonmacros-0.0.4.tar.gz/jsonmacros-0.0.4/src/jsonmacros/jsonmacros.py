from typing import Any
import json
import re
import os
import math
import numpy as np
import enum
import jsonschema
import random


class SimpleMacro:
    def __init__(self, name: str, body: Any):
        self.name: str = name
        self.body: Any = body


class ParameterizedMacro:
    def __init__(self, name: str, params: set[str], body: Any):
        self.name: str = name
        self.params: set[str] = params
        self.body: Any = body


class MacroNamespace:
    def __init__(self, macros: dict[str, Any]):
        for k, v in macros.items():
            setattr(self, k, v)


class JsonMacroFile:
    def __init__(self, pathname: str):
        self.name: str  # Name of the macro file
        self.include: list[str]  # List of valid file paths
        self.parameterized_macros: dict[
            str, ParameterizedMacro
        ]  # Parameterized macro definitions
        self.simple_macros: dict[str, SimpleMacro]  # Simple macro definitions
        self.properties: dict[str, Any]  # Other properties in the file

        self.pathname: str = os.path.abspath(pathname)
        self.name = os.path.splitext(os.path.basename(pathname))[0]

        data: dict[str, Any] = {}

        if not os.path.isfile(pathname):
            raise FileNotFoundError(f"Macro file not found: {pathname}")

        with open(pathname, "r") as f:
            # Validate against schema
            schema_path = os.path.join(
                os.path.dirname(__file__), "json_macro_schema.json"
            )
            data = json.load(f)
            with open(schema_path, "r") as schema_file:
                schema = json.load(schema_file)
                try:
                    jsonschema.validate(instance=data, schema=schema)
                except Exception as e:
                    raise ValueError(f"Invalid macro file {pathname}: {e}")

        self.include = data.get("$include", [])
        self.parameterized_macros = {}
        self.simple_macros = {}
        for macro_data in data.get("$macros", []):
            name = macro_data.get("name", "")
            if len(name) == 0:
                raise ValueError(
                    f"Invalid or missing 'name' in macro definition in file: {pathname}"
                )
            params = set(macro_data.get("params", []))
            body = macro_data.get("body", None)
            if name in self.parameterized_macros or name in self.simple_macros:
                raise ValueError(
                    f"Duplicate macro definition: {name} in file: {pathname}"
                )
            if not params:
                self.simple_macros[name] = SimpleMacro(name, body)
            else:
                self.parameterized_macros[name] = ParameterizedMacro(name, params, body)

        self.properties = {
            k: v for k, v in data.items() if k not in {"$name", "$include", "$macros"}
        }


class JsonMergeStrategy(enum.Enum):
    OVERRIDE = "override"  # Later definitions override earlier ones
    ERROR = "error"  # Raise an error on duplicate definitions
    MERGE = "merge"  # Merge dictionaries, concatenate lists, override on conflicts
    MERGE_WITH_ERROR = (
        "merge_with_error"  # Merge dictionaries, concatenate lists, error on conflicts
    )


class JsonMacroProcessor:
    MODULES = {
        "math": math,
        "np": np,
        "random": random,
    }

    def __init__(
        self,
        include_dirs: list[str] = [],
        merge_strategy: JsonMergeStrategy = JsonMergeStrategy.ERROR,
    ):
        self.macro_files: dict[str, JsonMacroFile] = {}
        self.include_dirs: list[str] = []
        self.parameterized_macros: dict[str, ParameterizedMacro] = {}
        self.simple_macros: dict[str, Any] = {}
        self.macro_namespaces: dict[str, MacroNamespace] = {}
        self.properties: dict[str, Any] = {}
        self.merge_strategy = merge_strategy
        self.macro_pattern = re.compile(r"\$\{.*\}")
        self.include_dirs = [os.path.abspath(d) for d in include_dirs]

    def process_file(self, pathname: str):
        if os.path.abspath(pathname) in self.macro_files:
            return  # Already loaded

        macro_file = JsonMacroFile(pathname)
        self.macro_files[macro_file.pathname] = macro_file

        # Resolve includes first (DFS)
        for include_path in macro_file.include:
            found = False
            for dir in [os.path.dirname(macro_file.pathname)] + self.include_dirs:
                full_path = os.path.abspath(os.path.join(dir, include_path))
                if os.path.isfile(full_path):
                    self.process_file(full_path)
                    found = True
                    break
            if not found:
                raise FileNotFoundError(
                    f"Included macro file '{include_path}' not found in include paths."
                )

        # Add simple macros from this file
        for macro in macro_file.simple_macros.values():
            name = macro_file.name + "." + macro.name
            if name in self.simple_macros:
                raise ValueError(f"Duplicate macro definition: {name}")
            # If the body is a simple macro, resolve it now
            if self._is_simple_macro(macro.body):
                macro.body = self._resolve_simple_macro(macro_file.pathname, macro.body)
            # If the body is a parameterized macro, resolve it now
            elif self._is_parameterized_macro(macro.body):
                macro.body = self._resolve_parameterized_macro(
                    macro_file.pathname, macro.body
                )
            self.simple_macros[name] = macro.body

        # Add parameterized macros from this file
        for macro in macro_file.parameterized_macros.values():
            name = macro_file.name + "." + macro.name
            if name in self.parameterized_macros:
                raise ValueError(f"Duplicate macro definition: {name}")
            # If the body is a simple macro, resolve it now
            if self._is_simple_macro(macro.body):
                macro.body = self._resolve_simple_macro(macro_file.pathname, macro.body)
            # If the body is a parameterized macro, resolve it now
            elif self._is_parameterized_macro(macro.body):
                macro.body = self._resolve_parameterized_macro(
                    macro_file.pathname, macro.body
                )
            self.parameterized_macros[name] = macro

        # Build macro namespace for this file
        self.macro_namespaces[macro_file.name] = MacroNamespace(
            {k: v.body for k, v in macro_file.simple_macros.items()}
        )

        # Resolve properties from this file
        resolved = self._resolve(macro_file.pathname, macro_file.properties)

        # Merge properties based on the selected strategy
        self.properties = JsonMacroProcessor._merge_properties(
            self.properties, resolved, self.merge_strategy
        )

        # Return the resolved properties
        return self.properties

    @staticmethod
    def _merge_properties(
        base: dict[str, Any], new: dict[str, Any], merge_strategy: JsonMergeStrategy
    ) -> dict[str, Any]:
        if base == {}:
            return new

        if merge_strategy == JsonMergeStrategy.OVERRIDE:
            merged = base.copy()
            merged.update(new)
            return merged
        elif merge_strategy == JsonMergeStrategy.ERROR:
            for key in new:
                if key in base:
                    raise ValueError(f"Duplicate property definition: {key}")
            merged = base.copy()
            merged.update(new)
            return merged
        elif (
            merge_strategy == JsonMergeStrategy.MERGE_WITH_ERROR
            or merge_strategy == JsonMergeStrategy.MERGE
        ):
            merged = base.copy()
            for key, value in new.items():
                if key in merged:
                    # If both values are dictionaries, merge them recursively
                    if isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key] = JsonMacroProcessor._merge_properties(
                            merged[key], value, merge_strategy
                        )
                    # If both values are lists, concatenate them
                    elif isinstance(merged[key], list) and isinstance(value, list):
                        merged[key] = merged[key] + value
                    # If values are of different types or not both dict/list, handle based on strategy
                    elif merge_strategy == JsonMergeStrategy.MERGE_WITH_ERROR:
                        raise ValueError(
                            f"Conflict at key '{key}': cannot merge {type(merged[key])} with {type(value)}"
                        )
                    else:  # OVERRIDE behavior for conflicts
                        merged[key] = value
                else:
                    merged[key] = value
            return merged
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")

    def _is_parameterized_macro(self, value: Any) -> bool:
        return isinstance(value, dict) and "$macro" in value and "$params" in value

    def _is_simple_macro(self, value: Any) -> bool:
        return isinstance(value, str) and bool(self.macro_pattern.search(value))

    def _is_conditional_macro(self, value: Any) -> bool:
        return isinstance(value, dict) and "$if" in value and "$then" in value

    def _resolve_parameterized_macro(
        self, name: str, value: dict[str, Any], local: dict[str, Any] = {}
    ) -> Any:
        macro_name = value["$macro"]
        params = value["$params"]

        # Get the macro definition
        macro: ParameterizedMacro
        if macro_name in self.parameterized_macros:
            # See if it using the global name
            macro = self.parameterized_macros[macro_name]
        elif macro_name in self.macro_files[name].parameterized_macros:
            # See if it using the local name
            macro = self.macro_files[name].parameterized_macros[macro_name]
        else:
            # If the macro cannot be found, raise an error
            raise ValueError(f"Undefined macro: {macro_name}")

        # Check for missing parameters
        missing_params = macro.params - params.keys()
        if missing_params:
            raise ValueError(
                f"Missing parameters {missing_params} for macro '{macro_name}'"
            )

        # Resolve parameters
        params = self._resolve(name, params, local)

        # Resolve the macro body with the parameters as local variables
        return self._resolve(name, macro.body, params)

    def _resolve_simple_macro(
        self, name: str, value: str, local: dict[str, Any] = {}
    ) -> Any:
        matches = self.macro_pattern.findall(value)
        if matches:
            # Build a lookup table to find macros
            lookup: dict[str, Any] = {
                # Include predefined modules
                **self.MODULES,
                # Include macro namespaces for qualified access
                **self.macro_namespaces,
                # Include global simple macros
                **self.simple_macros,
                # Include local simple macros
                **{k: v.body for k, v in self.macro_files[name].simple_macros.items()},
                # Include local parameters
                **local,
            }

            # Replace any occurance of ${...} with the corresponding value in the lookup table
            # If the expression does not exist in the lookup table, remove ${}
            for match in matches:
                match_without_braces = match[2:-1].strip()
                if match_without_braces in lookup:
                    value = value.replace(match, str(lookup[match_without_braces]))
                else:
                    value = value.replace(match, str(match_without_braces))

            # Recurse to ensure that nested expressions are resolved
            value = self._resolve_simple_macro(name, value, local)

            # Evaluate any math
            try:
                evaluated = eval(value, lookup)
                if evaluated is not None:
                    return evaluated
            except Exception as e:
                return value
        else:
            # If there are no matches, then we have resolved all macros
            return value

    def _resolve_conditional_macro(
        self, name: str, value: dict[str, Any], local: dict[str, Any] = {}
    ) -> Any:
        condition = value["$if"]
        then_branch = value["$then"]
        else_branch = value.get("$else", None)

        # Evaluate the condition
        condition_result = self._resolve_simple_macro(name, condition, local)
        if isinstance(condition_result, str):
            condition_result = bool(condition_result)
        elif isinstance(condition_result, (int, float)):
            condition_result = condition_result != 0
        elif not isinstance(condition_result, bool):
            raise ValueError(f"Condition '{condition}' did not evaluate to a boolean.")

        # Resolve the appropriate branch
        if condition_result:
            return self._resolve(name, then_branch, local)
        elif else_branch is not None:
            return self._resolve(name, else_branch, local)
        else:
            return None

    def _resolve(self, name: str, value: Any, local: dict[str, Any] = {}) -> Any:
        if self._is_parameterized_macro(value):
            return self._resolve_parameterized_macro(name, value, local)
        elif self._is_simple_macro(value):
            return self._resolve_simple_macro(name, value, local)
        elif self._is_conditional_macro(value):
            return self._resolve_conditional_macro(name, value, local)
        elif isinstance(value, list):
            return [self._resolve(name, item, local) for item in value]
        elif isinstance(value, dict):
            return {k: self._resolve(name, v, local) for k, v in value.items()}
        else:
            return value


if __name__ == "__main__":
    dir = "examples/"
    processor = JsonMacroProcessor(merge_strategy=JsonMergeStrategy.OVERRIDE)
    # For each .json file in dir, process it
    for filename in os.listdir(dir):
        if filename.endswith(".json"):
            macro_file = os.path.join(dir, filename)
            processor.process_file(macro_file)
    print(json.dumps(processor.properties, indent=4))
