from app.routers.dogs import router as dogs_router
from app.routers.login import router as login_router
from app.routers.owners import router as owners_router

__all__ = ["dogs_router", "login_router", "owners_router"]
