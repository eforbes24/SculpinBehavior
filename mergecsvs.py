#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import numpy as np
import re
import sys

# ====== HARD-CODED SETTINGS ======
INPUT_DIR = Path("C:\\Users\\eforb\\OneDrive\\Desktop\\RESEARCH\\PROJECTS\\SculBehave\\video_analyses")
OUTPUT_FILE = INPUT_DIR / "merged_dlc.csv"
FPS = 30.0
PATTERN = "*DLC.csv"
# =================================

# ====== UNIQUE FISH INDICES ======
timestamps = [
    ['1', [[]]], # Vid 1
    ['2', [[]]], # Vid 2
    ['3', [[]]], # Vid 3
    ['4_1', [[0, 360], [400, 475]]], # Vid 4_1
    ['4_2', [[]]], # Vid 4_2
    ['5_1', [[15, 320]]], # Vid 5_1
    ['5_2', [[0, 65], [75, 115], [188, 263], [269, 304]]], # Vid 5_2
    ['6', [[144, 180], [165, 247], [255, 420]]], # Vid 6
    ['7', [[]]], # Vid 7
    ['8_1', [[10, 312], [315, 420]]], # Vid 8_1
    ['8_2', [[0, 146], [160, 400]]], # Vid 8_2
    ['9_1', [[100, 300], [305, 395]]], # Vid 9_1
    ['9_2', [[]]], # Vid 9_2
    ['10_1', [[]]], # Vid 10_1
    ['10_2', [[60, 170], [180, 450]]], # Vid 10_2
    ['11_1', [[0, 410], [420, 470]]], # Vid 11_1
    ['11_2', [[]]], # Vid 11_2
    ['11_3', [[60, 313], [330, 420]]], # Vid 11_3
    ['12', [[0, 250], [270, 420]]], # Vid 12
    ['13', [[0, 150], [180, 375], [380, 440]]], # Vid 13
    ['14_1', [[0, 260], [270, 355]]], # Vid 14_1
    ['14_2', [[0, 230], [250, 360]]], # Vid 14_2
    ['15', [[0, 85], [100, 280]]], # Vid 15
    ['16_1', [[0, 230], [260, 345]]], # Vid 16_1
    ['16_2', [[40, 300]]], # Vid 16_2
    ['17', [[0, 30], [34, 48]]], # Vid 17
    ['18', [[0, 52], [60, 90]]], # Vid 18
    ['19', [[0, 1]]], # Vid 19 (omitted - caddisfly larvae)
    ['20', [[65, 120], [130, 220], [240, 350]]], # Vid 20 [34, 54], 
    ['21', [[0, 190], [200, 223], [230, 290]]], # Vid 21
    ['22_1', [[0, 105], [120, 180], [205, 310], [320, 450]]], # Vid 22_1
    ['22_2', [[20, 240], [260, 330]]], # Vid 22_2
    ['23', [[0, 75], [90, 250]]], # Vid 23
    ['24', [[15, 270], [315, 360], [365, 440], [445, 500]]], # Vid 24
    ['25_1', [[60, 130], [140, 275], [285, 390], [400, 560]]], # Vid 25_1
    ['25_2', [[]]], # Vid 25_2
    ['25_3', [[]]], # Vid 25_3
    ['25_4', [[]]], # Vid 25_4
    ['26', [[]]], # Vid 26
    ['27', [[0, 80], [100, 150]]], # Vid 27
    ['28', [[]]], # Vid 28
    ['29', [[0, 140], [190, 260], [290, 415]]], # Vid 29
    ['30', [[]]], # Vid 30
    ['31', [[0, 90], [110, 180], [185, 210]]], # Vid 31
    ['32', [[0, 210], [220, 300], [360, 580]]], # Vid 32
    ['33_1', [[0, 140], [160, 340], [360, 420], [465, 485], [495, 590]]], # Vid 33_1
    ['33_2', [[0, 24], [30, 70], [85, 130]]], # Vid 33_2
    ['33_3', [[]]], # Vid 33_3
    ['34_1', [[0, 90], [120, 210], [220, 350]]], # Vid 34_1
    ['34_2', [[10, 150], [165, 270], [290, 330]]], # Vid 34_2
    ['35_1', [[]]], # Vid 35_1
    ['35_2', [[0, 435], [450, 555]]], # Vid 35_2
    ['35_3', [[0, 50], [65, 153]]], # Vid 35_3
    ['36_1', [[0, 120], [140, 200], [225, 575]]], # Vid 36_1
    ['36_2', [[0, 170], [195, 270], [280, 370], [390, 595]]], # Vid 36_2
    ['37', [[0, 120], [130, 270], [300, 520]]], # Vid 37
    ['38', [[10, 140], [150, 270], [300, 410]]], # Vid 38
    ['39_1', [[0, 290], [300, 510], [525, 570]]], # Vid 39_1
    ['39_2', [[0, 300], [330, 395]]], # Vid 39_2
    ['40', [[]]], # Vid 40
    ['41', [[]]], # Vid 41
    ['42', [[]]], # Vid 42
    ['43', [[]]], # Vid 43
    ['44', [[]]], # Vid 44
    ['45', [[]]], # Vid 45
    ['46', [[]]], # Vid 46
    ['47', [[]]], # Vid 47
    ['48', [[]]], # Vid 48
    ['49', [[]]], # Vid 49
    ['50', [[]]], # Vid 50
    ['51', [[]]], # Vid 51
    ['52', [[]]], # Vid 52
    ['53', [[]]], # Vid 53
    ['54', [[]]], # Vid 54
    ['55', [[]]], # Vid 55
    ['56', [[]]], # Vid 56
    ['57', [[]]], # Vid 57
    ['58', [[]]], # Vid 58
    ['59', [[]]], # Vid 59
    ['60', [[]]], # Vid 60
    ['61', [[]]], # Vid 61

]
# =================================

