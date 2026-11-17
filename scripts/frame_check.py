#!/usr/bin/env python3
"""Compare storyboard frames: camera-shift estimate, blend, diff and strips.

Why: a clip's START and END frames must share the camera (only the scripted action may
change), or the video model invents a zoom/pan. Reviewers in test-video-05 found these
by blending frames and checking that fixed set elements were not doubled; this script
does that automatically.

Usage:
  frame_check.py pair START.png END.png --out review/clip1   # pair.jpg, blend.jpg, diff.jpg + verdict
  frame_check.py strip F1.png F2.png ... --out strip.jpg      # frames side by side, story order
Method: a zoom search (0.80-1.25) on edge images for the whole frame and for two set-only
bands (top 30% wall/shelf, bottom 20% counter), plus a tile-agreement fit. Verdicts:
SAME CAMERA / SLIGHT DRIFT (>=2% zoom or >1.5% pan) / CAMERA MOVED (>=4% zoom or >3.5% pan),
with notes for an uncertain zoom DIRECTION (bands disagree -> judge by eye) and weak matches.
Magnitudes are approximate; the verdict matched the blends in all test-video-05 pairs.
Requires ffmpeg and numpy (no PIL).
"""
import argparse, json, os, subprocess
import numpy as np

W = 376  # working width; height follows 9:16 frames (~668)

def load_gray(path, w=W, h=None):
    """Grayscale at width w; pass h to force the same size as another frame (e.g. a 480x854 video
    frame vs a 752x1344 storyboard image differ by a few rows after scaling)."""
    if h is None:
        probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                '-of', 'json', path], capture_output=True, text=True, check=True)
        s = json.loads(probe.stdout)['streams'][0]; h = int(round(s['height'] * w / s['width'] / 2) * 2)
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-vf', f'scale={w}:{h}', '-f', 'rawvideo',
                          '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w).astype(float)

def phase_shift(a, b):
    a = a - a.mean(); b = b - b.mean()
    win = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    F = np.fft.fft2(a * win); G = np.fft.fft2(b * win)
    R = F * np.conj(G); R /= np.abs(R) + 1e-9
    r = np.fft.ifft2(R).real
    y, x = np.unravel_index(np.argmax(r), r.shape)
    if y > a.shape[0] // 2: y -= a.shape[0]
    if x > a.shape[1] // 2: x -= a.shape[1]
    peak = r.max() / (np.abs(r).mean() + 1e-9)
    return -x, -y, peak

def grad(a):
    gy, gx = np.gradient(a); return np.hypot(gx, gy)

def rescale(img, s):
    """Zoom img about its centre by factor s (s>1 = push-in), bilinear, same size."""
    h, w = img.shape; cy, cx = (h - 1) / 2, (w - 1) / 2
    ys = (np.arange(h) - cy) / s + cy; xs = (np.arange(w) - cx) / s + cx
    ys = np.clip(ys, 0, h - 1.001); xs = np.clip(xs, 0, w - 1.001)
    y0 = ys.astype(int); x0 = xs.astype(int); fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
    a = img[y0][:, x0]; b = img[y0][:, x0 + 1]; c = img[y0 + 1][:, x0]; d = img[y0 + 1][:, x0 + 1]
    return a * (1 - fy) * (1 - fx) + b * (1 - fy) * fx + c * fy * (1 - fx) + d * fy * fx

def scale_search(A, B, band=None):
    """Find the zoom that best aligns the set: search s in 0.80..1.25 on edge images (B zoomed
    about the full-frame centre, then both cropped to `band` = (y0, y1) fractions), pick the
    strongest phase-correlation peak. Bands that hold only set (wall/shelf, counter edge) are
    far more reliable than the whole frame, where moving characters can flip the sign."""
    h = A.shape[0]; y0, y1 = (0, h) if band is None else (int(band[0] * h), int(band[1] * h))
    GA = grad(A)[y0:y1]; best = None
    for s in np.arange(0.80, 1.251, 0.01):
        GB = grad(rescale(B, 1 / s))[y0:y1]  # undo a zoom of s in B
        dx, dy, pk = phase_shift(GA, GB)
        if best is None or pk > best[3]: best = (s, dx, dy, pk)
    return {'zoom_pct': 100 * (best[0] - 1), 'tx': best[1], 'ty': best[2], 'peak': best[3]}

def camera_fit(A, B, cols=4, rows=6, min_peak=9.0):
    """Robust camera estimate: phase-correlate a grid of tiles, keep confident tiles, fit
    dx = s*(x-cx) + tx, dy = s*(y-cy) + ty (s = zoom), dropping outlier tiles (moving characters)."""
    h, w = A.shape; th, tw = h // rows, w // cols; pts = []
    for r in range(rows):
        for c in range(cols):
            a = A[r*th:(r+1)*th, c*tw:(c+1)*tw]; b = B[r*th:(r+1)*th, c*tw:(c+1)*tw]
            if a.std() < 4: continue  # flat area, no structure
            dx, dy, pk = phase_shift(a, b)
            if pk >= min_peak and abs(dx) < tw / 3 and abs(dy) < th / 3:
                pts.append(((c + .5) * tw - w / 2, (r + .5) * th - h / 2, dx, dy))
    if len(pts) < 4: return None
    P = np.array(pts, float); keep = np.ones(len(P), bool)
    for _ in range(3):
        X = P[keep]
        M = np.zeros((2 * len(X), 3)); v = np.zeros(2 * len(X))
        M[0::2, 0] = X[:, 0]; M[0::2, 1] = 1; v[0::2] = X[:, 2]
        M[1::2, 0] = X[:, 1]; M[1::2, 2] = 1; v[1::2] = X[:, 3]
        s, tx, ty = np.linalg.lstsq(M, v, rcond=None)[0]
        res = np.hypot(P[:, 2] - (s * P[:, 0] + tx), P[:, 3] - (s * P[:, 1] + ty))
        keep = res < max(3.0, np.median(res[keep]) * 2.5)
        if keep.sum() < 4: break
    return {'zoom_pct': 100 * s, 'tx': tx, 'ty': ty, 'tiles_used': int(keep.sum()), 'tiles_total': rows * cols, 'tiles_confident': len(P)}

