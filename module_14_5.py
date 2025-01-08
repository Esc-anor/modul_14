# импорт необходимых библиотек и методов
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
# блок из aiogram для работы с клавиатурой и объект кнопки
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from bot import *
import crud_functions_14_5

crud_functions_14_5.initiate_db()
if crud_functions_14_5.products_is_empty():
    crud_functions_14_5.populate_db()
products = crud_functions_14_5.get_all_products()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ],
        [KeyboardButton(text='Купить')],
        [KeyboardButton(text='Регистрация')]
    ], resize_keyboard=True
)

kb1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Рассчитать норму калорий',
                                 callback_data='calories'),
            InlineKeyboardButton(text='Формулы расчёта',
                                 callback_data='formulas')
        ]
    ]
)

kb2 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='М'),
            KeyboardButton(text='Ж')
        ]
    ]
)

kb_products = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text='Product1',
                             callback_data='product_buying'),
        InlineKeyboardButton(text='Product2',
                             callback_data='product_buying'),
        InlineKeyboardButton(text='Product3',
                             callback_data='product_buying'),
        InlineKeyboardButton(text='Product4',
                             callback_data='product_buying')
    ]]
)


# объявление класса состояния UserState наследованный от StatesGroup
class UserState(StatesGroup):
    # объявление объектов класса age, growth, weight, gender
    age = State()  # возраст
    growth = State()  # рост
    weight = State()  # вес
    gender = State()  # пол


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


# обработчик начала общения с ботом (команды /start)
@dp.message_handler(commands=['start'])
# функция старта
async def start(message):
    # дополнение методом reply_markup для отображения клавиатуры kb
    await message.answer('Привет! Я бот помогающий вашему здоровью.\n'
                         'Нажмите одну из кнопок для продолжения', reply_markup=kb)


# обработчик ожидания нажатия кнопки «Рассчитать»
@dp.message_handler(text=['Рассчитать'], state=None)
# функция получения возраста пользователя
async def main_menu(message: types.Message):
    # ожидание нажатия кнопок выбора
    await message.answer('Выберите опцию:', reply_markup=kb1)


# обработчик ожидания нажатия кнопки «Формулы расчёта»
@dp.callback_query_handler(text=['formulas'])
# функция вывода расчётной формулы
async def get_formula(call: types.CallbackQuery):
    await call.message.answer('Формула расчёта Миффлина-Сан Жеора:\n'
                              '(10*вес + 6.25*рост + 5*возраст + 5) - для мужчин\n'
                              '(10*вес + 6.25*рост + 5*возраст - 161) - для женщин')
    # ожидание останова данной функции
    await call.answer()


# обработчик ожидания нажатия кнопки «Рассчитать»
@dp.callback_query_handler(text=['calories'])
# функция получения возраста пользователя
async def set_age(call: types.CallbackQuery):
    # ожидание сообщения Calories и вывод текста
    await call.message.answer('Ваш возраст (полных лет):')
    # ожидание останова данной функции
    await call.answer()
    # ожидание ввода возраста
    await UserState.age.set()


# обработчик ожидания окончания статуса UserState.age
@dp.message_handler(state=UserState.age)
# функция получения роста пользователя
async def set_growth(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения возраста от пользователя в базе данных состояния
    await state.update_data(age_=message.text)
    # ожидание вывода текста
    await message.answer('Введите свой рост (см):')
    # ожидание ввода роста
    await UserState.growth.set()


# обработчик ожидания окончания статуса UserState.growth
@dp.message_handler(state=UserState.growth)
# функция получения веса пользователя
async def set_weight(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения роста от пользователя в базе данных состояния
    await state.update_data(growth_=message.text)
    # ожидание вывода текста
    await message.answer('Введите свой вес (кг):')
    # ожидание ввода веса
    await UserState.weight.set()


# обработчик ожидания окончания статуса UserState.weight
@dp.message_handler(state=UserState.weight)
# функция получения пола пользователя
async def set_gender(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения веса от пользователя в базе данных состояния
    await state.update_data(weight_=message.text)
    # ожидание вывода текста
    await message.reply('Введите свой пол (М / Ж):', reply_markup=kb2)
    # ожидание ввода пола
    await UserState.gender.set()


# обработчик ожидания окончания статуса UserState.gender
@dp.message_handler(state=UserState.gender)
# функция расчета суточного рациона пользователя в калориях
async def set_calories(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения веса от пользователя в базе данных состояния
    await state.update_data(gender_=message.text)
    # сохранение полученных данных в переменной data
    data = await state.get_data()
    # условие анализа пола пользователя
    if str(data['gender_']) == 'М':
        # Расчет по формуле Миффлина-Сан Жеора для мужчин
        calories = int(data['weight_']) * 10 + int(data['growth_']) * 6.25 - int(data['age_']) * 5 + 5
        # ожидание вывода текста результатов расчета
        await message.reply(f'Ваша норма калорий {calories} день')
    elif str(data['gender_']) == 'Ж':
        # Расчет по формуле Миффлина-Сан Жеора для женщин
        calories = int(data['weight_']) * 10 + int(data['growth_']) * 6.25 - int(data['age_']) * 5 - 161
        # ожидание вывода текста результатов расчета
        await message.reply(f'Ваша норма калорий {calories} к в день')
    print(f'{data}, {calories}')  # Вывод данных в консоль
    # завершение работы машины состояния
    await state.finish()


# обработчик кнопок Информация
@dp.message_handler(text=['Информация'])
# функция кнопок
async def inform(message):
    await message.answer("Бот поможет рассчитать суточный рацион в калориях\n"
                         "для вашего возраста, роста, веса и пола")


@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    for product in products:
        id, title, description, price = product
        await message.answer(f'Название: {title} | '
                             f'Описание: {description} | '
                             f'Цена: {price}')
        with open(f'product{id}.jpg', 'rb') as img:
            await message.answer_photo(img)

    await message.answer('Выберите продукт для покупки:',
                         reply_markup=kb_products)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')


@dp.message_handler(text=['Регистрация'])
async def sign_up(message):
    await message.answer(
        'Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if crud_functions_14_5.is_included(message.text):
        await message.answer('Пользователь существует, введите другое имя')
        return
    await state.update_data(username=message.text)
    await message.answer('Введите свой email:')
    await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    crud_functions_14_5.add_user(data['username'], data['email'], data['age'])
    await message.answer(f'Пользователь {data["username"]} зарегистрирован.')
    await state.finish()


# обработчик перехвата любых сообщений
@dp.message_handler()
# функция перехвата сообщений
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    # запуск бота (dp - аргумент через что стартовать)
    executor.start_polling(dp, skip_updates=True)
