import matplotlib.pyplot as plt
import io

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


import io
import matplotlib.pyplot as plt

def poop_histogram_by_hour(df):

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

    return buf


def weekly_poop_chart(df):
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