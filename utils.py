import zipfile
import io
import pandas as pd
import re
from datetime import datetime

MAX_UNZIPPED_SIZE = 5_000_000

def safe_extract_txt(file_bytes):
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
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%y %H:%M")
            data.append({"timestamp": timestamp, "author": author, "message": message})
    df = pd.DataFrame(data)
    start_date = datetime(2026, 2, 1)
    df["week_number"] = ((df["timestamp"] - start_date).dt.days // 7 + 1)
    return df