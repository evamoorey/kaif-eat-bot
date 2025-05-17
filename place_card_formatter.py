from telegram import Message, ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes

CATEGORY_ICONS = {
    'Ресторан': '🍽️',
    'Быстрое питание': '🍔',
    'Сыроварня': '🧀',
    'Суши-бар': '🍣',
    'Кафе': '☕️',
    'Столовая': '🥘',
    'Магазин суши и роллов': '🍱',
    'Пиццерия': '🍕',
    'Бар': '🍸',
    'Кофейня': '☕️',
    'Доставка еды и обедов': '🛵🍲',
    'Пекарня': '🥖',
    'Магазин продуктов': '🛒',
    'Магазин кулинарии': '🍴',
    'Чайхана': '🫖',
    'Караоке-клуб': '🎤',
    'Банкетный зал': '🎉',
    'Организация и проведение детских праздников': '🎈',
    'Кофейный автомат': '🤖☕',
    'Магазин пива': '🍺',
    'Кондитерская': '🍰',
    'Фудмолл, гастромаркет': '🏬🍜',
    'Кальян-бар': '💨',
    'Кофе с собой': '🥤',
    'Организация мероприятий': '📋',
    'Вейк-клуб': '🏄‍♂️',
    'Место для пикника': '🌳🧺',
    'Безалкогольный бар': '🍹❌🍺',
    'Пункт выдачи': '📦',
    'Бильярдный клуб': '🎱',
    'Фитнес-клуб': '💪',
    'Парк аттракционов': '🎡',
    'Продуктовый рынок': '🛒',
    'Спортбар': '🏈🍻',
}


async def send_place_card(update: Update, context: ContextTypes.DEFAULT_TYPE, place) -> Message:
    if place.rating is not None:
        rating_float = float(place.rating.replace(',', '.'))
        full_stars = int(rating_float)
        half_star = '⭐️' if (rating_float - full_stars) >= 0.5 else ''
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        rating_stars = '⭐️' * full_stars + half_star + '☆' * empty_stars
    else:
        rating_stars = '☆' * 5

    description = place.description
    if description:
        description = description.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        words = description.split()
        if len(words) > 20:
            description = ' '.join(words[:20]) + '...'
    else:
        description = '...'

    icon = CATEGORY_ICONS.get(place.category, '📍')
    if place.category in CATEGORY_ICONS:
        icon = CATEGORY_ICONS[place.category]

    message = f"""
{icon} <b>{place.name}</b>
<i> • {place.category} • </i>

<b>Рейтинг:</b> {rating_stars} ({place.rating}/5) • {place.reviews_count}
<b>Расстояние от вас:</b> {place.distance_km:.2f} км
<b>Адрес:</b> {place.address}

📌 <b>Описание:</b>
{description}
"""

    reply_markup = ReplyKeyboardMarkup(
        [
            ["🔍 Найти место"],
            ["⚙️ Настроить сортировку", "🗑️ Сбросить местоположение"]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    if place.image and place.image != 'Нет данных':
        try:
            return await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=place.image.split(';')[-1].strip(),
                caption=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except:
            pass

    return await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )
