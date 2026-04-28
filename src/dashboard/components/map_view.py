"""PyDeck scatter-plot map of scored parcels."""
from __future__ import annotations

import streamlit as st
import pandas as pd
import pydeck as pdk

from config.settings import DASHBOARD_MAP_ZOOM


def _score_to_rgb(score: float) -> list[int]:
    """Map a 0–100 score to a green→yellow→red gradient."""
    t = max(0.0, min(1.0, score / 100.0))
    if t < 0.5:
        # green → yellow
        r = int(255 * (t * 2))
        g = 255
    else:
        # yellow → red
        r = 255
        g = int(255 * (1 - (t - 0.5) * 2))
    return [r, g, 0, 180]


def render_map(df: pd.DataFrame, score_col: str) -> None:
    """Render a PyDeck scatter-plot map coloured by *score_col*."""
    if df.empty:
        st.info("No properties to display on the map.")
        return

    # Need lat/lon columns
    lat_col = next((c for c in ("latitude", "lat") if c in df.columns), None)
    lon_col = next((c for c in ("longitude", "lon", "lng") if c in df.columns), None)

    if lat_col is None or lon_col is None:
        st.warning("Latitude/longitude columns not found — map cannot be rendered.")
        return

    map_df = df[[lat_col, lon_col, score_col]].copy()
    map_df = map_df.rename(columns={lat_col: "lat", lon_col: "lon"})
    map_df["lat"] = pd.to_numeric(map_df["lat"], errors="coerce")
    map_df["lon"] = pd.to_numeric(map_df["lon"], errors="coerce")
    map_df = map_df.dropna(subset=["lat", "lon"])

    if map_df.empty:
        st.warning("No geocoded properties available for map display.")
        return

    # Add address and change_flag for tooltip if available
    if "address" in df.columns:
        map_df["address"] = df.loc[map_df.index, "address"].values
    else:
        map_df["address"] = ""
    if "change_flag" in df.columns:
        map_df["change_flag"] = df.loc[map_df.index, "change_flag"].fillna("").values
    else:
        map_df["change_flag"] = ""

    map_df["score"] = pd.to_numeric(map_df[score_col], errors="coerce").fillna(0)
    map_df["color"] = map_df["score"].apply(_score_to_rgb)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius=30,
        pickable=True,
        opacity=0.8,
    )

    view_state = pdk.ViewState(
        latitude=float(map_df["lat"].mean()),
        longitude=float(map_df["lon"].mean()),
        zoom=DASHBOARD_MAP_ZOOM,
        pitch=0,
    )

    tooltip = {
        "html": "<b>{address}</b><br/>Score: {score:.0f}<br/>Change: {change_flag}",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))


__all__ = ["render_map"]
