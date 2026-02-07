from fastapi import APIRouter

from .routers_log_in import router as login_router

router = APIRouter()

router.include_router(router=login_router)
