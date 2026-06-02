import asyncio
from datetime import datetime
import logging

import os
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import select

from models import Session, Usage

load_dotenv()

TOKEN = getenv("TOKEN")
# Инициализируем клиент OpenAI (он автоматически подтянет OPENAI_API_KEY из .env)
client = OpenAI()
dp = Dispatcher()

# Создаем папку для временного хранения аудиофайлов, если её нет
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Отправь мне текст или голосовое сообщение.")


# Обработчик только для голосовых сообщений
@dp.message(F.voice)
async def voice_handler(message: Message, bot: Bot) -> None:
    # Показываем пользователю статус, что бот записывает голосовое ответное сообщение
    await bot.send_chat_action(chat_id=message.chat.id, action="record_voice")

    # Формируем пути для временных файлов на основе ID сообщения
    input_audio_path = os.path.join(TEMP_DIR, f"in_{message.voice.file_id}.ogg")
    output_audio_path = os.path.join(TEMP_DIR, f"out_{message.voice.file_id}.mp3")

    try:
        # 1. Скачиваем голосовое сообщение из Телеграм
        file_info = await bot.get_file(message.voice.file_id)
        await bot.download_file(file_info.file_path, input_audio_path)

        # 2. Превращаем аудио в текст с помощью OpenAI Whisper
        with open(input_audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        user_text = transcription.text

        # Если Whisper ничего не расслышал
        if not user_text.strip():
            await message.reply("Извини, мне не удалось разобрать слова в голосовом сообщении.")
            return

        # 3. Отправляем распознанный текст в твою модель OpenAI
        ai_response = client.responses.create(
            model="gpt-5.5",
            input=user_text
        )
        ai_text = ai_response.output_text

        # 4. Превращаем текстовый ответ ИИ обратно в голос с помощью OpenAI TTS
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",  # Варианты голосов: alloy, echo, fable, onyx, nova, shimmer
            input=ai_text
        ) as tts_response:
            tts_response.stream_to_file(output_audio_path)

        # 5. Отправляем аудиофайл пользователю в виде голосового ответа
        reply_voice = FSInputFile(output_audio_path)
        await message.reply_voice(voice=reply_voice)

    except Exception as e:
        logging.error(f"Ошибка при обработке голоса: {e}")
        await message.answer("Произошла ошибка при обработке твоего голосового сообщения.")

    finally:
        # Обязательно удаляем временные файлы с диска, чтобы не забивать память
        if os.path.exists(input_audio_path):
            os.remove(input_audio_path)
        if os.path.exists(output_audio_path):
            os.remove(output_audio_path)


# Обработчик для текстовых сообщений
@dp.message(F.text)
async def text_handler(message: Message) -> None:
    with Session() as session:
        statement = select(Usage).where(Usage.tg_id == message.from_user.id)
        db_objects = session.scalars(statement).all()
    
    total_token = sum([obj.tokens for obj in db_objects])
    if total_token > 100:
        await message.answer("Лимит превышен. Купите подписку для дальнейшего пользование :)")
        return
    response = client.responses.create(
        model="gpt-5.5",
        input=message.text
    )
    usage = Usage(tg_id=message.from_user.id, created_at=datetime.now(), tokens=response.usage.total_tokens)
    
    with Session() as session:
        try:
            session.add(usage)
        except:
            session.rollback()
            raise
        else:
            session.commit()


    await message.answer(response.output_text)


# Заглушка на случай, если отправили фото, документ или стикер
@dp.message()
async def unknown_handler(message: Message) -> None:
    await message.answer("Я умею общаться только текстом или голосовыми сообщениями!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())