def video_id_from_filename(path: Path) -> str:
    stem = path.stem
    if stem.endswith("DLC"):
        stem = stem[:-3]
    return stem


def read_dlc_csv(p: Path) -> pd.DataFrame:
    """Try 4-level, then 3-level, then flat header."""
    # 4-level (scorer, individual, bodypart, coord)
    try:
        df = pd.read_csv(p, header=[0, 1, 2, 3], low_memory=False)
        if isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 4:
            return df
    except Exception:
        pass
    # 3-level (scorer, bodypart, coord)
    try:
        df = pd.read_csv(p, header=[0, 1, 2], low_memory=False)
        if isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 3:
            return df
    except Exception:
        pass
    # Flat fallback → synthesize 3-level
    df = pd.read_csv(p, low_memory=False)
    tuples = []
    for c in df.columns:
        if "_" in c:
            bp, coord = c.rsplit("_", 1)
            tuples.append(("", bp, coord))  # (scorer, bodypart, coord)
        else:
            tuples.append(("", c, ""))
    df.columns = pd.MultiIndex.from_tuples(tuples)
    return df


def norm_coord(c) -> str:
    c = str(c).strip().lower()
    if c in ("x", "x_val"):
        return "x"
    if c in ("y", "y_val"):
        return "y"
    if c in ("likelihood", "p", "prob", "conf", "confidence"):
        return "likelihood"
    return c


def normalize_columns(df: pd.DataFrame, fps: float, vid_id: str) -> pd.DataFrame:
    """Return long format with columns: Time, Individual, Bodypart, x_val, y_val, likelihood, ID."""
    if not isinstance(df.columns, pd.MultiIndex):
        raise ValueError("Expected MultiIndex columns.")

    nlevels = df.columns.nlevels

    if nlevels == 4:
        # (scorer, individual, bodypart, coord)
        cols = [(str(s), str(indiv), str(bp), norm_coord(co))
                for s, indiv, bp, co in df.columns]
        df.columns = pd.MultiIndex.from_tuples(cols, names=["scorer", "Individual", "Bodypart", "coord"])
        wanted = {"x", "y", "likelihood"}
        df = df.loc[:, [c for c in df.columns if c[3] in wanted]]

        # Stack Individual and Bodypart to rows; columns are coords
        long = df.stack(level=["Individual", "Bodypart"])

        # Ensure required coord columns are present
        for c in ["x", "y", "likelihood"]:
            if c not in long.columns.get_level_values(-1):
                long[(c,)] = np.nan

        long.columns = [c[-1] for c in long.columns]
        long = long[["x", "y", "likelihood"]]
        long = long.reset_index(names=["row", "Individual", "Bodypart"])

    elif nlevels == 3:
        # (scorer, bodypart, coord) → synthesize Individual = "ind1"
        cols = [(str(s), str(bp), norm_coord(co)) for s, bp, co in df.columns]
        df.columns = pd.MultiIndex.from_tuples(cols, names=["scorer", "Bodypart", "coord"])
        wanted = {"x", "y", "likelihood"}
        df = df.loc[:, [c for c in df.columns if c[2] in wanted]]

        long = df.stack(level="Bodypart")

        for c in ["x", "y", "likelihood"]:
            if c not in long.columns.get_level_values(-1):
                long[(c,)] = np.nan

        long.columns = [c[-1] for c in long.columns]
        long = long[["x", "y", "likelihood"]]
        long = long.reset_index(names=["row", "Bodypart"])
        long["Individual"] = "ind1"

    else:
        raise ValueError(f"Unsupported column levels: {nlevels}")

    # Compute Time from frame index
    long["Time"] = (long["row"].astype(float) / float(fps)).round(2)
    long = long.drop(columns=["row"], errors="ignore")

    # Rename coords
    long = long.rename(columns={"x": "x_val", "y": "y_val"})

    # Add ID and final column order
    long["ID"] = vid_id
    long = long[["Time", "Individual", "Bodypart", "x_val", "y_val", "likelihood", "ID"]]
    return long


