import os

import pytest
from pydantic import BaseModel
from starlette.routing import Route

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from fastapi_deferred_init import DeferringAPIRoute, DeferringAPIRouter

from .data.gen_code_ast import create_code
from .helpers import import_via_file_path, load_code


def skip_test(use_lib: bool):
    if not use_lib and not os.getenv("FULL_TEST"):
        pytest.skip()


@pytest.mark.parametrize(["use_lib"], [(True,), (False,)])
def test_basic(use_lib: bool, benchmark):
    skip_test(use_lib=use_lib)
    create_code(50, use_lib=use_lib)  # switch bool to compare

    generated_code = benchmark(load_code)

    app = FastAPI()
    router = generated_code.router

    app.include_router(router)

    assert type(router) is (DeferringAPIRouter if use_lib else APIRouter)
    client = TestClient(app)
    assert len(app.routes) == 54
    for route in app.routes:
        if route in router.routes:
            assert type(route) is (DeferringAPIRoute if use_lib else APIRoute)
        assert isinstance(route, Route)
        resp = client.get(route.path)
        assert resp.status_code == 200


@pytest.mark.parametrize(["use_lib"], [(True,), (False,)])
def test_with_pydantic_model(use_lib: bool):
    skip_test(use_lib=use_lib)
    app = FastAPI()
    router = DeferringAPIRouter() if use_lib else APIRouter()

    class Login(BaseModel):
        username: str
        password: str

    @router.post("/login")
    async def do_login(json: Login):
        assert isinstance(json, Login)
        assert isinstance(json.username, str)
        assert isinstance(json.password, str)

        return {"userdata": "[...]"}

    app.include_router(router)

    client = TestClient(app)

    resp = client.post("/login", json={"username": "jvllmr", "password": "password"})
    assert resp.status_code == 200


def test_fastapi_openapi_schema(monkeypatch):
    monkeypatch.setattr("fastapi.routing.APIRoute", DeferringAPIRoute)
    monkeypatch.setattr("fastapi.routing.APIRouter", DeferringAPIRouter)
    import_via_file_path(
        "fastapi_clone.tests.test_additional_properties",
        "fastapi/tests/test_additional_properties.py",
    )

    import_via_file_path(
        "fastapi_clone.tests.test_openapi_examples",
        "fastapi/tests/test_openapi_examples.py",
    )

    from fastapi_clone.tests.test_additional_properties import (  # noqa # type: ignore
        test_openapi_schema as fastapi_test_openapi_schema_additional,
    )
    from fastapi_clone.tests.test_openapi_examples import (  # noqa # type: ignore
        test_openapi_schema as fastapi_test_openapi_schema,
    )

    fastapi_test_openapi_schema()
    fastapi_test_openapi_schema_additional()
