from __future__ import annotations

from typing import Optional, Dict, Any, List
import math
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional, BatchNormalization, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.losses import MeanAbsoluteError, MeanSquaredError
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from keras_tuner import BayesianOptimization, HyperModel

from .layers import CustomAttentionLayer
from .utils import normalize_xy, create_rnn_dataset


def _set_global_seed(seed: int):
    np.random.seed(seed)
    tf.random.set_seed(seed)


def _resolve_loss(loss: str):
    loss = (loss or "mae").lower()
    if loss == "mae":
        return MeanAbsoluteError(), ["mse"]
    if loss == "mse":
        return MeanSquaredError(), ["mae"]
    raise ValueError(f"loss must be 'mae' or 'mse', got: {loss!r}")


class _CVHyperModel(HyperModel):
    def __init__(self, lookback: int, n_features: int, n_outputs: int = 1, loss: str = "mae"):
        self.input_shape = (lookback, n_features)
        self.n_outputs = n_outputs
        self.loss_obj, self.metrics_list = _resolve_loss(loss)

    def build(self, hp):
        m = Sequential()

        # Block 1 (only here we pass input_shape)
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_1", 32, 512, step=32),
            activation="tanh",
            return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_1", 1e-6, 1e-3, sampling="log")),
            input_shape=self.input_shape,
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_1", 0.1, 0.5, step=0.1)))

        # Block 2
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_2", 32, 512, step=32),
            activation="tanh",
            return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_2", 1e-6, 1e-3, sampling="log")),
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_2", 0.1, 0.5, step=0.1)))

        # Block 3
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_3", 32, 512, step=32),
            activation="tanh",
            return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_3", 1e-6, 1e-3, sampling="log")),
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_3", 0.1, 0.5, step=0.1)))

        m.add(CustomAttentionLayer(hp.Float("emphasis_factor", 1.0, 2.0, step=0.1)))
        m.add(Flatten())
        m.add(Dense(self.n_outputs))

        m.compile(
            loss=self.loss_obj,
            optimizer=Adam(hp.Float("learning_rate", 1e-4, 1e-2, sampling="log")),
            metrics=self.metrics_list,
        )
        return m


