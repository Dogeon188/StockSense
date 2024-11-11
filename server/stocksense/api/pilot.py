from fastapi import APIRouter


router = APIRouter(
    prefix="/pilot",
    tags=["pilot"],
    responses={404: {"description": "Not found"}},
)


# TODO: Implement endpoint for client-side user interaction
# - Select trading target
