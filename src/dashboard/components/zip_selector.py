"""ZIP code selector with data freshness check."""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

from config.chicago_zips import CHICAGO_ZIPS, all_zip_labels
from config.settings import scored_path_for_zip, DATA_STALENESS_DAYS


def _data_status(zip_code: str) -> tuple[str, datetime | None]:
    """Return ('ready' | 'stale' | 'missing', last_modified_datetime)."""
    p = scored_path_for_zip(zip_code)
    if not p.exists():
        return "missing", None
    mtime = datetime.fromtimestamp(os.path.getmtime(p))
    age = datetime.now() - mtime
    if age > timedelta(days=DATA_STALENESS_DAYS):
        return "stale", mtime
    return "ready", mtime


def render_zip_selector() -> str | None:
    """Render the ZIP code selector and return the selected ZIP.

    Returns None if no data is available and the user hasn't triggered ingestion.
    When ingestion is needed, this function runs it inline with a progress display.
    """
    st.header("Location")

    # County selector (Cook only for now)
    st.selectbox("County", ["Cook County"], index=0, key="county_select")

    # ZIP selector
    zip_items = all_zip_labels()
    labels = [label for _, label in zip_items]
    zips = [z for z, _ in zip_items]

    default_idx = zips.index("60610") if "60610" in zips else 0
    selected_label = st.selectbox(
        "ZIP Code",
        labels,
        index=default_idx,
        key="zip_select",
    )
    zip_code = zips[labels.index(selected_label)]

    # Check data status
    status, mtime = _data_status(zip_code)

    if status == "ready":
        st.success(
            f"Data loaded  --  Last refreshed: {mtime.strftime('%b %d, %Y')}",
            icon="✅",
        )
        return zip_code

    elif status == "stale":
        st.warning(
            f"Data last refreshed: {mtime.strftime('%b %d, %Y')} "
            f"({(datetime.now() - mtime).days} days ago)",
            icon="⚠️",
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Use existing data", key="use_existing", use_container_width=True):
                return zip_code
        with col2:
            if st.button("Refresh Data", key="refresh_data", type="primary", use_container_width=True):
                _run_ingestion(zip_code)
                return zip_code
        return zip_code

    else:  # missing
        st.info(f"No data available for ZIP {zip_code}.", icon="ℹ️")
        if st.button(
            f"Get Data for {zip_code}",
            key="get_data",
            type="primary",
            use_container_width=True,
        ):
            _run_ingestion(zip_code)
            return zip_code
        return None


def _run_ingestion(zip_code: str) -> None:
    """Run the pipeline inline with a Streamlit progress bar."""
    from main import run_pipeline

    progress_bar = st.progress(0, text=f"Starting pipeline for ZIP {zip_code}...")

    def _on_progress(step: int, total: int, msg: str):
        progress_bar.progress(step / total, text=msg)

    try:
        run_pipeline(zip_code, progress_callback=_on_progress)
        progress_bar.progress(1.0, text="Done!")
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")


__all__ = ["render_zip_selector"]
