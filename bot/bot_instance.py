from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode



bot_tocken = '6471784185:AAEWakBbPrU-bKGGanxahUq__ZbyZ1s8dBI'
#
# '6821675327:AAF9a8sfte4fvkIVmkxuTEkPb54_zdWU9xw'
# '6471784185:AAEWakBbPrU-bKGGanxahUq__ZbyZ1s8dBI'  - ChaPPy
#  '6749290706:AAEopst0S94hKVOGbRnTv7pO70-kt1ZiN54' Smart_Imperium_bot


bot = Bot(token=bot_tocken,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))



