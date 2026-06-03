import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from openai import AsyncOpenAI

from utils import check_tokens_limit, process_voice_message, process_text_message

load_dotenv()

TOKEN = getenv("TOKEN")
OPENAI_TOKEN = getenv("OPENAI_TOKEN")

dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_TOKEN)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Отправь мне текст или голосовое сообщение.")


@dp.message(F.voice)
async def voice_handler(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id

    if not check_tokens_limit(user_id):
        await message.answer("Лимит превышен. Купите подписку для дальнейшего пользование :)")
        return

    await bot.send_chat_action(chat_id=message.chat.id, action="record_voice")
    try:
        await process_voice_message(message, bot, client)
    except Exception as e:
        logging.error(f"Ошибка при обработке голоса: {e}")
        await message.answer("Произошла ошибка при обработке твоего голосового сообщения.")


@dp.message(F.text)
async def text_handler(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id

    if not check_tokens_limit(user_id):
        await message.answer("Лимит превышен. Купите подписку для дальнейшего пользование :)")
        return

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        await process_text_message(message, client)
    except Exception as e:
        logging.error(f"Ошибка при обработке текста: {e}")
        await message.answer("Не удалось получить ответ от ИИ.")


@dp.message()
async def unknown_handler(message: Message) -> None:
    await message.answer("Я умею общаться только текстом или голосовыми сообщениями!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())