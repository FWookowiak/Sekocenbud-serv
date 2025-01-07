from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def example_endpoint():
    return {"ex": "router"}