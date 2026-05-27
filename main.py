import asyncio
import logging

import sys
from openai import OpenAI
from os import getenv
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
load_dotenv()

TOKEN = getenv("TOKEN")
client = OpenAI()
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:

   
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    if message.text:
        response = client.responses.create(
            model="gpt-5.5",
            input=message.text)
        await message.answer(response.output_text)

    else:
        await message.answer("Nice try!")

    
        
        


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())