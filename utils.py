from http import client
import logging
from mailbox import Message
import os

from aiogram import Bot
from sqlalchemy import select
from main import TEMP_DIR
from models import Session, Usage
from io import BytesIO


def add_object(object) -> None:
    with Session() as session:
        try:
            session.add(object)
        except Exception:
            session.rollback()
            raise
        else:
            session.commit()

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
        reply_voice = FSInputFile(output_audio_path) # type: ignore
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
