import ast
import copy

base_module = ast.Module(
    body=[
        ast.ImportFrom(
            module="fastapi",
            names=[ast.alias(name="Depends"), ast.alias(name="APIRouter")],
            level=0,
        ),
        ast.ImportFrom(
            module="fastapi.responses",
            names=[ast.alias(name="JSONResponse")],
            level=0,
        ),
        ast.ImportFrom(
            module="fastapi_deferred_init",
            names=[ast.alias(name="DeferringAPIRouter")],
            level=0,
        ),
        ast.Assign(
            targets=[ast.Name(id="dependency0", ctx=ast.Store())],
            value=ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                body=ast.Constant(value=1),
            ),
        ),
    ],
    type_ignores=[],
)


def gen_func_def(n=1, last=False):
    return ast.AsyncFunctionDef(
        name=f"dependency{'' if last else n}",
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(
                    arg="sub_dependant",
                    annotation=ast.Name(id="int", ctx=ast.Load()),
                )
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[
                ast.Call(
                    func=ast.Name(id="Depends", ctx=ast.Load()),
                    args=[ast.Name(id=f"dependency{n - 1}", ctx=ast.Load())],
                    keywords=[],
                )
            ],
        ),
        body=[ast.Return(value=ast.Name(id="sub_dependant", ctx=ast.Load()))],
        decorator_list=[],
    )


def gen_router(n=2, last=False, use_lib=True):
    return [
        ast.Assign(
            targets=[ast.Name(id=f"router{'' if last else n}", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(
                    id="DeferringAPIRouter" if use_lib else "APIRouter", ctx=ast.Load()
                ),
                args=[],
                keywords=[
                    ast.keyword(
                        arg="prefix",
                        value=ast.Constant(value=f"/prefix{'' if last else n}"),
                    ),
                    ast.keyword(
                        arg="dependencies",
                        value=ast.List(
                            elts=[
                                ast.Call(
                                    func=ast.Name(id="Depends", ctx=ast.Load()),
                                    args=[
                                        ast.Name(id=f"dependency{n}", ctx=ast.Load())
                                    ],
                                    keywords=[],
                                )
                            ]
                        ),
                    ),
                ],
            ),
        ),
    ] + (
        [
            ast.FunctionDef(
                name=f"get{'' if last else n}",
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg="dependency")],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[
                        ast.Call(
                            func=ast.Name(id="Depends", ctx=ast.Load()),
                            args=[ast.Name(id=f"dependency{n}", ctx=ast.Load())],
                            keywords=[],
                        )
                    ],
                ),
                body=[
                    ast.Return(
                        value=ast.Call(
                            func=ast.Name(id="JSONResponse", ctx=ast.Load()),
                            args=[
                                ast.Dict(
                                    keys=[ast.Constant(value=str(n))],
                                    values=[ast.Constant(value=n)],
                                )
                            ],
                            keywords=[],
                        )
                    )
                ],
                decorator_list=[
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(
                                id=f"router{'' if last else n}", ctx=ast.Load()
                            ),
                            attr="get",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Constant(value=f"/get{'' if last else n}")],
                        keywords=[],
                    )
                ],
            ),
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=f"router{'' if last else n}", ctx=ast.Load()),
                        attr="include_router",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Name(id=f"router{n - 1}", ctx=ast.Load())],
                    keywords=[],
                )
            ),
        ]
        if n > 0
        else []
    )


def get_tree(n=1000, use_lib=True):
    module = copy.deepcopy(base_module)
    for i in range(1, n + 1):
        module.body.append(gen_func_def(i))

    module.body.append(gen_func_def(i + 1, True))

    for i in range(n):
        module.body.extend(gen_router(i, use_lib=use_lib))

    module.body.extend(gen_router(i + 1, True, use_lib))

    ast.fix_missing_locations(module)
    return module


def create_code(n=1000, use_lib=True):
    tree = get_tree(n, use_lib)

    with open("tests/data/code.py", "w") as f:
        f.write(ast.unparse(tree))
