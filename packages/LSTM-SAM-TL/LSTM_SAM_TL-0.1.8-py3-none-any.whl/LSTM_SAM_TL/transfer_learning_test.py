from __future__ import annotations

# === No-retraining transfer-learning TEST runner (mirrors your script) ===
# Loads every .h5 model in CWD, runs inference on the given CSV, plots, and
# writes merged predictions CSV under "LSTM-SAM predictions/".

import os
import warnings
import multiprocessing
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
from tensorflow.keras.models import load_model

from .layers import CustomAttentionLayer  # attention layer used by saved models

warnings.filterwarnings("ignore", category=FutureWarning)


def _env_setup(verbose: int):
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    try:
        num_cores = multiprocessing.cpu_count()
        if verbose:
            print(f"[TL-TEST] Number of CPU cores: {num_cores}")
    except Exception:
        pass

    gpus = tf.config.experimental.list_physical_devices("GPU")
    if gpus:
        try:
            tf.config.experimental.set_visible_devices(gpus[0], "GPU")
            tf.config.experimental.set_memory_growth(gpus[0], True)
            if verbose:
                print("[TL-TEST] GPU is being used")
        except RuntimeError as e:
            print(e)


def _normalize_data(X: pd.DataFrame):
    scaler = MinMaxScaler()
    X_norm = scaler.fit_transform(X)
    return X_norm, scaler


def _create_rnn_dataset(X_norm: np.ndarray, y_scaled: np.ndarray, lookback: int):
    Xs, ys = [], []
    for i in range(len(X_norm) - lookback):
        Xs.append(X_norm[i : (i + lookback)])
        ys.append(y_scaled[i + lookback])
    return np.array(Xs), np.array(ys)


def kge(y_true: np.ndarray, y_pred: np.ndarray):
    r, _ = pearsonr(y_true, y_pred)
    alpha = np.std(y_pred) / np.std(y_true)
    beta = np.mean(y_pred) / np.mean(y_true)
    return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)


def nse(y_true: np.ndarray, y_pred: np.ndarray):
    num = np.sum((y_true - y_pred) ** 2)
    den = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - num / den


def amb(y_true: np.ndarray, y_pred: np.ndarray):
    return np.mean(np.abs(y_true - y_pred))


def willmott_skill(y_true: np.ndarray, y_pred: np.ndarray):
    obs_mean = np.mean(y_true)
    num = np.sum((y_true - y_pred) ** 2)
    den = np.sum((np.abs(y_pred - obs_mean) + np.abs(y_true - obs_mean)) ** 2)
    return 1 - num / den


