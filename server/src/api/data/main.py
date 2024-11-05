from fastapi import APIRouter
from .endpoint import Endpoint
from .baostock import BaostockEndpoint


router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={404: {"description": "Not found"}},
)

endpoints: dict[str, Endpoint] = {
    "baostock": BaostockEndpoint(),
}


@router.get("/endpoints")
async def get_endpoints():
    return {"endpoints": [endpoint["name"] for endpoint in endpoints]}
