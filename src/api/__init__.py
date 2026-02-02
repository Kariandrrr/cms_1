from fastapi import APIRouter
from .auth import demo_jwt_auth_router
from .auth.demo_jwt_auth import router as demo_jwt_auth_router

api_router = APIRouter()

# add another routers and import in main.py only one main router


@api_router.get("/health")
async def health():
    return {"status": "backend alive"}


api_router.include_router(demo_jwt_auth_router)
