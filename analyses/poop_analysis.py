import pandas as pd

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