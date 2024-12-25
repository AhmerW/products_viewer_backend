from fastapi import APIRouter

from app.api.routes import products, login, categories

router = APIRouter()
router.include_router(products.router)
router.include_router(login.router)
router.include_router(categories.router)