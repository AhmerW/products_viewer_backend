from fastapi import APIRouter

from app.api.routes import products, login, categories, defaults, assets

router = APIRouter()
router.include_router(products.router)
router.include_router(login.router)
router.include_router(categories.router)
router.include_router(defaults.router)
router.include_router(assets.router)