from fastapi import APIRouter
from .demo_jwt_auth import router as demo_jwt_auth_router

router = APIRouter()
router.include_router(router=demo_jwt_auth_router)
