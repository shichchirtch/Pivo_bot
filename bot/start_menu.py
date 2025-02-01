from aiogram.types import BotCommand

# Функция для настройки кнопки Menu бота
async def set_main_menu(bot):

    main_menu_commands = [
        BotCommand(command='/help',
                   description='Как работать с ботом'),

        BotCommand(command='/catalog',
                   description='Пролистать каталог пива'),

        BotCommand(command='/show_collection',
                   description='Посмотреть коллекцию пива'),

        BotCommand(command='/add_new_beer',
                   description='Добавить новый сорт пива в коллекцию'),

        BotCommand(command='/poisk',
                   description='Узнай, есть ли Пиво в моей коллекции !')
    ]

    await bot.set_my_commands(main_menu_commands)

