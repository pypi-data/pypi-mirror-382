from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Dict, Optional, Any, Union, List
from http import HTTPStatus

try:
    from http import HTTPMethod
except (ImportError, ModuleNotFoundError):
    # Temporary patch for Python 3.10
    from backports.strenum import StrEnum

    class HTTPMethod(StrEnum):  # type: ignore
        CONNECT = "CONNECT"
        DELETE = "DELETE"
        GET = "GET"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        PATCH = "PATCH"
        POST = "POST"
        PUT = "PUT"
        TRACE = "TRACE"


class OpenAPIInfo(BaseModel):
    title: str
    description: Optional[str] = ""
    version: str


class Parameter(BaseModel):
    name: str
    description: Optional[str] = ""
    required: Optional[bool] = False
    type: Optional[str | List[str]] = None
    parameter_schema: Optional[Component] = Field(alias="schema", default=None)


class Component(BaseModel):
    title: Optional[str] = ""
    type: Optional[str | List[str]] = None
    description: Optional[str] = ""
    enum: List[Union[str, Any]] = []
    required: List[str] = []
    properties: Dict[str, Union[ResponseSelection, Component, Any]] = {}
    items: Optional[Component] = None

    def transform_properties_to_parameter(
        self, is_required: Optional[bool] = None
    ) -> List[Parameter]:
        parameters = []

        for key, item in self.properties.items():
            if isinstance(item, Component):
                parameters.append(
                    Parameter(
                        name=key,
                        description=item.description,
                        required=key in self.required or is_required,
                        type=item.type,
                        schema=item,
                    )
                )

            elif isinstance(item, ResponseSelection):
                nested_parameters = item.get_parameters(is_required)
                parameters.append(
                    Parameter(
                        name=key,
                        required=is_required,
                    )
                )

                if nested_parameters:
                    for np in nested_parameters:
                        parameters.append(
                            Parameter(
                                name=f"{key}.{np.name}",
                                description=np.description,
                                required=np.required,
                                type=np.type,
                                schema=np.parameter_schema,
                            )
                        )
                else:
                    parameters.append(Parameter(name=key, required=is_required))
            else:
                pass

        if self.items:
            parameters.extend(
                self.items.transform_properties_to_parameter(is_required)
            )

        return parameters


class ResponseSelection(BaseModel):
    model_config = ConfigDict(extra="ignore")

    oneOf: List[Component] = []
    allOf: List[Component] = []
    anyOf: List[Component] = []

    def get_parameters(
        self, is_required: Optional[bool] = None
    ) -> List[Parameter]:
        for key in self.model_fields.keys():
            list_of_components = getattr(self, key)

            if list_of_components:
                merged_properties: List[Parameter] = []

                for component in list_of_components:
                    merged_properties.extend(
                        component.transform_properties_to_parameter(is_required)
                    )

                return merged_properties

        return []


class SchemaObject(BaseModel):
    object_schema: Union[ResponseSelection, Component] = Field(alias="schema")

    def get_parameters(
        self, is_required: Optional[bool] = None
    ) -> List[Parameter]:
        if isinstance(self.object_schema, Component):
            if self.object_schema.type == "array":
                # TODO: https://github.com/TathagataChakraborti/NESTFUL/issues/4
                items = self.object_schema.items

                if not items:
                    raise ValueError(f"Empty array specification: {self}")
                else:
                    if items.type != "object":
                        raise NotImplementedError

                    return items.transform_properties_to_parameter(is_required)

            elif self.object_schema.type == "object":
                return self.object_schema.transform_properties_to_parameter(
                    is_required
                )

            else:
                # TODO: https://github.com/TathagataChakraborti/NESTFUL/issues/3
                return [Parameter(name="None")]

        elif isinstance(self.object_schema, ResponseSelection):
            return self.object_schema.get_parameters(is_required)

        else:
            raise NotImplementedError


class PayloadObject(BaseModel):
    model_config = ConfigDict(extra="ignore")

    description: Optional[str] = ""
    content: Dict[str, SchemaObject] = {}
    required: Optional[bool] = None

    def get_parameters(
        self, serialization_scheme: Optional[str] = None
    ) -> List[Parameter]:
        output_schema = self.get_output_schema(serialization_scheme)
        return (
            output_schema.get_parameters(is_required=self.required)
            if output_schema
            else []
        )

    def get_output_schema(
        self, serialization_scheme: Optional[str] = None
    ) -> Optional[SchemaObject]:
        if serialization_scheme:
            return self.content.get(serialization_scheme, None)

        else:
            return next(iter(self.content.values()))


class PathSpec(BaseModel):
    model_config = ConfigDict(extra="ignore")

    operationId: str
    description: Optional[str] = ""
    summary: Optional[str] = ""
    parameters: List[Parameter] = []
    requestBody: Optional[PayloadObject] = None
    responses: Dict[HTTPStatus, PayloadObject]

    @model_validator(mode="after")
    def merge_request_body_into_parameters(self) -> PathSpec:
        if self.requestBody:
            request_body_parameters = self.requestBody.get_parameters()
            self.parameters.extend(request_body_parameters)

        return self


class ComponentDict(BaseModel):
    schemas: Dict[str, Component]


class OpenAPI(BaseModel):
    model_config = ConfigDict(extra="ignore")

    openapi: str
    info: OpenAPIInfo
    paths: Dict[str, Dict[str, Union[PathSpec, List[Parameter]]]]
    components: Optional[ComponentDict] = None

    @model_validator(mode="after")
    def merge_global_parameters(self) -> OpenAPI:
        new_paths = {}

        for path, path_object in self.paths.items():
            global_parameters = path_object.get("parameters", [])

            if isinstance(global_parameters, PathSpec):
                pass
            else:
                new_spec: Dict[str, PathSpec] = {}

                for method in HTTPMethod:
                    path_spec = path_object.get(method.lower(), None)

                    if isinstance(path_spec, PathSpec):
                        path_spec.parameters.extend(global_parameters)
                        new_spec[method] = path_spec

                new_paths[path] = new_spec

        self.paths = new_paths  # type: ignore
        return self


def merge_components(
    c1: Optional[Component], c2: Optional[Component]
) -> Optional[Component]:
    if c1 is None and c2 is None:
        return None

    c1 = c1 or Component()
    c2 = c2 or Component()

    return Component.model_validate(
        {
            **c1.model_dump(),
            **c2.model_dump(),
            "items": merge_components(c1.items, c2.items),
            "properties": {
                **c1.properties,
                **c2.properties,
            },
        }
    )


def process_props(props: Component | ResponseSelection) -> Component:
    if isinstance(props, Component):
        if props.items:
            props.items = process_props(props.items)

        if props.properties:
            for k, v in props.properties.items():
                props.properties[k] = process_props(v)

        return props

    elif isinstance(props, ResponseSelection):
        merged_component = Component()

        for key in ResponseSelection.model_fields.keys():
            list_of_components = getattr(props, key)

            if list_of_components:
                for component in list_of_components:
                    merged_component = (
                        merge_components(merged_component, component)
                        or Component()
                    )

        return process_props(merged_component)
    else:
        raise ValueError(props)
