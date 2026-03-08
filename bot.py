import os
import zipfile
import io
import pandas as pd

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# Get token from environment variable
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Security limits
MAX_ZIP_SIZE = 200_000       # 200 KB
MAX_UNZIPPED_SIZE = 2_000_000  # 2 MB


# ---------------------------
# Safe ZIP extraction
# ---------------------------
def safe_extract(file_bytes):
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        total_size = 0
        csv_content = None

        for member in z.infolist():
            total_size += member.file_size

            # Prevent zip bombs
            if total_size > MAX_UNZIPPED_SIZE:
                raise Exception("ZIP too large after extraction.")

            # Only accept CSV files
            if member.filename.endswith(".txt"):
                csv_content = z.read(member.filename)

        if csv_content is None:
            raise Exception("No CSV file found in ZIP.")

        return csv_content


# ---------------------------
# Message Handler
# ---------------------------
async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document.file_name.endswith(".zip"):
        await update.message.reply_text("Please send a ZIP file.")
        return

    if document.file_size > MAX_ZIP_SIZE:
        await update.message.reply_text("ZIP file too large.")
        return

    # Download file
    file = await document.get_file()
    file_bytes = await file.download_as_bytearray()

    # Extract CSV safely
    try:
        csv_bytes = safe_extract(file_bytes)

        # Read CSV
        df = pd.read_csv(io.BytesIO(csv_bytes))

        print("CSV preview:")
        print(df.head())

        await update.message.reply_text("Data received successfully.")

    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("Error processing file.")


# ---------------------------
# Main function
# ---------------------------
def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.Document.ALL, handle_zip)
    )

    print("Bot running...")

    app.run_polling()


# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    main()