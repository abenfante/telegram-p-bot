import pandas as pd

def count_poop(df):
    df["poop_count"] = df["message"].str.contains("💩", regex=False)
    poop_total = df.groupby("author")["poop_count"].sum().sort_values(ascending=False)
    return poop_total

def poop_plus_other(df):
    df["poop_plus_other"] = df["message"].apply(
        lambda m: "💩" in m and any(c for c in m if c != "💩" and ord(c) > 1000)
    )
    return df[df["poop_plus_other"]]