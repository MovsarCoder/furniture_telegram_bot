from aiogram import Router


router = Router()

from .main_admin import router as main_admin_router
router.include_router(main_admin_router)

from .requests_cooperation import router as requests_cooperation_router
router.include_router(requests_cooperation_router)

from .new_category_furniture_handler import router as new_category_furniture_router
router.include_router(new_category_furniture_router)

from .list_categories_furniture_handler import router as list_categories_furniture_router
router.include_router(list_categories_furniture_router)