def TSCV_model(
    csv_path: str,
    lookback: int = 24,
    n_splits: int = 10,
    epochs: int = 300,
    batch_size: int = 128,
    validation_split: float = 0.2,  # used for the final fit only
    patience: int = 5,
    max_trials: int = 10,
    loss: str = "mae",
    seed: int = 42,
    save_model_path: Optional[str] = None,
    model_name: Optional[str] = None,  # auto name: {model_name}{batch_size}b{lookback}hCV.h5
    return_model: bool = False,
    verbose: int = 1,
) -> Dict[str, Any]:
    """
    True time-series CV:
      1) Chronological tuner split inside the 80% training chunk.
      2) Expanding-window TimeSeriesSplit across the 80% training chunk for CV metrics.
      3) Final fit on the full 80% training windows; 20% holdout for test.

    Saving behavior:
      - If `save_model_path` is provided, save to that exact path.
      - Else if `model_name` is provided, save to f"{model_name}{batch_size}b{lookback}hCV.h5".
      - Else, do not save.
    """
    _set_global_seed(seed)

    if verbose:
        print(f"[TSCV] Loading data from: {csv_path}")

    data = pd.read_csv(csv_path, header=0, parse_dates=[0])
    dt_cols = [c for c in ("Date", "Time (GMT)") if c in data.columns]
    core = data.drop(columns=dt_cols) if dt_cols else data
    X = core.iloc[:, :-1].to_numpy()
    y = core.iloc[:, -1].to_numpy()

    if verbose:
        print(f"[TSCV] Data shape X:{X.shape} y:{y.shape} | lookback={lookback} | n_splits={n_splits}")

    # Scale full series
    Xn, yn, x_scaler, y_scaler = normalize_xy(X, y)

    # 80/20 chronological split -> final holdout is last 20%
    train_size = int(len(Xn) * 0.8)
    X_train, X_test = Xn[:train_size], Xn[train_size:]
    y_train, y_test = yn[:train_size], yn[train_size:]

    # --------- Chronological tuner split inside training chunk ----------
    # e.g., first 80% of training for tuner-train, last 20% for tuner-val (no leakage)
    tuner_cut = int(len(X_train) * 0.8)
    X_tn, X_tv = X_train[:tuner_cut], X_train[tuner_cut:]
    y_tn, y_tv = y_train[:tuner_cut], y_train[tuner_cut:]

    # Window the tuner sets AFTER splitting
    X_tn_rnn, y_tn_rnn = create_rnn_dataset(X_tn, y_tn, lookback)
    X_tv_rnn, y_tv_rnn = create_rnn_dataset(X_tv, y_tv, lookback)

    if verbose:
        print(f"[TSCV] Tuner windows  X_tn_rnn:{X_tn_rnn.shape}  y_tn_rnn:{y_tn_rnn.shape} | "
              f"X_tv_rnn:{X_tv_rnn.shape}  y_tv_rnn:{y_tv_rnn.shape}")

    # Tune with chronological validation set
    n_features = Xn.shape[1]
    tuner = BayesianOptimization(
        _CVHyperModel(lookback=lookback, n_features=n_features, loss=loss),
        objective="val_loss",
        max_trials=max_trials,
        seed=seed,
        project_name="Trials_tscv",
        overwrite=True,
    )
    es = EarlyStopping(monitor="val_loss", patience=patience, mode="min", restore_best_weights=True)

    tuner.search(
        X_tn_rnn, y_tn_rnn,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_tv_rnn, y_tv_rnn),   # IMPORTANT: chronological, not random split
        callbacks=[es],
        verbose=verbose,
    )
    best_hps = tuner.get_best_hyperparameters(1)[0]

    if verbose:
        print("[TSCV] Best hyperparameters found:")
        print({
            "units_1": best_hps.get("units_1"),
            "units_2": best_hps.get("units_2"),
            "units_3": best_hps.get("units_3"),
            "dropout_1": best_hps.get("dropout_1"),
            "dropout_2": best_hps.get("dropout_2"),
            "dropout_3": best_hps.get("dropout_3"),
            "learning_rate": best_hps.get("learning_rate"),
            "emphasis_factor": best_hps.get("emphasis_factor"),
        })
        print(f"[TSCV] Running {n_splits}-fold expanding-window CV with best hyperparameters...")

    # --------- Expanding-window CV across the 80% training chunk ----------
    # We split on raw X_train/y_train, then window INSIDE each fold to avoid leakage.
    tscv = TimeSeriesSplit(n_splits=n_splits)
    fold_scores: List[Dict[str, float]] = []
    for fold_idx, (tr_idx, va_idx) in enumerate(tscv.split(X_train), start=1):
        if verbose:
            print(f"[TSCV] Fold {fold_idx}/{n_splits}: "
                  f"train idx {tr_idx[0]}–{tr_idx[-1]}, val idx {va_idx[0]}–{va_idx[-1]}")

        X_tr, X_va = X_train[tr_idx], X_train[va_idx]
        y_tr, y_va = y_train[tr_idx], y_train[va_idx]

        # Window AFTER splitting
        X_tr_rnn, y_tr_rnn = create_rnn_dataset(X_tr, y_tr, lookback)
        X_va_rnn, y_va_rnn = create_rnn_dataset(X_va, y_va, lookback)

        if verbose:
            print(f"[TSCV]  -> windowed fold shapes  X_tr_rnn:{X_tr_rnn.shape}  X_va_rnn:{X_va_rnn.shape}")

        m = tuner.hypermodel.build(best_hps)
        m.fit(
            X_tr_rnn, y_tr_rnn,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_va_rnn, y_va_rnn),
            callbacks=[es],
            verbose=verbose,
        )
        eval_vals = m.evaluate(X_va_rnn, y_va_rnn, verbose=0)
        fold_scores.append({"val_loss": float(eval_vals[0]), "val_metric": float(eval_vals[1])})

        if verbose:
            print(f"[TSCV]  -> fold {fold_idx} val_loss={eval_vals[0]:.5f}, val_metric={eval_vals[1]:.5f}")

    # --------- Final model on full training windows ----------
    if verbose:
        print("[TSCV] Training final model on full training windows...")

    # Build full training windows
    X_train_rnn, y_train_rnn = create_rnn_dataset(X_train, y_train, lookback)
    # For final fit we can still monitor a small chronological tail of the train set
    tail = max(int(len(X_train) * 0.1), lookback + 1)
    X_final_tr, X_final_val = X_train[:-tail], X_train[-tail:]
    y_final_tr, y_final_val = y_train[:-tail], y_train[-tail:]
    X_final_tr_rnn, y_final_tr_rnn = create_rnn_dataset(X_final_tr, y_final_tr, lookback)
    X_final_val_rnn, y_final_val_rnn = create_rnn_dataset(X_final_val, y_final_val, lookback)

    model = tuner.hypermodel.build(best_hps)
    model.fit(
        X_final_tr_rnn, y_final_tr_rnn,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_final_val_rnn, y_final_val_rnn),
        callbacks=[es],
        verbose=verbose,
    )

    # --------- Holdout test on last 20% ----------
    if verbose:
        print("[TSCV] Evaluating on holdout test...")

    X_test_rnn, y_test_rnn = create_rnn_dataset(X_test, y_test, lookback)
    test_pred = model.predict(X_test_rnn, verbose=verbose)
    test_pred_orig = y_scaler.inverse_transform(test_pred)
    y_all_orig = y_scaler.inverse_transform(yn)

    start = train_size + lookback
    mse = mean_squared_error(y_all_orig[start:], test_pred_orig)
    mae = mean_absolute_error(y_all_orig[start:], test_pred_orig)
    rmse = math.sqrt(mse)
    r2 = r2_score(y_all_orig[start:], test_pred_orig)

    # Save model (priority: explicit path > auto name)
    saved_path = None
    if save_model_path:
        saved_path = save_model_path
    elif model_name:
        saved_path = f"{model_name}{batch_size}b{lookback}hCV.h5"

    if saved_path:
        if verbose:
            print(f"[TSCV] Saving model to: {saved_path}")
        model.save(saved_path)

    if verbose:
        print("[TSCV] Done. Holdout metrics:", {"mse": float(mse), "rmse": float(rmse), "mae": float(mae), "r2": float(r2)})

    result: Dict[str, Any] = {
        "cv_folds": fold_scores,
        "best_hyperparams": {
            "units_1": best_hps.get("units_1"),
            "units_2": best_hps.get("units_2"),
            "units_3": best_hps.get("units_3"),
            "dropout_1": best_hps.get("dropout_1"),
            "dropout_2": best_hps.get("dropout_2"),
            "dropout_3": best_hps.get("dropout_3"),
            "learning_rate": best_hps.get("learning_rate"),
            "emphasis_factor": best_hps.get("emphasis_factor"),
        },
        "holdout_metrics": {"mse": float(mse), "rmse": float(rmse), "mae": float(mae), "r2": float(r2)},
        "y_test_pred": test_pred_orig.flatten().tolist(),
    }
    if saved_path:
        result["saved_model_path"] = saved_path
    if return_model:
        result["model"] = model
    return result
