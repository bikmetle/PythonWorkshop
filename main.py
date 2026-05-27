from openai import OpenAI
import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.getenv("TOKEN")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")

dp = Dispatcher()
client = OpenAI(api_key=OPENAI_TOKEN)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    if message.text:
        response = client.responses.create(
            model="gpt-5.5",
            input=message.text,
        )

        await message.answer(response.output_text)

    else:
        await message.answer("Nice try")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
