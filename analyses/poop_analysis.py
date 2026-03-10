import pandas as pd
import numpy as np
import io

def count_poop(df):
    df["poop_count"] = df["message"].str.contains("💩", regex=False)
    poop_total = df.groupby("author")["poop_count"].sum().sort_values(ascending=False)
    return poop_total

import re
from collections import defaultdict

def analyze_poop_plus_other(df):

    # Messages containing 💩 AND at least one other emoji
    def has_poop_and_other(message):
        if "💩" not in message:
            return False
        # Check if there is any other emoji character
        emojis = re.findall(r"[\U00010000-\U0010ffff]", message)
        other_emojis = [e for e in emojis if e != "💩"]
        return len(other_emojis) > 0

    df["poop_plus_other"] = df["message"].apply(has_poop_and_other)

    # --- Part 1: User → all co-occurring emojis ---
    user_emojis = defaultdict(set)

    for _, row in df[df["poop_plus_other"]].iterrows():
        message = row["message"]
        user = row["author"]

        emojis = re.findall(r"[\U00010000-\U0010ffff]", message)
        for e in emojis:
            if e != "💩":
                user_emojis[user].add(e)

    # Format output
    user_emojis_text = []
    for user, emojis in user_emojis.items():
        emoji_string = "".join(sorted(emojis))
        user_emojis_text.append(f"{user}:\n{emoji_string}")

    user_emojis_text = "\n\n".join(user_emojis_text)

    # --- Part 2: Leaderboard by occurrences ---
    leaderboard = (
        df[df["poop_plus_other"]]
        .groupby("author")
        .size()
        .sort_values(ascending=False)
    )

    leaderboard_text = "\n".join(
        [f"{user}: {count}" for user, count in leaderboard.items()]
    )

    return user_emojis_text, leaderboard_text

def poop_coupling_heatmap(df, window_minutes=60):

    import matplotlib.pyplot as plt

    poop_df = df[df["poop_count"]].copy()
    poop_df = poop_df.sort_values("timestamp")

    users = poop_df["author"].unique()
    user_index = {u:i for i,u in enumerate(users)}

    matrix = np.zeros((len(users), len(users)))

    window = pd.Timedelta(minutes=window_minutes)

    times = poop_df["timestamp"].values
    authors = poop_df["author"].values

    for i in range(len(poop_df)):
        t1 = times[i]
        a1 = authors[i]

        j = i + 1
        while j < len(poop_df):

            if times[j] - t1 > window:
                break

            a2 = authors[j]

            if a1 != a2:
                matrix[user_index[a1], user_index[a2]] += 1
                matrix[user_index[a2], user_index[a1]] += 1

            j += 1

    plt.figure(figsize=(6,5))

    plt.imshow(matrix)

    plt.colorbar(label="Coupled 💩 events")

    plt.xticks(range(len(users)), users, rotation=45)
    plt.yticks(range(len(users)), users)

    plt.title(f"💩 Poop Coupling (≤ {window_minutes} min)")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return buf