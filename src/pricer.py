"""Car deal pricer.

Reads scraped listings, trains a RandomForest price model per car model,
computes a `delta` (predicted − actual) for cars shown on the web, and
writes results to the `priced` table.

Usage:
    python -m src.pricer xval   # cross-validate on training data
    python -m src.pricer real   # score live listings and write to DB
"""

import logging
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from .db import drop_if_exists, get_engine
from .utils import get_xval_indices

logger = logging.getLogger(__name__)

MODELS = {"accord", "camry", "civic", "corolla", "silverado"}
NUM_ON_WEB = 150
FEATURE_COLS = ["year", "miles"]


def _get_mae(prediction: np.ndarray, target: np.ndarray) -> float:
    return float(np.abs(prediction - target).mean())


def _exclude_outliers(df: pd.DataFrame, col: str, lo: float, hi: float) -> pd.DataFrame:
    return df[(df[col] >= lo) & (df[col] <= hi)].reset_index(drop=True)


def main(mode: str) -> None:
    if mode not in ("xval", "real"):
        raise ValueError("mode must be 'xval' or 'real'")

    engine = get_engine()

    full = pd.read_sql(
        f"SELECT model, year, miles, price, url, body, title, date "
        f"FROM scraped "
        f"WHERE area='sfbay' AND model IN {tuple(MODELS)}",
        con=engine,
    )

    full = _exclude_outliers(full, "year", 1990, 2030)
    full = _exclude_outliers(full, "miles", 1_000, 250_000)
    full = _exclude_outliers(full, "price", 500, 75_000)

    # Most recent NUM_ON_WEB listings per model are shown on the web UI
    full = full.sort_values("date", ascending=False).reset_index(drop=True)
    full["on_web"] = full.index < NUM_ON_WEB

    delta_rows: list[dict] = []

    for model in MODELS:
        df = full[full["model"] == model][FEATURE_COLS + ["price", "url", "on_web"]].copy()
        if len(df) < 10:
            logger.warning("Too few records for '%s' (%d), skipping", model, len(df))
            continue

        logger.info("Pricing model: %s (%d records)", model, len(df))

        # Training uses cars NOT shown on web to avoid leakage
        train = df[~df["on_web"]]
        test = df[df["on_web"]]

        train_X = train[FEATURE_COLS].values
        train_y = train["price"].values

        predictor = RandomForestRegressor(n_estimators=100, min_samples_split=20, random_state=42)

        if mode == "xval":
            train_idx, val_idx = get_xval_indices(len(train_X))
            predictor.fit(train_X[train_idx], train_y[train_idx])
            preds = predictor.predict(train_X[val_idx])
            logger.info("%s validation MAE = $%.0f", model, _get_mae(preds, train_y[val_idx]))

        elif mode == "real":
            if len(train_X) == 0:
                logger.warning("No training data for '%s', skipping", model)
                continue
            predictor.fit(train_X, train_y)
            if len(test) == 0:
                continue
            preds = predictor.predict(test[FEATURE_COLS].values)
            delta = preds - test["price"].values
            for url, d in zip(test["url"].values, delta):
                delta_rows.append({"url": url, "delta": d})

    if mode == "real":
        delta_frame = pd.DataFrame(delta_rows)
        result = full.merge(delta_frame, on="url", how="inner")
        drop_if_exists(engine, "priced")
        result.to_sql("priced", engine, if_exists="append", index=False)
        logger.info("Wrote %d rows to 'priced'", len(result))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mode = sys.argv[1] if len(sys.argv) > 1 else "real"
    main(mode)
