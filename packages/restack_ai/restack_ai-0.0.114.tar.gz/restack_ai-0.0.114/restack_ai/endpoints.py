import inspect
from dataclasses import is_dataclass
from typing import Any

from msgspec import json
from pydantic import BaseModel


def _apply_namespace_to_schema(
    schema: dict[str, Any],
    namespace_prefix: str,
) -> dict[str, Any]:
    """Apply namespace prefix to $defs and update all $ref references."""
    if not namespace_prefix or "$defs" not in schema:
        return schema

    namespaced_defs = {}
    original_defs = schema["$defs"]

    # Create mapping of old refs to new refs
    ref_mapping = {}
    for def_name in original_defs:
        new_name = f"{namespace_prefix}_{def_name}"
        ref_mapping[f"#/$defs/{def_name}"] = f"#/$defs/{new_name}"
        namespaced_defs[new_name] = original_defs[def_name]

    # Update all $ref references in the schema
    def update_refs(obj: Any) -> None:
        if isinstance(obj, dict):
            if "$ref" in obj and obj["$ref"] in ref_mapping:
                obj["$ref"] = ref_mapping[obj["$ref"]]
            else:
                for value in obj.values():
                    update_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                update_refs(item)

    update_refs(schema)
    schema["$defs"] = namespaced_defs
    return schema


def extract_openapi_schema(
    cls: Any,
    namespace_prefix: str = "",
) -> dict[str, Any]:
    """Extract standard JSON Schema with $defs and optional namespacing for conflict prevention.

    Args:
        cls: The class to extract schema from (Pydantic BaseModel or dataclass)
        namespace_prefix: Optional prefix to namespace $defs keys (prevents conflicts)

    Returns:
        JSON Schema dictionary with optional namespaced $defs
    """
    try:
        if issubclass(cls, BaseModel):
            # Generate standard JSON Schema with $defs
            schema = cls.model_json_schema(mode="validation")
        elif is_dataclass(cls):
            # Generate standard JSON Schema with $defs
            schema = json.schema(cls)
        else:
            return {}
    except TypeError:
        # cls is not a class
        return {}

    # Apply namespace prefix to prevent conflicts between different workflows/agents
    return _apply_namespace_to_schema(schema, namespace_prefix)


def explore_class_details(cls: Any) -> dict[str, Any]:
    """Extract detailed information about a class or function, focusing on input/output schemas.

    Returns:
        Dict containing:
        - name: The name of the class/function
        - type: 'class' or 'function'
        - input_schema: OpenAPI-compatible JSON schema of the input if applicable
        - output_schema: OpenAPI-compatible JSON schema of the output if applicable

    """
    details = {
        "name": getattr(cls, "__name__", "Unknown"),
        "type": "class" if inspect.isclass(cls) else "function",
        "input_schema": {},
        "output_schema": {},
        "description": (
            getattr(cls, "__restack_description__", "")
        ),
    }

    if inspect.isclass(cls):
        for name, method in inspect.getmembers(
            cls,
            predicate=inspect.isfunction,
        ):
            if name == "run":
                sig = inspect.signature(method)
                for param in sig.parameters.values():
                    if (
                        param.annotation
                        != inspect.Parameter.empty
                        and inspect.isclass(
                            param.annotation,
                        )
                    ):
                        details["input_schema"] = (
                            extract_openapi_schema(
                                param.annotation,
                                namespace_prefix=cls.__name__,
                            )
                        )
                if (
                    sig.return_annotation
                    != inspect.Signature.empty
                    and inspect.isclass(
                        sig.return_annotation,
                    )
                ):
                    details["output_schema"] = (
                        extract_openapi_schema(
                            sig.return_annotation,
                            namespace_prefix=cls.__name__,
                        )
                    )

    return details
