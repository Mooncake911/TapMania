from aiogram import Dispatcher

from .user import user_router


def register_all_handlers(dp: Dispatcher) -> None:
    routers = (
        user_router,
    )
    for router in routers:
        dp.include_router(router)