_indiv_num_re = re.compile(r"(\d+)$")

def indiv_sort_key(indiv: str) -> tuple:
    """
    Sort key for Individual labels like 'ind1', 'ind2', ..., 'ind10'.
    Returns (prefix, number) where number is int if found, else large number to put unknowns last.
    """
    s = str(indiv)
    m = _indiv_num_re.search(s)
    if m:
        return (s.rstrip(m.group(1)), int(m.group(1)))
    return (s, 10**9)  # unknown suffix goes last


def main():
    files = sorted(INPUT_DIR.glob(PATTERN))
    if not files:
        print(f"No CSVs found in folder: {INPUT_DIR} with pattern {PATTERN}")
        sys.exit(1)

    frames = []
    for i, p in enumerate(files):
        try:
            dfw = read_dlc_csv(p)
            vid_id = video_id_from_filename(p)
            long = normalize_columns(dfw, fps=FPS, vid_id=vid_id)
            
            # Extract timestamp ranges for this video
            # Find matching timestamp entry by video ID
            ranges = None
            for ts_entry in timestamps:
                if ts_entry[0] == vid_id:
                    ranges = ts_entry[1]
                    break
            
            if ranges:
                subset_id = 0
                for time_range in ranges:
                    if not time_range:
                        # Use all data if no time range specified
                        subset = long.copy()
                        subset["ID"] = f"{vid_id}_seq{subset_id}"
                        frames.append(subset)
                        subset_id += 1
                    else:
                        start_frame, end_frame = time_range
                        # Filter rows within frame range
                        mask = (long["Time"] >= start_frame) & (long["Time"] <= end_frame)
                        subset = long[mask].copy()
                        if not subset.empty:
                            # Create unique ID: original_id + subset number
                            subset["ID"] = f"{vid_id}_seq{subset_id}"
                            frames.append(subset)
                            subset_id += 1
            else:
                frames.append(long)
            
            print("Processed", p.name)
        except Exception as e:
            print("[WARN] Skipping", p.name, ":", e)

    if not frames:
        print("No files processed successfully.")
        sys.exit(2)

    out = pd.concat(frames, ignore_index=True)

    # Order rows: by ID, then Individual (ind1, ind2, ...), then Time
    tmp_key = out["Individual"].map(lambda s: indiv_sort_key(s)[1])
    out = out.assign(_indiv_num=tmp_key).sort_values(by=["ID", "_indiv_num", "Time"], kind="stable")
    out = out.drop(columns=["_indiv_num"])

    out.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {len(out):,} rows → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()



# def main():
#     files = sorted(INPUT_DIR.glob(PATTERN))
#     if not files:
#         print(f"No CSVs found in folder: {INPUT_DIR} with pattern {PATTERN}")
#         sys.exit(1)

#     frames = []
#     for i, p in enumerate(files):
#         try:
#             dfw = read_dlc_csv(p)
#             vid_id = video_id_from_filename(p)
#             long = normalize_columns(dfw, fps=FPS, vid_id=vid_id)
            
#             # Extract timestamp ranges for this video
#             if i < len(timestamps):
#                 ranges = list(timestamps)[i]
#                 subset_id = 0
#                 for start_frame, end_frame in ranges:
#                     # Filter rows within frame range
#                     mask = (long["Time"] >= start_frame / FPS) & (long["Time"] <= end_frame / FPS)
#                     subset = long[mask].copy()
#                     if not subset.empty:
#                         # Create unique ID: original_id + subset number
#                         subset["ID"] = f"{vid_id}_{subset_id}"
#                         frames.append(subset)
#                         subset_id += 1
#             else:
#                 frames.append(long)
            
#             print("Processed", p.name)
#         except Exception as e:
#             print("[WARN] Skipping", p.name, ":", e)

#     if not frames:
#         print("No files processed successfully.")
#         sys.exit(2)

#     out = pd.concat(frames, ignore_index=True)

#     # Order rows: by ID, then Individual (ind1, ind2, ...), then Time
#     tmp_key = out["Individual"].map(lambda s: indiv_sort_key(s)[1])
#     out = out.assign(_indiv_num=tmp_key).sort_values(by=["ID", "_indiv_num", "Time"], kind="stable")
#     out = out.drop(columns=["_indiv_num"])

#     out.to_csv(OUTPUT_FILE, index=False)
#     print(f"Wrote {len(out):,} rows → {OUTPUT_FILE}")


# if __name__ == "__main__":
#     main()
