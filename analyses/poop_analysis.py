import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import networkx as nx

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


def normalized_poop_graph(df, window_minutes=60, threshold=1.2):

    import matplotlib.pyplot as plt

    poop_df = df[df["poop_count"]].copy()
    poop_df = poop_df.sort_values("timestamp")

    users = poop_df["author"].unique()
    user_index = {u:i for i,u in enumerate(users)}

    raw_matrix = np.zeros((len(users), len(users)))

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
                raw_matrix[user_index[a1], user_index[a2]] += 1
                raw_matrix[user_index[a2], user_index[a1]] += 1

            j += 1

    counts = poop_df["author"].value_counts()
    total_poops = len(poop_df)

    G = nx.Graph()

    for u in users:
        G.add_node(u)

    for i,u1 in enumerate(users):
        for j,u2 in enumerate(users):

            if j <= i:
                continue

            observed = raw_matrix[i,j]

            expected = (counts[u1] * counts[u2]) / total_poops

            if expected == 0:
                continue

            score = observed / expected

            if score >= threshold:
                G.add_edge(u1, u2, weight=score)

    pos = nx.spring_layout(G, seed=42)

    edges = G.edges(data=True)
    weights = [d["weight"]*2 for (_,_,d) in edges]

    plt.figure(figsize=(7,6))

    nx.draw_networkx_nodes(G, pos, node_size=1200)
    nx.draw_networkx_labels(G, pos)

    nx.draw_networkx_edges(
        G,
        pos,
        width=weights
    )

    edge_labels = {(u,v):f"{d['weight']:.2f}" for u,v,d in edges}

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels
    )

    plt.title(f"💩 Normalized Poop Coupling Network (≤ {window_minutes} min)")
    plt.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close()

    return buf