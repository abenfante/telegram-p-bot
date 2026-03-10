import io
import numpy as np
import pandas as pd

def compute_leaderboards(df):

    last_week = df["week_number"].max()
    last_completed = last_week - 1

    if last_completed < 1:
        return "Not enough data.", ""

    # ---------------------------
    # Weekly leaderboard (NO arrows)
    # ---------------------------
    weekly_df = df[df["week_number"] == last_completed]

    weekly_scores = (
        weekly_df.groupby("author")["poop_count"]
        .sum()
        .sort_values(ascending=False)
    )

    weekly_text = "\n".join(
        [f"{user}: {count}" for user, count in weekly_scores.items()]
    )

    # ---------------------------
    # Overall leaderboard (comparison)
    # ---------------------------
    overall_current = (
        df[df["week_number"] <= last_completed]
        .groupby("author")["poop_count"]
        .sum()
        .sort_values(ascending=False)
    )

    overall_previous = (
        df[df["week_number"] < last_completed]
        .groupby("author")["poop_count"]
        .sum()
    )

    # Convert previous totals into ranking
    previous_rank = overall_previous.sort_values(ascending=False)
    previous_positions = {
        user: rank for rank, user in enumerate(previous_rank.index)
    }

    current_rank = overall_current
    current_positions = {
        user: rank for rank, user in enumerate(current_rank.index)
    }

    overall_text_lines = []

    for user, count in current_rank.items():

        if user in previous_positions:
            old_pos = previous_positions[user]
            new_pos = current_positions[user]

            if new_pos < old_pos:
                arrow = "⬆️"
            elif new_pos > old_pos:
                arrow = "⬇️"
            else:
                arrow = "➡️"
        else:
            arrow = "🆕"

        overall_text_lines.append(f"{arrow} {user}: {count}")

    overall_text = "\n".join(overall_text_lines)

    return weekly_text, overall_text

def poop_histogram_by_hour(df):
    import matplotlib.pyplot as plt
    poop_df = df[df["poop_count"]].copy()

    # Extract hour
    poop_df["hour"] = poop_df["timestamp"].dt.hour

    # Count messages per hour
    hourly_counts = poop_df["hour"].value_counts().sort_index()

    # Force all 24 hours to exist (0–23)
    hourly_counts = hourly_counts.reindex(range(24), fill_value=0)

    plt.figure(figsize=(8,4))

    plt.bar(hourly_counts.index, hourly_counts.values)

    plt.xticks(range(24))  # Ensure every hour label appears
    plt.xlabel("A che ora")
    plt.ylabel("Quanto spesso")
    plt.title("Come è spalmata la ... durante la giornata")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    del poop_df
    return buf


def weekly_poop_chart(df):
    import matplotlib.pyplot as plt
    poop_df = df[df["poop_count"]]
    weekly = poop_df.groupby(["week_number", "author"])["poop_count"].sum().unstack(fill_value=0)
    plt.figure(figsize=(10, 5))
    weekly.plot(kind="bar")
    plt.xlabel("Settimana")
    plt.ylabel("Numero")
    plt.title("Cacchine settimanali individuali")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf


def poop_heatmap(df):

    import matplotlib.pyplot as plt

    poop_df = df[df["poop_count"]].copy()

    poop_df["hour"] = poop_df["timestamp"].dt.hour
    poop_df["weekday"] = poop_df["timestamp"].dt.weekday  # Monday = 0

    heatmap = np.zeros((7, 24))

    for _, row in poop_df.iterrows():
        heatmap[row["weekday"], row["hour"]] += 1

    plt.figure(figsize=(10,4))

    plt.imshow(heatmap, aspect="auto")

    plt.colorbar(label= "Numero di sedute")

    plt.xticks(range(24))
    plt.yticks(
        range(7),
        ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    )

    plt.xlabel("Hour of Day")
    plt.ylabel("Day of Week")
    plt.title("Activity Heatmap")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return buf


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