def pair(a_path, b_path, out, tol):
    os.makedirs(out, exist_ok=True)
    A = load_gray(a_path); B = load_gray(b_path, h=A.shape[0])
    h, w = A.shape
    mad = float(np.abs(A - B).mean())
    full = scale_search(A, B)
    bands = {'top band (wall/shelf)': scale_search(A, B, (0.0, 0.30)), 'bottom band (counter/set)': scale_search(A, B, (0.80, 1.0))}
    fit = camera_fit(A, B)
    print(f"  whole frame: zoom {full['zoom_pct']:+.0f}%  pan dx={full['tx']:+.0f}px dy={full['ty']:+.0f}px  [peak {full['peak']:.0f}]   (+zoom = END tighter/push-in, -zoom = END wider/pull-back)")
    for n, b in bands.items():
        print(f"  {n}: zoom {b['zoom_pct']:+.0f}%  pan dx={b['tx']:+.0f}px dy={b['ty']:+.0f}px  [peak {b['peak']:.0f}]")
    if fit:
        print(f"  tile check: {fit['tiles_used']} of {fit['tiles_confident']} confident tiles agree (tile pan dy {fit['ty']:+.0f}px)   mean abs difference {mad:.1f}")
    meas = [full] + list(bands.values())
    strong = [m for m in meas if m['peak'] >= 6] or meas
    zs = [m['zoom_pct'] for m in strong]
    bz = [b['zoom_pct'] for b in bands.values()]
    # Calibrated on test-video-05: a move is real if the whole frame shows it, or both set bands
    # agree on the direction (>=3% each). Pans are read from the whole frame (band pans are noisy).
    bands_agree = (all(z >= 3 for z in bz) or all(z <= -3 for z in bz))
    big = abs(full['zoom_pct']) >= 4 or bands_agree or abs(full['tx']) / w > 0.035 or abs(full['ty']) / h > 0.035
    small = any(abs(m['zoom_pct']) >= 2 for m in strong) or abs(full['tx']) / w > tol or abs(full['ty']) / h > tol
    dir_conflict = any(z >= 3 for z in zs) and any(z <= -3 for z in zs)
    moved = big
    if big:
        print('VERDICT: CAMERA MOVED -> re-roll END in EDIT mode (START as Image 1: "EDIT Image 1, do not re-compose it ... change only ...") unless this exact move is planned')
    elif small:
        print('VERDICT: SLIGHT DRIFT -> OK only if a slow push/pull in this direction is planned; confirm on blend.jpg')
    else:
        print('VERDICT: SAME CAMERA -> still check blend.jpg: untouched props must not be doubled or moved')
    if dir_conflict:
        print('  note: zoom DIRECTION uncertain (bands disagree) -> decide push-in vs pull-back by eye: props/set larger in END = push-in')
    if all(m['peak'] < 6 for m in meas) or (fit and fit['tiles_used'] < 6):
        print('  note: weak match -> low confidence; judge pair.jpg/blend.jpg by eye')
    sp = lambda *a: subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *a], check=True)
    sp('-i', a_path, '-i', b_path, '-filter_complex', '[0]scale=540:-2[a];[1]scale=540:-2[b];[a][b]hstack', os.path.join(out, 'pair.jpg'))
    sp('-i', a_path, '-i', b_path, '-filter_complex', '[0]scale=540:-2[a];[1]scale=540:-2[b];[a][b]blend=all_mode=average', os.path.join(out, 'blend.jpg'))
    sp('-i', a_path, '-i', b_path, '-filter_complex', '[0]scale=540:-2[a];[1]scale=540:-2[b];[a][b]blend=all_mode=difference,eq=brightness=0.05:contrast=2.5', os.path.join(out, 'diff.jpg'))
    print('wrote', ', '.join(os.path.join(out, f) for f in ('pair.jpg', 'blend.jpg', 'diff.jpg')))
    return bool(moved)

def strip(frames, out, h=640):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    args = ['ffmpeg', '-loglevel', 'error', '-y']
    for f in frames: args += ['-i', f]
    chains = ''.join(f'[{i}]scale=-2:{h}[s{i}];' for i in range(len(frames)))
    args += ['-filter_complex', chains + ''.join(f'[s{i}]' for i in range(len(frames))) + f'hstack=inputs={len(frames)}', out]
    subprocess.run(args, check=True); print('wrote', out)

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('pair'); p.add_argument('a'); p.add_argument('b'); p.add_argument('--out', required=True)
    p.add_argument('--tol', type=float, default=0.015)
    s = sub.add_parser('strip'); s.add_argument('frames', nargs='+'); s.add_argument('--out', required=True); s.add_argument('--height', type=int, default=640)
    a = ap.parse_args()
    if a.cmd == 'pair':
        print(f'{os.path.basename(a.a)} -> {os.path.basename(a.b)}'); pair(a.a, a.b, a.out, a.tol)
    else:
        strip(a.frames, a.out, a.height)

if __name__ == '__main__':
    main()
