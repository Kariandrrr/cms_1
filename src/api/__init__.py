from fastapi import APIRouter, Depends

from .auth.routers_log_in import router as register_router
from ..core.models.db_helper import get_db

api_router = APIRouter()
api_router.include_router(register_router, dependencies=[Depends(get_db)])
