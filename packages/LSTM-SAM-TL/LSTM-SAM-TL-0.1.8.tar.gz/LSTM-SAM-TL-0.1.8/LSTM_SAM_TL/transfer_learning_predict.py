from __future__ import annotations

# === No-retraining transfer-learning PREDICT-ONLY runner ===
# Loads every .h5 model in CWD, runs inference on the given CSV, and
# writes merged predictions CSV under "LSTM-SAM predictions/PRE_EWL_<stem>.csv".
# No comparisons with observations; no metrics.

import os
import warnings
import multiprocessing
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

from .layers import CustomAttentionLayer  # attention layer used by saved models

warnings.filterwarnings("ignore", category=FutureWarning)


def _env_setup(verbose: int):
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    try:
        num_cores = multiprocessing.cpu_count()
        if verbose:
            print(f"[TL-PRED] Number of CPU cores: {num_cores}")
    except Exception:
        pass

    gpus = tf.config.experimental.list_physical_devices("GPU")
    if gpus:
        try:
            tf.config.experimental.set_visible_devices(gpus[0], "GPU")
            tf.config.experimental.set_memory_growth(gpus[0], True)
            if verbose:
                print("[TL-PRED] GPU is being used")
        except RuntimeError as e:
            print(e)


def _normalize_data(X: pd.DataFrame):
    scaler = MinMaxScaler()
    X_norm = scaler.fit_transform(X)
    return X_norm, scaler


def _create_rnn_dataset(X_norm: np.ndarray, lookback: int):
    Xs = []
    for i in range(len(X_norm) - lookback):
        Xs.append(X_norm[i : (i + lookback)])
    return np.array(Xs)


def _extract_lookback_from_filename(filename: str):
    h_pos = filename.find("h")
    if h_pos > 0 and filename[h_pos - 1].isdigit():
        start = h_pos - 2 if h_pos > 1 and filename[h_pos - 2].isdigit() else h_pos - 1
        return int(filename[start:h_pos])
    return None


def _extract_prefix_from_filename(filename: str):
    return filename.split(".h5")[0]


def _append_predictions_csv(
    preds: np.ndarray,
    lookback: int,
    DateTime: pd.DataFrame,
    prefix: str,
    filename: str,
    verbose: int,
):
    """Create/append a single model's prediction column into PRE_EWL_<stem>.csv."""
    dirpath = os.path.dirname(filename)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    indices = np.arange(len(preds.flatten()))
    pred_col = prefix.replace("lstm", "")

    # Align dates (shift forward by lookback)
    idx_adj = indices + lookback
    df = pd.DataFrame(
        {
            "Date": DateTime["Date"].iloc[idx_adj].values,
            "Time (GMT)": DateTime["Time (GMT)"].iloc[idx_adj].values,
            pred_col: preds.flatten()[indices],
        }
    )
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[["Date", "Time (GMT)", pred_col]]

    if not os.path.exists(filename):
        df.to_csv(filename, index=False)
        if verbose:
            print(f"[TL-PRED] Created CSV: {filename}")
    else:
        existing = pd.read_csv(filename)
        existing["Date"] = pd.to_datetime(existing["Date"])
        # drop same prediction col if present, then merge new
        existing = existing.drop(columns=[pred_col], errors="ignore")
        merged = existing.merge(df, on=["Date", "Time (GMT)"], how="left")
        merged.to_csv(filename, index=False)
        if verbose:
            print(f"[TL-PRED] Appended column '{pred_col}' to: {filename}")


def _plot_predictions_only(
    dates: pd.Series,
    preds: np.ndarray,
    filename_prefix: str,
    plots_dir: str,
    verbose: int,
    start_date: Optional[pd.Timestamp],
    end_date: Optional[pd.Timestamp],
):
    """Plot only predicted time series (no actuals; no metrics)."""
    os.makedirs(plots_dir, exist_ok=True)

    # Optionally window the plot
    plot_dates = dates.copy()
    plot_preds = preds.copy()
    if start_date is not None and end_date is not None:
        mask = (plot_dates >= pd.to_datetime(start_date)) & (plot_dates <= pd.to_datetime(end_date))
        plot_dates = plot_dates[mask.values]
        plot_preds = plot_preds[mask.values]

    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    ax.plot(plot_preds, label="Predicted")
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Water level (m)")
    ax.legend(loc="best")
    out_png = os.path.join(plots_dir, f"{filename_prefix}_pred_only.png")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.show()

    if verbose:
        print(f"[TL-PRED] Plot saved: {out_png}")


