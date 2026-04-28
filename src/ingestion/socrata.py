"""Paginated Socrata API client."""
from __future__ import annotations

import time
import requests
import pandas as pd


def fetch_socrata(
    domain: str,
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = 50_000,
) -> pd.DataFrame:
    url = f"https://{domain}/resource/{dataset_id}.json"
    all_rows: list[dict] = []
    offset = 0

    while True:
        params: dict = {"$limit": limit, "$offset": offset}
        if where:
            params["$where"] = where
        if select:
            params["$select"] = select
        if order:
            params["$order"] = order

        resp = requests.get(url, params=params, timeout=120)
        resp.raise_for_status()
        rows = resp.json()

        if isinstance(rows, dict):
            raise RuntimeError(f"Socrata error: {rows}")
        if not rows:
            break

        all_rows.extend(rows)
        print(f"  ... {len(all_rows):,} rows")

        if len(rows) < limit:
            break
        offset += limit
        time.sleep(1)

    if not all_rows:
        return pd.DataFrame()
    return pd.DataFrame(all_rows)
