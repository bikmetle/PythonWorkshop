import os
from datetime import datetime
from sqlalchemy import select
from aiogram import Bot
from aiogram.types import Message, FSInputFile
from openai import AsyncOpenAI
from models import Session, Usage

FREE_TOKEN_LIMIT = 100
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

def add_usage(usage: Usage) -> None:
    with Session() as session:
        try:
            session.add(usage)
        except Exception:
            session.rollback()
            raise
        else:
            session.commit()

def get_usage(user_id: int) -> int:
    statement = select(Usage).where(Usage.user_id == user_id)
    with Session() as session:
        db_objects = session.scalars(statement).all()
    return sum(row.tokens for row in db_objects if row.tokens)

def check_tokens_limit(user_id: int) -> bool:
    total_spent = get_usage(user_id)
    return total_spent < FREE_TOKEN_LIMIT

async def process_voice_message(message: Message, bot: Bot, client: AsyncOpenAI) -> None:
    user_id = message.from_user.id
    input_audio_path = os.path.join(TEMP_DIR, f"in_{message.voice.file_id}.ogg")
    output_audio_path = os.path.join(TEMP_DIR, f"out_{message.voice.file_id}.mp3")

    try:
        file_info = await bot.get_file(message.voice.file_id)
        await bot.download_file(file_info.file_path, input_audio_path)

        with open(input_audio_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        user_text = transcription.text

        if not user_text.strip():
            await message.reply("Извини, мне не удалось разобрать слова в голосовом сообщении.")
            return

        response = await client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": user_text}]
        )
        ai_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        new_log = Usage(
            user_id=user_id,
            created_at=datetime.now(),
            tokens=tokens_used
        )
        add_usage(new_log)

        tts_response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=ai_text
        )
        tts_response.stream_to_file(output_audio_path)

        reply_voice = FSInputFile(output_audio_path)
        await message.reply_voice(voice=reply_voice)

    finally:
        if os.path.exists(input_audio_path):
            os.remove(input_audio_path)
        if os.path.exists(output_audio_path):
            os.remove(output_audio_path)

async def process_text_message(message: Message, client: AsyncOpenAI) -> None:
    user_id = message.from_user.id
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message.text}]
    )
    ai_text = response.choices[0].message.content
    tokens_used = response.usage.total_tokens

    new_log = Usage(
        user_id=user_id,
        created_at=datetime.now(),
        tokens=tokens_used
    )
    add_usage(new_log)

    await message.answer(ai_text)