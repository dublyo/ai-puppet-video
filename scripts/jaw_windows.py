#!/usr/bin/env python3
"""Measure when a puppet's jaw is open, frame by frame, from a crop around its mouth.

Why: Seedance treats mouth timing loosely, so the creator's voice must be placed on the
MEASURED jaw-open windows, not on the planned ones. This counts mouth-interior pixels
(red/pink tongue + dark cavity) inside a crop box on every frame and auto-thresholds
between the closed baseline and the open peak.

Usage:
  jaw_windows.py clip.mp4 --box X,Y,W,H [--fps 24] [--ratio 0.4] [--csv out.csv]
  Pick the box from one open-mouth frame (pixels of the clip, e.g. 480x854): wrap the
  whole mouth with ~10 px margin, avoid other red objects (bow tie!) inside the box.
Prints open ranges in CLIP time, ready for edit.json "jaw": [[a, b], ...].
The colour test assumes orange/tan fleece with a red mouth lining (Professor, Sami). For a
puppet with red or very dark fleece or clothing near the mouth, check the result against
a contact sheet before trusting it.
Validated on take-3 clips against the reviewers' frame-by-frame measurements:
  S2 Sami 0.50-2.04 s (review 0.46-2.08), S3 Professor 0.00-2.58 s (review 0.00-2.63),
  S5-B Professor 2.67-3.96 s (review 2.62-3.96). In two-shots the box must exclude the
  other puppet and red props; a wrong box shows up as "open" for the whole clip.
Requires ffmpeg and numpy.
"""
import argparse, json, subprocess
import numpy as np

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('clip'); ap.add_argument('--box', required=True)
    ap.add_argument('--fps', type=float, default=24); ap.add_argument('--ratio', type=float, default=0.4,
        help='open if count > closed + ratio*(open_peak - closed)')
    ap.add_argument('--gap', type=int, default=2, help='merge ranges separated by <= gap frames')
    ap.add_argument('--csv'); a = ap.parse_args()
    x, y, w, h = [int(v) // 2 * 2 for v in a.box.split(',')]  # yuv420 crops snap to even values
    cmd = ['ffmpeg', '-loglevel', 'error', '-i', a.clip, '-vf', f'fps={a.fps},crop={w}:{h}:{x}:{y}',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(int)
    R, G, B = fr[..., 0], fr[..., 1], fr[..., 2]
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    # orange/tan fleece has R-G ~70-85; the red tongue/lining >110; the cavity is dark
    mouth = ((R - G > 110) & (R - B > 60)) | (lum < 60)
    cnt = mouth.reshape(len(fr), -1).sum(1)
    lo, hi = np.percentile(cnt, 10), np.percentile(cnt, 95)
    if hi - lo < 0.01 * w * h:
        print(f'No clear jaw motion in this box (closed~{lo:.0f}px, peak~{hi:.0f}px).'); return
    thr = lo + a.ratio * (hi - lo); is_open = cnt > thr
    ranges, start, last = [], None, None
    for i, o in enumerate(is_open):
        if o:
            if start is None: start = i
            elif i - last > a.gap + 1: ranges.append((start, last)); start = i
            last = i
    if start is not None: ranges.append((start, last))
    ranges = [(s, e) for s, e in ranges if e - s >= 1]
    out = [[round(s / a.fps, 2), round((e + 1) / a.fps, 2)] for s, e in ranges]
    print(f'closed~{lo:.0f}px open-peak~{hi:.0f}px threshold {thr:.0f}px, {len(fr)} frames')
    for s, e in out: print(f'  jaw open {s:.2f} -> {e:.2f} s ({e - s:.2f} s)')
    print('edit.json "jaw":', json.dumps(out))
    if out: print(f'overall line window: {out[0][0]:.2f} -> {out[-1][1]:.2f} s (use this for the voice table)')
    print('Sanity-check: if the whole clip reads "open", the box caught something else (hair, bow tie, a dark edge); tighten it.')
    if a.csv:
        with open(a.csv, 'w') as f:
            f.write('t,count,open\n'); [f.write(f'{i / a.fps:.3f},{c},{int(o)}\n') for i, (c, o) in enumerate(zip(cnt, is_open))]

if __name__ == '__main__':
    main()
