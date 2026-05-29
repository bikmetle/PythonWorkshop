from openai import AsyncOpenAI
from openai import APIConnectionError
import asyncio
import logging
import sys
from os import getenv
from io import BytesIO

from datetime import datetime
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from models import Usage
from utils import add_usage

load_dotenv()

TOKEN = getenv("TOKEN")
OPENAI_TOKEN = getenv("OPENAI_TOKEN")

dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_TOKEN)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message, bot: Bot) -> None:
    try:
        if message.text:
            response = await client.responses.create(
                model="gpt-5.5",
                input=message.text,
            )

            await message.answer(response.output_text)

        elif message.voice:
            file = await bot.get_file(message.voice.file_id)

            audio_buffer = BytesIO()
            await bot.download_file(file.file_path, audio_buffer)

            audio_buffer.seek(0)
            audio_buffer.name = "voice.ogg"

            transcription = await client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_buffer,
            )

            response = await client.responses.create(
                model="gpt-5.5",
                input=transcription.text,
            )

            await message.answer(response.output_text)

        else:
            await message.answer(
                "Ну ты конечно красавчик, я не отрицаю, но давай мне текст или голосовое сообщение своё сюда!"
            )
            return
        total_tokens = response.usage.total_tokens
        usage = Usage(
            tg_id=message.from_user.id, created_at=datetime.now(), tokens=total_tokens
        )
        add_usage(usage)
    except Exception as e:
        logging.exception(e)
        await message.answer("Произошла ошибка при обращении к OpenAI.")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
