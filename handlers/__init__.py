from aiogram import Router

router = Router()

from .admin import router as admin_router
router.include_router(admin_router)

from .backend import router as backend_router
router.include_router(backend_router)

from .cooperation.cooperation import router as cooperation_router
router.include_router(cooperation_router)