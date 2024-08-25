from aiogram.utils.keyboard import InlineKeyboardBuilder


async def new_user_keyboard(url):
    builder = InlineKeyboardBuilder()

    builder.button(text="Buy access to the program 🐹", url=url)
    builder.button(text="Already paid, get access!", callback_data="check_payment")

    builder.adjust(1, 2)

    return builder.as_markup()


async def old_user_keyboard():
    builder = InlineKeyboardBuilder()

    # builder.button(text="Change Login", callback_data="change_login")
    builder.button(text="Change Password", callback_data="change_password")

    builder.adjust(1, 2)

    return builder.as_markup()
