import os
import gc
print("CURRENT WORKING DIRECTORY:", os.getcwd())
print("FILES:", os.listdir("."))
print("ANALYSES CONTENTS:", os.listdir("analyses"))
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from utils import safe_extract_txt, parse_chat
from analyses.poop_analysis import count_poop, analyze_poop_plus_other, normalized_poop_graph
from analyses.weekly_analysis \
    import compute_leaderboards, poop_histogram_by_hour, weekly_poop_chart, poop_heatmap

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

        await update.message.reply_text("Cacche speciali:\n\n" + user_emojis_text)
        await update.message.reply_text("Classifica cacche speciali:\n\n" + leaderboard_text)

        weekly_text, overall_text = compute_leaderboards(df)

        await update.message.reply_text(
            f"📊 Classifica della settimana:\n\n{weekly_text}"
        )

        await update.message.reply_text(
            f"🏆 Classifica totale:\n\n{overall_text}"
        )

        hist_buf = poop_histogram_by_hour(df)
        weekly_buf = weekly_poop_chart(df)
        heatmap_img = poop_heatmap(df)
        #coupling_img = normalized_poop_graph(df, window_minutes=20, threshold= 1.2)
        await update.message.reply_photo(photo=hist_buf, caption="💩🕛")
        await update.message.reply_photo(photo=weekly_buf, caption="Come è andata rispetto a prima? 🤔")
        await update.message.reply_photo(heatmap_img)
        #await update.message.reply_photo(coupling_img)
        del df
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