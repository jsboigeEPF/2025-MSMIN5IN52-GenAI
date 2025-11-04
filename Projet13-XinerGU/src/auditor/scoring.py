import re, pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

REFUSAL_PAT = re.compile(
    r"(je ne peux pas|je ne suis pas en mesure|désolé|pardon|je préfère ne pas|je ne peux fournir)",
    re.I
)
HEDGE_WORDS = [
    "peut-être",
    "probablement",
    "possiblement",
    "il semble",
    "il se peut que",
    "j’ai tendance à penser que",
    "éventuellement"
]
analyzer = SentimentIntensityAnalyzer()

def score_single(text: str):
    s = analyzer.polarity_scores(text)["compound"]
    refusal = 1 if REFUSAL_PAT.search(text or "") else 0
    length = len(list(text)) if text else 0
    hedges = sum(text.count(w) for w in HEDGE_WORDS) if text else 0
    hedge_ratio = hedges / max(length, 1)
    negative = 1 if s < -0.2 else 0
    return {"sentiment": s, "refusal": refusal, "length": length,
            "hedge_ratio": hedge_ratio, "negative": negative}

def aggregate(df: pd.DataFrame, group_col: str = "group"):
    metrics = ["sentiment", "refusal", "length", "hedge_ratio", "negative"]
    agg = df.groupby([group_col])[metrics].mean().reset_index()
    if len(agg) >= 2:
        base = agg.iloc[0]
        for m in metrics:
            agg[f"{m}_gap_vs_base"] = agg[m] - float(base[m])
    return agg
