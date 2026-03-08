import os
import zipfile
import shutil
import tempfile
import pandas as pd

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]

MAX_ZIP_SIZE = 200_000       # 200 KB
MAX_UNZIPPED_SIZE = 2_000_000  # 2 MB


def safe_extract(zip_path, extract_to):

    total_size = 0

    with zipfile.ZipFile(zip_path) as z:

        for member in z.infolist():

            # protect against path traversal
            member_path = os.path.abspath(
                os.path.join(extract_to, member.filename)
            )

            if not member_path.startswith(os.path.abspath(extract_to)):
                raise Exception("Unsafe file path detected")

            total_size += member.file_size

            if total_size > MAX_UNZIPPED_SIZE:
                raise Exception("ZIP too large after extraction")

        z.extractall(extract_to)


async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document.file_name.endswith(".zip"):
        await update.message.reply_text("Please send a ZIP file.")
        return

    if document.file_size > MAX_ZIP_SIZE:
        await update.message.reply_text("ZIP file too large.")
        return

    temp_dir = tempfile.mkdtemp()

    try:

        zip_path = os.path.join(temp_dir, "data.zip")

        file = await document.get_file()
        await file.download_to_drive(zip_path)

        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir)

        safe_extract(zip_path, extract_dir)

        csv_file = None

        for f in os.listdir(extract_dir):
            if f.endswith(".csv"):
                csv_file = os.path.join(extract_dir, f)
                break

        if not csv_file:
            await update.message.reply_text("No CSV file found in ZIP.")
            return

        df = pd.read_csv(csv_file)

        print("CSV loaded")
        print(df.head())

        await update.message.reply_text("Data received successfully.")

    except Exception as e:

        print("Error:", e)
        await update.message.reply_text("Error processing file.")

    finally:

        shutil.rmtree(temp_dir, ignore_errors=True)


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.Document.ALL, handle_zip)
    )

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()