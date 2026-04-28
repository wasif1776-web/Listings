"""Propensity scoring engine — loads weights from YAML and scores properties."""
from __future__ import annotations

from pathlib import Path

import yaml
import pandas as pd
import numpy as np


def _eval_condition(series: pd.Series, condition: str, full_df: pd.DataFrame) -> pd.Series:
    """Evaluate a scoring condition against a column, returning a boolean Series."""
    condition = condition.strip()
    numeric = pd.to_numeric(series, errors="coerce")

    if condition == "high":
        threshold = numeric.quantile(0.75)
        return numeric >= threshold

    if condition == "low":
        threshold = numeric.quantile(0.25)
        return numeric <= threshold

    if condition.startswith("between"):
        parts = condition.split()
        lo, hi = float(parts[1]), float(parts[2])
        return (numeric >= lo) & (numeric <= hi)

    if condition.startswith(">="):
        return numeric >= float(condition[2:].strip())
    if condition.startswith("<="):
        return numeric <= float(condition[2:].strip())
    if condition.startswith(">"):
        return numeric > float(condition[1:].strip())
    if condition.startswith("<"):
        return numeric < float(condition[1:].strip())
    if condition.startswith("!="):
        val = condition[2:].strip()
        if val in ("True", "true"):
            return series.astype(str).str.lower() != "true"
        if val in ("False", "false"):
            return series.astype(str).str.lower() != "false"
        return series.astype(str) != val
    if condition.startswith("=="):
        val = condition[2:].strip()
        if val in ("True", "true"):
            return series.astype(str).str.lower().isin(["true", "1", "1.0"])
        if val in ("False", "false"):
            return series.astype(str).str.lower().isin(["false", "0", "0.0"])
        return series.astype(str).str.strip() == val

    return pd.Series(False, index=series.index)


def score_use_case(
    df: pd.DataFrame,
    signals: list[dict],
    use_case: str,
) -> pd.Series:
    """Compute a 0-100 score for one use case."""
    max_points = sum(s["points"] for s in signals)
    if max_points == 0:
        return pd.Series(0.0, index=df.index)

    raw_score = pd.Series(0.0, index=df.index)

    for signal_def in signals:
        col = signal_def["signal"]
        condition = str(signal_def["condition"])
        points = signal_def["points"]

        if col not in df.columns:
            continue

        hit = _eval_condition(df[col], condition, df)
        hit = hit.fillna(False)
        raw_score += hit.astype(float) * points

    normalized = (raw_score / max_points * 100).clip(0, 100)
    return normalized


def score_all(df: pd.DataFrame, weights_path: str | Path | None = None) -> pd.DataFrame:
    """Score properties across all 10 use cases defined in scoring_weights.yaml."""
    if weights_path is None:
        weights_path = Path(__file__).resolve().parents[2] / "config" / "scoring_weights.yaml"

    with open(weights_path) as f:
        weights = yaml.safe_load(f)

    df = df.copy()

    score_col_map = {
        "likely_to_sell": "score_likely_to_sell",
        "likely_to_buy": "score_likely_to_buy",
        "downsize": "score_downsize",
        "upsize": "score_upsize",
        "near_retirement": "score_near_retirement",
        "relocation_risk": "score_relocation_risk",
        "school_district_movers": "score_school_district_movers",
        "investor": "score_investor",
        "likely_to_rent_out": "score_likely_to_rent_out",
        "upgrade_renters": "score_upgrade_renters",
    }

    for use_case, signals in weights.items():
        col_name = score_col_map.get(use_case, f"score_{use_case}")
        df[col_name] = score_use_case(df, signals, use_case)

        vals = df[col_name]
        active_signals = sum(1 for s in signals if s["signal"] in df.columns)
        total_signals = len(signals)
        nonzero = (vals > 0).sum()
        print(
            f"  {col_name}: signals={active_signals}/{total_signals}, "
            f"nonzero={nonzero:,}/{len(df):,}, "
            f"mean={vals.mean():.1f}, unique={vals.nunique()}"
        )

    return df
