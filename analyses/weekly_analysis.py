import matplotlib.pyplot as plt
import io

def weekly_leaderboards(df):
    # Determine latest fully completed week
    last_week = df["week_number"].max()
    target_week = last_week - 1      # last completed week
    previous_week = last_week - 2     # week before that

    # Safety check
    if target_week < 1:
        return "Not enough data for weekly leaderboard.", ""

    # Data for target week
    target_df = df[df["week_number"] == target_week]
    target_poop = (
        target_df.groupby("author")["poop_count"]
        .sum()
        .sort_values(ascending=False)
    )

    # Data for previous week (for comparison arrows)
    prev_df = df[df["week_number"] == previous_week]
    prev_poop = prev_df.groupby("author")["poop_count"].sum()

    # Build leaderboard with arrows
    leaderboard = []

    for user, count in target_poop.items():
        prev_count = prev_poop.get(user, 0)

        if count > prev_count:
            emoji = "⬆️"
        elif count < prev_count:
            emoji = "⬇️"
        else:
            emoji = "➡️"

        leaderboard.append(f"{emoji} {user}: {count}")

    # All-time leaderboard (unchanged)
    all_time = (
        df.groupby("author")["poop_count"]
        .sum()
        .sort_values(ascending=False)
    )

    all_time_text = "\n".join(
        [f"{user}: {count}" for user, count in all_time.items()]
    )

    return "\n".join(leaderboard), all_time_text


def poop_histogram_by_hour(df):
    poop_df = df[df["poop_count"]].copy()
    plt.figure(figsize=(8, 4))
    poop_df["hour"] = poop_df["timestamp"].dt.hour
    poop_df["hour"].hist(bins=24, rwidth=0.8)
    plt.xlabel("Hour of Day")
    plt.ylabel("Cacchine")
    plt.title("Distribuzione oraria")
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
    plt.xlabel("Week Number")
    plt.ylabel("💩 Messages")
    plt.title("Cacchine settimanali individuali")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf