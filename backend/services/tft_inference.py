import torch
import numpy as np
import pandas as pd
import logging
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.metrics import QuantileLoss
from pytorch_forecasting.data.encoders import EncoderNormalizer
from typing import Optional, Dict, Tuple

MAX_ENCODER_LENGTH = 96
MAX_PRED_LENGTH = 1
BATCH_SIZE = 64

KNOWN_REALS = [
    "hour_sin", "hour_cos",
    "day_sin",  "day_cos",
    "m2_sin",   "m2_cos",
    "s2_sin",   "s2_cos",
    "k1_sin",   "k1_cos",
    "hour",     "month",  "day_of_week"
]

PAST_REALS = [
    "water_level_lag_1",  "water_level_lag_2",  "water_level_lag_3",
    "water_level_lag_6",  "water_level_lag_12", "water_level_lag_24",
    "water_level_mean_6h",  "water_level_mean_12h",  "water_level_mean_24h",
    "water_level_std_6h",   "water_level_std_12h",   "water_level_std_24h",
]

_model_cache: Dict[str, TemporalFusionTransformer] = {}

logger = logging.getLogger(__name__)

class RobustTFT(TemporalFusionTransformer):
    def log_prediction(self, x, out, batch_idx, **kwargs):
        try:
            super().log_prediction(x, out, batch_idx, **kwargs)
        except (ValueError, Exception):
            pass

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df["hour_sin"] = np.sin(2 * np.pi * df.index.hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df.index.hour / 24)
    df["day_sin"]  = np.sin(2 * np.pi * df.index.dayofyear / 365.25)
    df["day_cos"]  = np.cos(2 * np.pi * df.index.dayofyear / 365.25)
    
    df["m2_sin"] = np.sin(2 * np.pi * df.index.hour / 12.42)
    df["m2_cos"] = np.cos(2 * np.pi * df.index.hour / 12.42)
    df["s2_sin"] = np.sin(2 * np.pi * df.index.hour / 12.0)
    df["s2_cos"] = np.cos(2 * np.pi * df.index.hour / 12.0)
    df["k1_sin"] = np.sin(2 * np.pi * df.index.hour / 23.93)
    df["k1_cos"] = np.cos(2 * np.pi * df.index.hour / 23.93)
    
    df["hour"]        = df.index.hour
    df["month"]       = df.index.month
    df["day_of_week"] = df.index.dayofweek
    
    for lag in [1, 2, 3, 6, 12, 24]:
        df[f"water_level_lag_{lag}"] = df["water_level"].shift(lag)
        
    for window in [6, 12, 24]:
        df[f"water_level_mean_{window}h"] = df["water_level"].rolling(window, min_periods=1).mean()
        df[f"water_level_std_{window}h"]  = df["water_level"].rolling(window, min_periods=1).std().fillna(0)
        
    df = df.dropna()
    return df

def load_model(checkpoint_path: str) -> RobustTFT:
    if checkpoint_path in _model_cache:
        return _model_cache[checkpoint_path]
        
    logger.info(f"Loading TFT checkpoint from {checkpoint_path}")
    _orig = torch.load
    try:
        torch.load = lambda f, *a, **kw: _orig(f, *a, **{**kw, "weights_only": False})
        ckpt = torch.load(checkpoint_path, map_location="cpu")
        if "pytorch-lightning_version" not in ckpt:
            ckpt["pytorch-lightning_version"] = "1.9.5"
            torch.save(ckpt, checkpoint_path)
        model = RobustTFT.load_from_checkpoint(checkpoint_path, map_location="cpu")
        torch.load = _orig
        
        model.eval()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        
        _model_cache[checkpoint_path] = model
        logger.info(f"Model loaded on {device}")
        return model
    except Exception as e:
        torch.load = _orig
        logger.error(f"Error loading model: {e}")
        raise

def prepare_inference_dataset(df: pd.DataFrame, station_id: str) -> Tuple[TimeSeriesDataSet, pd.DataFrame]:
    df = df.copy()
    
    df = df.set_index("datetime").sort_index()
    df = df[["water_level"]]
    df["water_level"] = df["water_level"].ffill().bfill()
    
    df = df.resample("h").mean()
    df = df.dropna(subset=["water_level"])
    
    df = engineer_features(df)
    
    df = df.reset_index()
    if "index" in df.columns:
        df = df.rename(columns={"index": "datetime"})
    
    df["time_idx"] = list(range(len(df)))
    df["group"] = station_id
    
    if len(df) < MAX_ENCODER_LENGTH + MAX_PRED_LENGTH:
        raise ValueError(f"Not enough data: need at least {MAX_ENCODER_LENGTH + MAX_PRED_LENGTH} rows, got {len(df)}")
        
    dataset = TimeSeriesDataSet(
        df,
        time_idx="time_idx",
        target="water_level",
        group_ids=["group"],
        max_encoder_length=MAX_ENCODER_LENGTH,
        max_prediction_length=MAX_PRED_LENGTH,
        time_varying_known_reals=KNOWN_REALS,
        time_varying_unknown_reals=PAST_REALS + ["water_level"],
        target_normalizer=EncoderNormalizer(),
        add_relative_time_idx=True,
        add_target_scales=True,
        add_encoder_length=True,
    )
    
    return dataset, df

def run_inference(model: RobustTFT, dataset: TimeSeriesDataSet, df: pd.DataFrame, n_steps: int = 168) -> dict:
    val_loader = dataset.to_dataloader(train=False, batch_size=256, num_workers=0)
    output = model.predict(val_loader, mode="quantiles", return_y=True)
    
    q_preds = output.output.cpu().numpy()
    y_true = output.y[0].cpu().numpy()
    
    n = min(n_steps, q_preds.shape[1])
    
    q10 = q_preds[0, :n, 1].tolist()
    q25 = q_preds[0, :n, 2].tolist()
    q50 = q_preds[0, :n, 3].tolist()
    q75 = q_preds[0, :n, 4].tolist()
    q90 = q_preds[0, :n, 5].tolist()
    actuals = y_true[0, :n].tolist()
    
    timestamps = df["datetime"].iloc[-n:].dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist()
    
    return {
        "timestamps": timestamps,
        "q10": q10,
        "q25": q25,
        "q50": q50,
        "q75": q75,
        "q90": q90,
        "actuals": actuals
    }

def get_forecast(station_id: str, observations_df: pd.DataFrame, checkpoint_path: str) -> Optional[dict]:
    try:
        model = load_model(checkpoint_path)
        dataset, df = prepare_inference_dataset(observations_df, station_id)
        result = run_inference(model, dataset, df)
        return result
    except Exception as e:
        logger.error(f"Inference failed for station {station_id}: {e}", exc_info=True)
        return None
