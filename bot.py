import os
print("CURRENT WORKING DIRECTORY:", os.getcwd())
print("FILES:", os.listdir("."))
print("ANALYSES CONTENTS:", os.listdir("analyses"))
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from utils import safe_extract_txt, parse_chat
from analyses.poop_analysis import count_poop, analyze_poop_plus_other
from analyses.weekly_analysis import weekly_leaderboards, poop_histogram_by_hour, weekly_poop_chart

BOT_TOKEN = os.environ["BOT_TOKEN"]
MAX_ZIP_SIZE = 200_000


async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    #if not doc.file_name.endswith(".zip"):
    #    await update.message.reply_text("Please send a ZIP file.")
    #    return
    if doc.file_size > MAX_ZIP_SIZE:
        await update.message.reply_text("ZIP file too large.")
        return
    file = await doc.get_file()
    file_bytes = await file.download_as_bytearray()
    try:
        txt = safe_extract_txt(file_bytes)
        df = parse_chat(txt)
        df["poop_count"] = df["message"].str.contains("💩")
        user_emojis_text, leaderboard_text = analyze_poop_plus_other(df)

        await update.message.reply_text("💩 + Emoji per User:\n\n" + user_emojis_text)
        await update.message.reply_text("💩 + Emoji Leaderboard:\n\n" + leaderboard_text)

        leaderboard_week, leaderboard_all = weekly_leaderboards(df)
        await update.message.reply_text(f"📊 Last Week Leaderboard:\n{leaderboard_week}")
        await update.message.reply_text(f"📊 All-Time Leaderboard:\n{leaderboard_all}")

        hist_buf = poop_histogram_by_hour(df)
        weekly_buf = weekly_poop_chart(df)
        await update.message.reply_photo(photo=hist_buf, caption="💩 Messages by Hour")
        await update.message.reply_photo(photo=weekly_buf, caption="Weekly 💩 Messages per User")

    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("Error processing file.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_zip))
    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()