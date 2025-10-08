from fastapi import APIRouter, Depends

dependency0 = lambda: 1  # noqa: E731

dependency = lambda: 0  # noqa: E731


def dependency1(sub_dependant: int = Depends(dependency0)):
    return sub_dependant


router1 = APIRouter(prefix="/prefix1")


@router1.get("/get1")
def get1(dependency=Depends(dependency)):
    return {"1": 1}


router2 = APIRouter(prefix="/prefix2")


@router2.get("/get2")
def get2(dependency=Depends(dependency)):
    return {"2": 2}


router2.include_router(router1)
