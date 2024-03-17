import asyncio

from env import TELEGRAM_TOKEN

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold


dp = Dispatcher()

"https://t.me/quantfreedom_bot"


@dp.message(CommandStart())
async def cmd_start(msg: types.Message) -> None:
    reply_text = f"Hello, {hbold(msg.from_user.username)}"

    await msg.answer(
        text=reply_text,
    )


async def main() -> None:
    bot = Bot(
        token=TELEGRAM_TOKEN,
        parse_mode="HTML",
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
