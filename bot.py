import os
import zipfile
import io
import re
import pandas as pd
from datetime import datetime

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
        txt_content = None

        for member in z.infolist():
            total_size += member.file_size

            if total_size > MAX_UNZIPPED_SIZE:
                raise Exception("ZIP too large after extraction.")

            if member.filename.endswith(".txt"):
                txt_content = z.read(member.filename)

        if txt_content is None:
            raise Exception("No .txt file found in ZIP.")

        return txt_content.decode("utf-8", errors="ignore")

def parse_chat(text):

    pattern = r"(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - (.*?): (.*)"

    data = []

    for line in text.split("\n"):
        match = re.match(pattern, line)
        if match:
            date_str, time_str, author, message = match.groups()

            timestamp = datetime.strptime(
                f"{date_str} {time_str}", "%d/%m/%y %H:%M"
            )

            data.append({
                "timestamp": timestamp,
                "author": author,
                "message": message
            })

    return pd.DataFrame(data)
# ---------------------------
# Message Handler
# ---------------------------
async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document


    if document.file_size > MAX_ZIP_SIZE:
        await update.message.reply_text("ZIP file too large.")
        return

    # Download file
    file = await document.get_file()
    file_bytes = await file.download_as_bytearray()

    # Extract CSV safely
    try:
        txt_content = safe_extract(file_bytes)

        df = parse_chat(txt_content)

        print("Parsed messages:", len(df))
        print(df.head())

        await update.message.reply_text(
            f"Data received successfully.\nMessages parsed: {len(df)}"
        )

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