from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from database import get_nearest_eat_location, get_another_nearest_eat_location, get_top_rated_eat_location
from place_card_formatter import send_place_card


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Доступные команды:\n/start - начать общение\n/help - помощь')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет!\n'
        'Я помогу тебе найти самые вкусные места.\n'
        'Пожалуйста, поделись своим местоположением для начала работы.',
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Поделиться местоположением", request_location=True)]],
            resize_keyboard=True
        )
    )


async def request_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Пожалуйста, поделись своим местоположением:',
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Поделиться местоположением", request_location=True)]],
            resize_keyboard=True
        )
    )


async def update_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    location_button = KeyboardButton("📍Поделиться местоположением", request_location=True)
    sort_button = KeyboardButton("⚙️ Настроить сортировку")
    reply_markup = ReplyKeyboardMarkup([[location_button], [sort_button]], resize_keyboard=True)

    await update.message.reply_text(
        '📍Отправь мне своё местоположение, и я подберу для тебя лучшие кафе и рестораны!',
        reply_markup=reply_markup)


async def show_sort_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    current_sort = user_data.get('sort_by', 'distance')

    nearby_button = KeyboardButton("🔍 По расстоянию" + (" ✅" if current_sort == 'distance' else ""))
    rating_button = KeyboardButton("⭐ По рейтингу" + (" ✅" if current_sort == 'rating' else ""))
    back_button = KeyboardButton("⬅️ Назад")
    reply_markup = ReplyKeyboardMarkup([[nearby_button, rating_button], [back_button]], resize_keyboard=True)

    await update.message.reply_text(
        'Выберите способ сортировки',
        reply_markup=reply_markup
    )


async def handle_sort_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_data = context.user_data

    if text == "⬅️ Назад":
        await update_location(update, context)
        return

    if 'last_location' not in user_data:
        await update.message.reply_text(
            "Пожалуйста, сначала отправьте ваше местоположение.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Отправить местоположение", request_location=True)]],
                resize_keyboard=True
            )
        )
        return

    lat, lon = user_data['last_location']

    if text.startswith("🔍 По расстоянию"):
        user_data['sort_by'] = 'distance'
        user_data['shown_place_ids'] = []  # Сбрасываем просмотренные места при смене сортировки
        nearest = get_nearest_eat_location(lat, lon)
        if nearest:
            user_data['shown_place_ids'] = [nearest.id]
            await send_place_card(update, context, nearest)
        await show_main_menu(update, context)  # Возвращаемся в главное меню

    elif text.startswith("⭐ По рейтингу"):
        user_data['sort_by'] = 'rating'
        user_data['shown_place_ids'] = []  # Сбрасываем просмотренные места при смене сортировки
        top_rated = get_top_rated_eat_location(lat, lon)
        if top_rated:
            user_data['shown_place_ids'] = [top_rated.id]
            await send_place_card(update, context, top_rated)
        await show_main_menu(update, context)  # Возвращаемся в главное меню


async def handle_new_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    location = update.message.location
    context.user_data['last_location'] = (location.latitude, location.longitude)
    context.user_data['shown_place_ids'] = []
    context.user_data['sort_by'] = 'distance'  # Устанавливаем сортировку по умолчанию

    # Показываем главное меню после получения местоположения
    await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    current_sort = user_data.get('sort_by', 'distance')
    sort_text = "Выбрана сортировка: 🔍 По расстоянию" if current_sort == 'distance' else "Выбрана сортировка: ⭐ По рейтингу"

    menu_buttons = [
        ["🔍 Найти место"],
        ["⚙️ Настроить сортировку", "🗑️ Сбросить местоположение"]
    ]
    await update.message.reply_text(
        f"{sort_text} \nНайдем новое место, чтобы перекусить?",
        reply_markup=ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    )


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "🔍 Найти место":
        await handle_find_another_place(update, context)
    elif text == "⚙️ Настроить сортировку":
        await show_sort_options(update, context)
    elif text == "🗑️ Сбросить местоположение":
        await reset_location(update, context)
    elif 'last_location' not in context.user_data:
        await request_location(update, context)
    else:
        await show_main_menu(update, context)


async def reset_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Очищаем данные о местоположении
    context.user_data.pop('last_location', None)
    context.user_data.pop('shown_place_ids', None)

    # Запрашиваем новое местоположение
    await update.message.reply_text(
        "Местоположение сброшено.\n"
        "Пожалуйста, отправьте новое местоположение",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Поделиться местоположением", request_location=True)]],
            resize_keyboard=True
        )
    )


async def handle_find_another_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data

    if 'last_location' not in user_data:
        await update.message.reply_text(
            "Пожалуйста, отправьте ваше местоположение заново.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Отправить местоположение", request_location=True)]],
                resize_keyboard=True
            )
        )
        return

    lat, lon = user_data['last_location']
    shown_ids = user_data.get('shown_place_ids', [])
    sort_by = user_data.get('sort_by', 'distance')  # Получаем сохраненный метод сортировки

    if sort_by == 'distance':
        new_place = get_another_nearest_eat_location(lat, lon, shown_ids)
    else:
        new_place = get_top_rated_eat_location(lat, lon, excluded_ids=shown_ids)

    if new_place:
        user_data['shown_place_ids'] = shown_ids + [new_place.id]
        await send_place_card(update, context, new_place)
    else:
        await update.message.reply_text(
            "Вы просмотрели все места поблизости. Хотите отправить новое местоположение?",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Отправить местоположение", request_location=True)]],
                resize_keyboard=True
            )
        )