import matplotlib.pyplot as plt


def weekly_leaderboards(df):
    last_week = df["week_number"].max()
    last_week_df = df[df["week_number"] == last_week]
    last_week_poop = last_week_df.groupby("author")["poop_count"].sum().sort_values(ascending=False)

    all_time = df.groupby("author")["poop_count"].sum().sort_values(ascending=False)

    prev_week_df = df[df["week_number"] == last_week - 1]
    prev_week_poop = prev_week_df.groupby("author")["poop_count"].sum()

    leaderboard_last_week = []
    for user, count in last_week_poop.items():
        prev_count = prev_week_poop.get(user, 0)
        emoji = "⬆️" if count > prev_count else "⬇️" if count < prev_count else "➡️"
        leaderboard_last_week.append(f"{emoji} {user}: {count}")
    return "\n".join(leaderboard_last_week), "\n".join([f"{user}: {count}" for user, count in all_time.items()])


def poop_histogram_by_hour(df):
    poop_df = df[df["poop_count"]]
    plt.figure(figsize=(8, 4))
    poop_df["hour"] = poop_df["timestamp"].dt.hour
    poop_df["hour"].hist(bins=24, rwidth=0.8)
    plt.xlabel("Hour of Day")
    plt.ylabel("💩 Messages")
    plt.title("💩 Messages Distribution by Hour")
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
    plt.title("Weekly 💩 Messages per User")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf