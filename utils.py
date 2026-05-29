from sqlalchemy import select
from models import Session, Usage
from io import BytesIO


def add_usage(usage: Usage) -> None:
    with Session() as session:
        try:
            session.add(usage)
        except Exception:
            session.rollback()
            raise
        else:
            session.commit()

def get_usage(tg_id: int) -> int:
    statement = select(Usage).where(Usage.tg_id == tg_id)

    with Session() as session:
        db_objects = session.scalars(statement).all()

    return sum(row.tokens for row in db_objects)

async def message_text(message, client) -> None:
    response = await client.responses.create(
                model="gpt-5.5",
                input=message.text,
            )

    await message.answer(response.output_text)
    return response.usage.total_tokens

async def voice_message_text(message, bot, client) -> None:
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
    return response.usage.total_tokens