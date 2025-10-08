from aiogram import Router

router = Router()

from .unified_furniture_handler import router as unified_furniture_router
router.include_router(unified_furniture_router)

from .navigation_handler import router as navigation_router
router.include_router(navigation_router)