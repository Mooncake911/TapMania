import re
import uuid
import string
import secrets

from aiogram import Router, types, F, html
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from yoomoney import Client, Quickpay

from .keyboards import user_kb as kb
from ...bd import redis_manager
from config import YOOMONEY_ACCESS_TOKEN


def generate_password(length=6):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def is_valid_string(s):
    return bool(re.match(r'^[A-Za-z0-9]+$', s))


client = Client(YOOMONEY_ACCESS_TOKEN)


def make_payment_link(order_id):
    quick_pay = Quickpay(
        receiver="4100117647508117",
        quickpay_form="shop",
        targets="Payment for access to the service",
        paymentType="AC",  # AC - банковская карта, PC - Яндекс.Деньги
        sum=2,  # RUB
        label=order_id
    )
    return quick_pay


user_router = Router(name="UserRouter")


class PaymentState(StatesGroup):
    order_id = State()


class Form(StatesGroup):
    # login = State()
    password = State()


@user_router.message(CommandStart())
async def command_start(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_data = redis_manager.get_user_data(telegram_id=user_id)

    if not user_data:
        order_id = f"user_{user_id};order_{uuid.uuid4()}"
        await state.update_data(order_id=order_id)
        quick_pay = make_payment_link(order_id)
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!\n"
                             f"You will get access after payment:\n",
                             reply_markup=await kb.new_user_keyboard(url=quick_pay.redirected_url))
    else:
        await message.answer(f"Your access data:\n"
                             f"Login: {user_id}\n"
                             f"Password: {user_data.get('password')}\n",
                             reply_markup=await kb.old_user_keyboard())


@user_router.callback_query(F.data == 'check_payment')
async def check_payment_status(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')

    if not order_id:
        await callback.message.answer("No payment information found. Please /start again.")
        return

    operations = client.operation_history(label=order_id)
    for operation in operations.operations:
        if operation.status == "success":
            user_id = callback.message.from_user.id
            password = generate_password()
            redis_manager.set_user_data(telegram_id=user_id, password=password)
            await callback.message.answer(f"The payment was successful! 🙌\n"
                                          f"Login: {user_id}\n"
                                          f"Password: {password}\n", reply_markup=await kb.old_user_keyboard())
            break
    else:
        await callback.message.answer(
            "Sorry, the payment has not been completed yet 🔄.\n"
            "Please try again later or contact with our support: @Vadim_noodle.")


# @user_router.callback_query(F.data == "change_login")
# async def change_login(callback: types.CallbackQuery, state: FSMContext) -> None:
#     await state.set_state(Form.login)
#     await callback.message.answer(f"Enter your new login:")


# @user_router.message(Form.login)
# async def process_new_login(message: types.Message, state: FSMContext) -> None:
#     user_id = message.from_user.id
#     username = message.text
#     redis_manager.update_user_username(telegram_id=user_id, username=username)
#     await command_start(message, state)
#     await state.clear()


@user_router.callback_query(F.data == "change_password")
async def change_password(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Form.password)
    await callback.message.answer(f"Enter your new password:")


@user_router.message(Form.password)
async def process_new_password(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    password = message.text.replace(" ", "")
    if is_valid_string(password):
        redis_manager.update_user_password(telegram_id=user_id, password=password)
        await command_start(message, state)
        await state.clear()
    else:
        await state.set_state(Form.password)
        await message.answer(f"Please, use only numbers, uppercase and lowercase English letters.\n"
                             f"But your password is: {password}.")


@user_router.message(Command("cancel"))
@user_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Cancelled.", reply_markup=types.ReplyKeyboardRemove())
