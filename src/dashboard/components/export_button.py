"""CSV export download button."""
from __future__ import annotations

import streamlit as st
import pandas as pd


def render_export_button(df: pd.DataFrame) -> None:
    """Render a download button that streams *df* as CSV."""
    csv = df.to_csv(index=False).encode("utf-8")
    row_count = len(df)

    st.download_button(
        label=f"Download {row_count:,} properties as CSV",
        data=csv,
        file_name="listings_export.csv",
        mime="text/csv",
    )


__all__ = ["render_export_button"]
