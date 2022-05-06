from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Перезапустить бота"),
            types.BotCommand("quest", "Запустить квест"),
            types.BotCommand("help", "Вывести справку"),
            types.BotCommand("create_token", "Создать новый токен"),
            types.BotCommand("load_script", "Обновить сценарий")
        ]
    )
