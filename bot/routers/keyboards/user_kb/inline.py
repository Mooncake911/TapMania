from aiogram.utils.keyboard import InlineKeyboardBuilder


async def new_user_keyboard(bay_url, download_url):
    builder = InlineKeyboardBuilder()

    builder.button(text="Buy access to the program ✅", url=bay_url)
    builder.button(text="Download the program 🐹", url=download_url)
    builder.button(text="Already paid, get access!", callback_data="check_payment")

    builder.adjust(1)

    return builder.as_markup()


async def old_user_keyboard(download_url):
    builder = InlineKeyboardBuilder()

    # builder.button(text="Change Login", callback_data="change_login")
    builder.button(text="Download the program 🐹", url=download_url)
    builder.button(text="Change Password", callback_data="change_password")

    builder.adjust(1)

    return builder.as_markup()
