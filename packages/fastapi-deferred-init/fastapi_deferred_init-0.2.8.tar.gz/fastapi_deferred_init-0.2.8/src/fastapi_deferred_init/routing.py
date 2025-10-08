import inspect
from enum import Enum, IntEnum
from functools import cached_property
from typing import (
    Any,
    Callable,
    ClassVar,
    Optional,
    Union,
)
from collections.abc import Sequence

from starlette.routing import BaseRoute
from starlette.routing import Mount as Mount  # noqa
from starlette.routing import compile_path, get_name
from starlette.types import ASGIApp, Lifespan


from fastapi import params, routing  # type:ignore
from fastapi._compat import ModelField, lenient_issubclass
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.dependencies.utils import (
    _should_embed_body_fields,
    get_body_field,
    get_dependant,
    get_flat_dependant,
    get_parameterless_sub_dependant,
    get_typed_return_annotation,
)
from fastapi.responses import JSONResponse, Response
from fastapi.types import IncEx
from fastapi.utils import (
    create_cloned_field,
    create_model_field,
    generate_unique_id,
    is_body_allowed_for_status_code,
)


class DeferringAPIRoute(routing.APIRoute):
    _getattr: ClassVar[Callable[[Any, str], Any]]

    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        response_model: Any = Default(None),
        status_code: Optional[int] = None,
        tags: Optional[list[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[dict[Union[int, str], dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        name: Optional[str] = None,
        methods: Optional[Union[set[str], list[str]]] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[IncEx] = None,
        response_model_exclude: Optional[IncEx] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Union[type[Response], DefaultPlaceholder] = Default(
            JSONResponse
        ),
        dependency_overrides_provider: Optional[Any] = None,
        callbacks: Optional[list[BaseRoute]] = None,
        openapi_extra: Optional[dict[str, Any]] = None,
        generate_unique_id_function: Union[
            Callable[["routing.APIRoute"], str], DefaultPlaceholder
        ] = Default(generate_unique_id),
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        if isinstance(response_model, DefaultPlaceholder):
            return_annotation = get_typed_return_annotation(endpoint)
            if lenient_issubclass(return_annotation, Response):
                response_model = None
            else:
                response_model = return_annotation
        self.response_model = response_model
        self.summary = summary
        self.response_description = response_description
        self.deprecated = deprecated
        self.operation_id = operation_id
        self.response_model_include = response_model_include
        self.response_model_exclude = response_model_exclude
        self.response_model_by_alias = response_model_by_alias
        self.response_model_exclude_unset = response_model_exclude_unset
        self.response_model_exclude_defaults = response_model_exclude_defaults
        self.response_model_exclude_none = response_model_exclude_none
        self.include_in_schema = include_in_schema
        self.response_class = response_class
        self.dependency_overrides_provider = dependency_overrides_provider
        self.callbacks = callbacks
        self.openapi_extra = openapi_extra
        self.generate_unique_id_function = generate_unique_id_function
        self.tags = tags or []
        self.responses = responses or {}
        self.name = get_name(endpoint) if name is None else name
        self.path_regex, self.path_format, self.param_convertors = compile_path(path)
        if methods is None:
            methods = ["GET"]
        self.methods: set[str] = {method.upper() for method in methods}
        if isinstance(generate_unique_id_function, DefaultPlaceholder):
            current_generate_unique_id: Callable[[routing.APIRoute], str] = (
                generate_unique_id_function.value
            )
        else:
            current_generate_unique_id = generate_unique_id_function
        self.unique_id = self.operation_id or current_generate_unique_id(self)
        # normalize enums e.g. http.HTTPStatus
        if isinstance(status_code, IntEnum):
            status_code = int(status_code)
        self.status_code = status_code
        if self.response_model:
            assert is_body_allowed_for_status_code(status_code), (
                f"Status code {status_code} must not have a response body"
            )
        self.dependencies = list(dependencies or [])
        self.description = description or inspect.cleandoc(self.endpoint.__doc__ or "")
        self.description = self.description.split("\f")[0].strip()

        assert callable(endpoint), "An endpoint must be a callable"

    @cached_property
    def dependant(self):
        dependant = get_dependant(path=self.path_format, call=self.endpoint)

        for depends in self.dependencies[::-1]:
            dependant.dependencies.insert(
                0,
                get_parameterless_sub_dependant(depends=depends, path=self.path_format),
            )
        return dependant

    @cached_property
    def _flat_dependant(self):
        return get_flat_dependant(self.dependant)

    @cached_property
    def _embed_body_fields(self):
        return _should_embed_body_fields(self._flat_dependant.body_params)

    @cached_property
    def response_field(self):
        if self.response_model:
            response_name = "Response_" + self.unique_id
            return create_model_field(
                name=response_name,
                type_=self.response_model,
                mode="serialization",
            )
        else:
            return None

    @cached_property
    def secure_cloned_response_field(self) -> Optional[ModelField]:
        return create_cloned_field(self.response_field) if self.response_model else None

    @cached_property
    def response_fields(self) -> dict[Union[int, str], ModelField]:
        response_fields: dict[Union[int, str], ModelField] = {}
        for additional_status_code, response in self.responses.items():
            assert isinstance(response, dict), "An additional response must be a dict"
            model = response.get("model")
            if model:
                assert is_body_allowed_for_status_code(additional_status_code), (
                    f"Status code {additional_status_code} must not have a response body"
                )
                response_name = f"Response_{additional_status_code}_{self.unique_id}"
                response_field = create_model_field(
                    name=response_name, type_=model, mode="serialization"
                )
                response_fields[additional_status_code] = response_field
        return response_fields

    @cached_property
    def body_field(self):
        return get_body_field(
            flat_dependant=self._flat_dependant,
            name=self.unique_id,
            embed_body_fields=self._embed_body_fields,
        )

    @cached_property
    def app(self):
        return routing.request_response(self.get_route_handler())


class DeferringAPIRouter(routing.APIRouter):
    def __init__(
        self,
        *,
        prefix: str = "",
        tags: Optional[list[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        default_response_class: type[Response] = Default(JSONResponse),
        responses: Optional[dict[Union[int, str], dict[str, Any]]] = None,
        callbacks: Optional[list[BaseRoute]] = None,
        routes: Optional[list[BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        dependency_overrides_provider: Optional[Any] = None,
        route_class: type[routing.APIRoute] = DeferringAPIRoute,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        lifespan: Optional[Lifespan[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(
            generate_unique_id
        ),
    ) -> None:
        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )
