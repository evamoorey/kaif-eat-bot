from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

from handlers import start, help_command, handle_new_location, handle_find_another_place, request_location, \
    show_sort_options, handle_sort_selection, handle_main_menu

TOKEN = ""


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("location", request_location))

    # Обработчики кнопок
    application.add_handler(MessageHandler(filters.Text("🔍 Найти место"), handle_find_another_place))
    application.add_handler(MessageHandler(filters.Text("⚙️ Настроить сортировку"), show_sort_options))
    application.add_handler(MessageHandler(filters.Text("⬅️ Назад"), handle_main_menu))
    application.add_handler(MessageHandler(filters.Text(["🔍 По расстоянию", "⭐ По рейтингу"]), handle_sort_selection))

    # Обработчик местоположения
    application.add_handler(MessageHandler(filters.LOCATION, handle_new_location))

    # Обработчик текста по умолчанию
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu))

    application.run_polling()


if __name__ == '__main__':
    main()