def _evaluate_and_plot(
    model: tf.keras.Model,
    X_test_rnn: np.ndarray,
    y_test_rnn: np.ndarray,
    dates: pd.Series,
    scaler_y: MinMaxScaler,
    filename_prefix: str,
    plots_dir: str,
    verbose: int,
    start_date: Optional[pd.Timestamp],
    end_date: Optional[pd.Timestamp],
):
    # Evaluate and predict 
    _ = model.evaluate(X_test_rnn, y_test_rnn, verbose=0)
    preds = model.predict(X_test_rnn, verbose=verbose)

    # Inverse scaling 
    y_true = scaler_y.inverse_transform(y_test_rnn)
    y_pred = scaler_y.inverse_transform(preds)

    # Window for plotting/metrics (filtering only affects visuals/metrics)
    y_test_filtered = y_true
    test_predictions_filtered = y_pred
    if start_date is not None and end_date is not None:
        mask = (dates >= pd.to_datetime(start_date)) & (dates <= pd.to_datetime(end_date))
        y_test_filtered = y_true[mask.values]
        test_predictions_filtered = y_pred[mask.values]

    # Metrics on filtered subset
    rmse = np.sqrt(mean_squared_error(y_test_filtered, test_predictions_filtered))
    kge_v = kge(y_test_filtered.flatten(), test_predictions_filtered.flatten())
    nse_v = nse(y_test_filtered.flatten(), test_predictions_filtered.flatten())
    d_v = willmott_skill(y_test_filtered.flatten(), test_predictions_filtered.flatten())
    amb_v = amb(y_test_filtered.flatten(), test_predictions_filtered.flatten())

    metrics_text = [
        f"RMSE: {rmse:.4f}",
        f"KGE: {kge_v:.4f}",
        f"NSE: {nse_v:.4f}",
        "Willmott's d: {:.4f}".format(d_v),
        f"mBias: {amb_v:.4f}",
    ]

    # Side-by-side plots
    os.makedirs(plots_dir, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Time series WITH metrics in legend (phantom lines)
    ax1.plot(y_test_filtered, "r--", label="Actual")
    ax1.plot(test_predictions_filtered, label="Predicted")
    for text in metrics_text:
        ax1.plot([], [], " ", label=text)
    ax1.set_xlabel("Time (h)")
    ax1.set_ylabel("Water level (m)")
    ax1.legend(loc="best")

    # 1:1 scatter
    mn = min(y_test_filtered.min(), test_predictions_filtered.min())
    mx = max(y_test_filtered.max(), test_predictions_filtered.max())
    ax2.plot([mn, mx], [mn, mx], "k--", label="1:1 line")
    ax2.scatter(y_test_filtered, test_predictions_filtered, alpha=0.7, label="Predicted")
    ax2.scatter(y_test_filtered, y_test_filtered, s=5, label="Actual")
    ax2.set_xlabel("Actual (m)")
    ax2.set_ylabel("Predicted (m)")
    ax2.legend(loc="best")

    plt.tight_layout()
    out_png = os.path.join(plots_dir, f"{filename_prefix}_combined.png")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.show()

    if verbose:
        print(f"[TL-TEST] Plot saved: {out_png}")

    return rmse, kge_v, nse_v, d_v, amb_v, y_true, y_pred


def _extract_lookback_from_filename(filename: str):
    h_pos = filename.find("h")
    if h_pos > 0 and filename[h_pos - 1].isdigit():
        start = h_pos - 2 if h_pos > 1 and filename[h_pos - 2].isdigit() else h_pos - 1
        return int(filename[start:h_pos])
    return None


def _extract_prefix_from_filename(filename: str):
    return filename.split(".h5")[0]


def _extract_and_save_all(
    test_pred: np.ndarray,
    y_true: np.ndarray,
    lookback: int,
    DateTime: pd.DataFrame,
    prefix: str,
    filename: str,
    verbose: int,
):
    dirpath = os.path.dirname(filename)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    indices = np.arange(len(y_true.flatten()))
    pred_col = prefix.replace("lstm", "")
    df = pd.DataFrame(
        {
            "Actual water level": y_true.flatten()[indices],
            pred_col: test_pred.flatten()[indices],
        }
    )

    idx_adj = indices + lookback
    df["Date"] = DateTime["Date"].iloc[idx_adj].values
    df["Time (GMT)"] = DateTime["Time (GMT)"].iloc[idx_adj].values
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[["Date", "Time (GMT)", "Actual water level", pred_col]]

    if not os.path.exists(filename):
        df.to_csv(filename, index=False)
        if verbose:
            print(f"[TL-TEST] Created CSV: {filename}")
    else:
        existing = pd.read_csv(filename)
        existing["Date"] = pd.to_datetime(existing["Date"])
        existing = existing.drop(columns=[pred_col], errors="ignore")
        merged = existing.merge(
            df[["Date", "Time (GMT)", pred_col]], on=["Date", "Time (GMT)"], how="left"
        )
        merged.to_csv(filename, index=False)
        if verbose:
            print(f"[TL-TEST] Appended column '{pred_col}' to: {filename}")

    return df


def transfer_learning_test(
    data_path: str = "sandy_1992.csv",
    verbose: int = 1,
    start_date: Optional[str] = None,   # <-- NEW: set plotting window start (e.g., "1992-12-08")
    end_date: Optional[str] = None,     # <-- NEW: set plotting window end   (e.g., "1992-12-14")
) -> Dict[str, Any]:
    """
    No-retraining test runner (verbose-enabled).
    - Reads `data_path` (expects 'Date' and 'Time (GMT)' columns + features + target last).
    - Finds all *.h5 models in CWD.
    - For each model: infers lookback from filename (…b24h…), windows data, runs predict,
      makes plots under Visualization/, and merges predictions into LSTM-SAM predictions/DAT_EWL_<stem>.csv
    - Returns a dict of per-model metrics.

    Args:
        data_path: CSV to evaluate (default: 'sandy_1992.csv').
        verbose: 0 = silent, 1 = progress, 2 = more detailed keras bars.
        start_date, end_date: optional ISO date strings to limit the plotted/evaluated window.

    Returns:
        {"metrics": {model_file: {"rmse":..., "kge":..., "nse":..., "willmott_d":..., "mbias":...}, ...},
         "output_csv": "<merged csv path>"}
    """
    _env_setup(verbose)

    if verbose:
        print(f"[TL-TEST] Loading data from: {data_path}")

    # Load data
    data = pd.read_csv(data_path, header=0, parse_dates=[0])
    DateTime = data[["Date", "Time (GMT)"]]
    data = data.drop(columns=["Date", "Time (GMT)"])
    if verbose:
        print("[TL-TEST] Target station data imported! Loading LSTM-SAM models...")

    # Output dirs
    plots_dir = "Visualization"
    os.makedirs(plots_dir, exist_ok=True)
    out_dir = "LSTM-SAM predictions"
    os.makedirs(out_dir, exist_ok=True)

    # Preprocess
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]
    X_norm, _ = _normalize_data(X)
    scaler_y = MinMaxScaler(feature_range=(0, 1))
    y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))

    # Discover models
    all_files = os.listdir()
    model_files = [f for f in all_files if f.endswith(".h5")]
    lookbacks = [_extract_lookback_from_filename(f) for f in model_files]
    prefixes = [_extract_prefix_from_filename(f) for f in model_files]

    if verbose:
        print(f"[TL-TEST] Found {len(model_files)} model(s): {model_files}")

    # Output CSV name based on input stem
    input_stem = os.path.splitext(os.path.basename(data_path))[0]
    merged_csv = os.path.join(out_dir, f"DAT_EWL_{input_stem}.csv")
    if verbose:
        print(f"[TL-TEST] Merged predictions CSV: {merged_csv}")

    per_model_metrics: Dict[str, Dict[str, float]] = {}

    # Convert optional dates up-front (or defaults you used before)
    sd = pd.to_datetime(start_date) if start_date is not None else None
    ed = pd.to_datetime(end_date) if end_date is not None else None

    for model_file, lookback, prefix in zip(model_files, lookbacks, prefixes):
        if lookback is None:
            if verbose:
                print(f"[TL-TEST] Skipping {model_file}: could not infer lookback from filename.")
            continue

        if verbose:
            print(f"[TL-TEST] >>> Evaluating model: {model_file}")

        X_test, y_test = _create_rnn_dataset(X_norm, y_scaled, lookback)
        dates_test = DateTime["Date"].iloc[lookback:].reset_index(drop=True)

        try:
            model = load_model(model_file, custom_objects={"CustomAttentionLayer": CustomAttentionLayer})
        except Exception as e:
            print(f"[TL-TEST] Failed to load {model_file}: {e}")
            continue

        rmse, kge_v, nse_v, d_v, amb_v, y_true, y_pred = _evaluate_and_plot(
            model, X_test, y_test, dates_test, scaler_y, prefix, plots_dir,
            verbose=max(0, verbose - 0), start_date=sd, end_date=ed
        )

        # Instead reuse what we already computed:
        _extract_and_save_all(
            y_pred,              # predictions (inverse-scaled)
            y_true,              # ground truth (inverse-scaled)
            lookback, DateTime, prefix, merged_csv, verbose)

        per_model_metrics[model_file] = {
            "rmse": float(rmse),
            "kge": float(kge_v),
            "nse": float(nse_v),
            "willmott_d": float(d_v),
            "mbias": float(amb_v),
        }

    if verbose:
        print("[TL-TEST] Predictions completed!")
    
