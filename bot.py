import os
import zipfile
import io
import pandas as pd

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]

MAX_ZIP_SIZE = 200_000
MAX_UNZIPPED_SIZE = 2_000_000


def safe_extract(file_bytes):
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        total_size = 0
        csv_content = None

        for member in z.infolist():
            total_size += member.file_size
            if total_size > MAX_UNZIPPED_SIZE:
                raise Exception("ZIP too large")

            if member.filename.endswith(".csv"):
                csv_content = z.read(member.filename)

        if csv_content is None:
            raise Exception("No CSV found")

        return csv_content


async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document.file_name.endswith(".zip"):
        await update.message.reply_text("Please send a ZIP file.")
        return

    if document.file_size > MAX_ZIP_SIZE:
        await update.message.reply_text("ZIP file too large.")
        return

    file = await document.get_file()
    file_bytes = await file.download_as_bytearray()

    csv_bytes = safe_extract(file_bytes)

    df = pd.read_csv(io.BytesIO(csv_bytes))
    print(df.head())

    await update.message.reply_text("Data received successfully.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.Document.ALL, handle_zip)
    )

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()