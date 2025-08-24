from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/greet")
def greet(name: str = Query(..., description="Name of the person")):
    return {"message": f"Hello, {name}!"}