def transfer_learning_predict(
    data_path: str = "sandy_1992.csv",
    verbose: int = 1,
    start_date: Optional[str] = None,   # optional plotting window start (e.g., "1992-12-08")
    end_date: Optional[str] = None,     # optional plotting window end   (e.g., "1992-12-14")
) -> Dict[str, Any]:
    """
    No-retraining PREDICT-ONLY runner (no metrics; no actual-vs-predicted).
    - Reads `data_path` (expects 'Date' and 'Time (GMT)' + features + target(last) just for scaling).
    - Finds all *.h5 models in CWD.
    - For each model: infers lookback from filename (…b24h…), windows data, runs predict,
      saves a predicted-only time series plot, and merges predictions into
      LSTM-SAM predictions/PRE_EWL_<stem>.csv (one column per model).
    - Returns a dict with the output CSV path and the list of processed models.

    Args:
        data_path: CSV to evaluate (default: 'sandy_1992.csv').
        verbose: 0 = silent, 1 = progress, 2 = keras bars.
        start_date, end_date: optional ISO date strings for plotting window (affects plot only).

    Returns:
        {"output_csv": "<merged csv path>", "models": ["m1.h5", ...]}
    """
    _env_setup(verbose)

    if verbose:
        print(f"[TL-PRED] Loading data from: {data_path}")

    # Load data
    data = pd.read_csv(data_path, header=0, parse_dates=[0])
    DateTime = data[["Date", "Time (GMT)"]]
    core = data.drop(columns=["Date", "Time (GMT)"])

    # NOTE: we still read the last column (assumed target) only to build a scaler
    # so we can inverse-transform predictions to the original units. No comparisons are made.
    X = core.iloc[:, :-1]
    y = core.iloc[:, -1]
    X_norm, _ = _normalize_data(X)
    scaler_y = MinMaxScaler(feature_range=(0, 1))
    y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))  # only for inverse transform of preds

    # Discover models
    all_files = os.listdir()
    model_files = [f for f in all_files if f.endswith(".h5")]
    lookbacks = [_extract_lookback_from_filename(f) for f in model_files]
    prefixes = [_extract_prefix_from_filename(f) for f in model_files]

    if verbose:
        print(f"[TL-PRED] Found {len(model_files)} model(s): {model_files}")

    # Output CSV name based on input stem
    input_stem = os.path.splitext(os.path.basename(data_path))[0]
    merged_csv = os.path.join("LSTM-SAM predictions", f"PRE_EWL_{input_stem}.csv")
    os.makedirs(os.path.dirname(merged_csv), exist_ok=True)
    if verbose:
        print(f"[TL-PRED] Merged predictions CSV: {merged_csv}")

    # Convert optional dates up-front for plotting
    sd = pd.to_datetime(start_date) if start_date is not None else None
    ed = pd.to_datetime(end_date) if end_date is not None else None

    processed_models = []

    for model_file, lookback, prefix in zip(model_files, lookbacks, prefixes):
        if lookback is None:
            if verbose:
                print(f"[TL-PRED] Skipping {model_file}: could not infer lookback from filename.")
            continue

        if verbose:
            print(f"[TL-PRED] >>> Predicting with model: {model_file}")

        # Build model inputs
        X_windows = _create_rnn_dataset(X_norm, lookback)
        # Dates aligned to prediction windows
        dates_pred = DateTime["Date"].iloc[lookback:].reset_index(drop=True)

        try:
            model = load_model(model_file, custom_objects={"CustomAttentionLayer": CustomAttentionLayer})
        except Exception as e:
            print(f"[TL-PRED] Failed to load {model_file}: {e}")
            continue

        # Predict (scaled space) then inverse to original target units
        preds_scaled = model.predict(X_windows, verbose=max(0, verbose - 0))
        preds_orig = scaler_y.inverse_transform(preds_scaled)

        # Plot predicted-only timeseries
        _plot_predictions_only(
            dates_pred, preds_orig, prefix, "Visualization", verbose, sd, ed
        )

        # Append/merge predictions into PRE_EWL_<stem>.csv
        _append_predictions_csv(preds_orig, lookback, DateTime, prefix, merged_csv, verbose)

        processed_models.append(model_file)

    if verbose:
        print("[TL-PRED] Predictions completed!")
    
