from aiogram import Router

router = Router()

from .sleep_furniture_handler import router as sleep_furniture_router
router.include_router(sleep_furniture_router)

from .kitchen_furniture_handler import router as kitchen_furniture_router
router.include_router(kitchen_furniture_router)

from .soft_furniture_handler import router as soft_furniture_router
router.include_router(soft_furniture_router)

from .tables_chairs_handler import router as tables_chairs_router
router.include_router(tables_chairs_router)

from .cabinets_commodes_handler import router as cabinets_commodes_router
router.include_router(cabinets_commodes_router)

from .bed_furniture_handler import router as bed_furniture_router
router.include_router(bed_furniture_router)

from .mattresses_handler import router as mattresses_router
router.include_router(mattresses_router)

from .wardrobes_handler import router as wardrobes_router
router.include_router(wardrobes_router)