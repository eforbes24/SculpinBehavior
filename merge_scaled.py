#!/usr/bin/env python3
import pandas as pd
import numpy as np
import re
from pathlib import Path

# ==== CONSTANTS ====
midlik_threshold = 0.975    # Midpoint threshold
otherlik_threshold = 0.96   # Nose/Tail/Left/Right threshold

arenax = 1150  # px
arenay = 870   # px
offset_x = 385 # px
offset_y = 106 # px
scale_x = [0.4/arenax, 0.6/arenax]   # [first era], [second era]
scale_y = [0.3/arenay, 0.45/arenay]

# ==== INPUT / OUTPUT (hard-coded) ====
in_path  = Path("C:\\Users\\eforb\\OneDrive\\Desktop\\RESEARCH\\PROJECTS\\SculBehave\\video_analyses\\merged_dlc.csv")
out_path = Path("C:\\Users\\eforb\\OneDrive\\Desktop\\RESEARCH\\PROJECTS\\SculBehave\\video_analyses\\merged_dlc_final.csv")

# ==== Helpers ====
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize columns to:
      id, individual, body_part, x, y, likelihood, [time]
    Drop any columns named like x_px / y_px if present.
    """
    # Drop unwanted pixel columns right away
    drop_cols = [c for c in df.columns if c.lower() in ("x_px", "y_px", "x pix", "y pix", "xpix", "ypix")]
    df = df.drop(columns=drop_cols, errors="ignore")

    # Map lowercase → original
    lc2orig = {c.lower(): c for c in df.columns}

    def pick(*names):
        for n in names:
            if n in lc2orig:
                return lc2orig[n]
        return None

    id_col   = pick("id", "video id", "video_id")
    ind_col  = pick("individual", "ind", "indiv", "individual_id")
    bp_col   = pick("body_part", "bodypart", "body part")
    x_col    = pick("x", "x_val", "xvalue", "x_value")
    y_col    = pick("y", "y_val", "yvalue", "y_value")
    lik_col  = pick("likelihood", "likeli", "conf", "confidence", "prob", "p")
    time_col = pick("time", "t")

    rename_map = {}
    if id_col:   rename_map[id_col] = "id"
    if ind_col:  rename_map[ind_col] = "individual"
    if bp_col:   rename_map[bp_col] = "body_part"
    if x_col:    rename_map[x_col] = "x"
    if y_col:    rename_map[y_col] = "y"
    if lik_col:  rename_map[lik_col] = "likelihood"
    if time_col: rename_map[time_col] = "time"

    out = df.rename(columns=rename_map).copy()

    required = ["id", "individual", "body_part", "x", "y", "likelihood"]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {missing}. Found: {list(out.columns)}")

    out["x"] = pd.to_numeric(out["x"], errors="coerce")
    out["y"] = pd.to_numeric(out["y"], errors="coerce")
    out["likelihood"] = pd.to_numeric(out["likelihood"], errors="coerce")

    out["id"] = out["id"].astype(str).str.strip()
    out["individual"] = out["individual"].astype(str).str.strip()
    out["body_part"] = out["body_part"].astype(str).str.strip()

    return out

def choose_scale_for_id(id_str: str):
    """
    Use first scale if:
      - id is numeric and < 26, OR
      - id starts with one of: 26_, 27_, 28_, 29_
    Else use second scale.
    """
    s = str(id_str).strip()
    for prefix in ("26_", "27_", "28_", "29_"):
        if s.startswith(prefix):
            return scale_x[0], scale_y[0]
    m = re.match(r"\s*(\d+)", s)
    if m and int(m.group(1)) < 26:
        return scale_x[0], scale_y[0]
    return scale_x[1], scale_y[1]

def apply_likelihood_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep rows where:
      - body_part contains 'mid' (any case) and likelihood >= midlik_threshold
      - otherwise likelihood >= otherlik_threshold
    """
    bp = df["body_part"].str.lower()
    is_mid = bp.str.contains("mid")
    keep_mid = is_mid & (df["likelihood"] >= midlik_threshold)
    keep_other = (~is_mid) & (df["likelihood"] >= otherlik_threshold)
    return df[keep_mid | keep_other].copy()

def scale_coords_inplace(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace x,y with scaled meters based on per-row id-derived scale.
    Does NOT create x_px/y_px.
    """
    # Per-row scales
    sx = np.empty(len(df))
    sy = np.empty(len(df))
    ids = df["id"].tolist()
    for i, s in enumerate(ids):
        cx, cy = choose_scale_for_id(s)
        sx[i] = cx
        sy[i] = cy

    df["x"] = (df["x"] - offset_x) * sx
    df["y"] = (df["y"] - offset_y) * sy
    return df

# ==== Main ====
def main():
    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path}")

    raw = pd.read_csv(in_path, low_memory=False)
    std = normalize_columns(raw)

    # Clean early
    std = std.dropna(subset=["x", "y", "likelihood"])

    # Filter by likelihood thresholds
    std = apply_likelihood_filter(std)

    # Scale to meters (no x_px/y_px retained)
    std = scale_coords_inplace(std)

    # Ensure x_px/y_px aren't present (if they were in the input somehow)
    std = std.drop(columns=[c for c in std.columns if c.lower() in ("x_px", "y_px")], errors="ignore")

    # Order columns (time optional)
    ordered = ["id", "individual", "time", "body_part", "x", "y", "likelihood"]
    std = std[[c for c in ordered if c in std.columns] + [c for c in std.columns if c not in ordered]]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    std.to_csv(out_path, index=False)
    print(f"Saved scaled file to: {out_path}")
    print(f"Rows written: {len(std)}")

if __name__ == "__main__":
    main()
