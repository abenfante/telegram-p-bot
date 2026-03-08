# worker_bot.py
import os
import zipfile
import io
import pandas as pd
from telegram import Bot, Update
from telegram.constants import ParseMode
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
bot = Bot(BOT_TOKEN)

MAX_ZIP_SIZE = 200_000       # 200 KB
MAX_UNZIPPED_SIZE = 2_000_000  # 2 MB

def safe_extract(file_bytes, max_unzip_size=MAX_UNZIPPED_SIZE):
    """Safely unzip in memory and return CSV content"""
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        total_size = 0
        csv_content = None

        for member in z.infolist():
            total_size += member.file_size
            if total_size > max_unzip_size:
                raise Exception("ZIP too large after extraction")
            if member.filename.endswith(".csv"):
                csv_content = z.read(member.filename)
        if csv_content is None:
            raise Exception("No CSV found")
        return csv_content

async def handle_request(request):
    """Cloudflare Worker entry point"""
    try:
        body = await request.json()
        update = Update.de_json(body, bot)

        # Only handle documents (ZIP files)
        if not update.message or not update.message.document:
            return Response("No document found", status=200)

        doc = update.message.document
        if not doc.file_name.endswith(".zip"):
            bot.send_message(update.message.chat.id, "Please send a ZIP file.")
            return Response("Done", status=200)

        if doc.file_size > MAX_ZIP_SIZE:
            bot.send_message(update.message.chat.id, "ZIP file too large.")
            return Response("Done", status=200)

        # Download file from Telegram
        file_bytes = bot.get_file(doc.file_id).download_as_bytearray()
        csv_bytes = safe_extract(file_bytes)

        df = pd.read_csv(io.BytesIO(csv_bytes))
        print(df.head())

        bot.send_message(update.message.chat.id, "Data received successfully.", parse_mode=ParseMode.MARKDOWN)
        return Response("OK", status=200)

    except Exception as e:
        print("Error:", e)
        return Response("Error", status=200)