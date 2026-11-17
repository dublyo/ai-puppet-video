#!/usr/bin/env python3
"""Detect leaked character voices in a generated clip and optionally mute them.

Why: Seedance with generate_audio=true can voice dialogue even when the prompt bans
voices. Voiced speech is harmonic with a pitch of roughly 85-300 Hz and is sustained;
SFX like a lid pop or creak are usually a single harmonic transient. This scans 0.1 s
windows, keeps sustained harmonic runs, and can write a copy with those ranges muted
(video stream copied untouched).

IMPORTANT: a CLEAN result is not proof of silence. On take 3 the scan caught the main
leaks in S2, S3 and S5 but missed S1's quiet 0.2 s leak (a lone window, h=0.63) and the
0.5-0.95 s onset in S3. Because the creator's voice replaces every line anyway, the safe
default is to ALSO mute each shot's measured jaw-open windows (--jaw, from
jaw_windows.py), then spot-check by ear or with Whisper.

Usage:
  voice_scan.py clip.mp4                                   # report only
  voice_scan.py clip.mp4 --mute out.mp4                    # mute detected ranges
  voice_scan.py clip.mp4 --mute out.mp4 --jaw 0.5-2.04,3.1-3.6   # mute ranges + jaw windows
Exit code: report-only -> 0 clean / 1 voice-like ranges found; with --mute -> 0 if written.
Requires ffmpeg and numpy.
"""
import argparse, subprocess, sys, tempfile, os, wave
import numpy as np

def load_wav(path, sr=16000):
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', path, '-ar', str(sr), '-ac', '1', tmp], check=True)
    w = wave.open(tmp)
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    os.unlink(tmp)
    return x, sr

def scan(x, sr, win=0.1, min_db=-34.0, fmin=85, fmax=300):
    n = int(sr * win); rows = []
    for i in range(0, len(x) - n, n):
        f = x[i:i + n]; e = float(np.sqrt((f ** 2).mean()))
        db = 20 * np.log10(max(e, 1e-9))
        if db < min_db:
            rows.append((i / sr, db, 0.0, 0.0)); continue
        f = f - f.mean(); ac = np.correlate(f, f, 'full')[n - 1:]; ac /= ac[0] + 1e-12
        lo, hi = int(sr / fmax), int(sr / fmin)
        k = lo + int(np.argmax(ac[lo:hi])); rows.append((i / sr, db, sr / k, float(ac[k])))
    return rows

def ranges(rows, win, min_h, pad, weak=0.45, strong=0.85):
    """Speech is sustained: keep a run of adjacent harmonic windows if it has >=2 windows
    with h>=weak and at least one >=min_h, or a single window >=strong. A lone harmonic
    window is usually an SFX transient (a lid pop or creak scored 0.64 in our tests)."""
    groups, cur = [], []
    for t, db, p, h in rows:
        if h >= weak and (not cur or t - cur[-1][0] <= win + 1e-6): cur.append((t, h))
        elif h >= weak: groups.append(cur); cur = [(t, h)]
        else:
            if cur: groups.append(cur); cur = []
    if cur: groups.append(cur)
    out = []
    for g in groups:
        hs = [h for _, h in g]
        if (len(g) >= 2 and max(hs) >= min_h) or max(hs) >= strong:
            out.append([max(0.0, g[0][0] - pad), g[-1][0] + win + pad])
    return out

def merge(rs):
    rs = sorted(rs); out = []
    for a, b in rs:
        if out and a <= out[-1][1]: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('clip'); ap.add_argument('--mute')
    ap.add_argument('--jaw', help='extra windows to mute, e.g. "0.5-2.04,3.1-3.6" (clip time)')
    ap.add_argument('--min-db', type=float, default=-34.0)
    ap.add_argument('--min-h', type=float, default=0.45, help='autocorrelation peak threshold (voice ~0.6-0.95)')
    ap.add_argument('--pad', type=float, default=0.15)
    a = ap.parse_args()
    x, sr = load_wav(a.clip)
    rows = scan(x, sr, min_db=a.min_db)
    print(f'{a.clip}: {len(x)/sr:.2f}s, loud windows:')
    for t, db, p, h in rows:
        if db >= a.min_db:
            print(f'  {t:5.1f}s {db:6.1f} dB  pitch {p:5.0f} Hz  h={h:.2f}' + ('  (harmonic)' if h >= 0.45 else ''))
    rg = merge(ranges(rows, 0.1, a.min_h, a.pad))
    if rg:
        print('VOICE-LIKE RANGES (confirm by ear; muting a few SFX frames is harmless):')
        for s, e in rg: print(f'  {s:.2f}-{e:.2f}s')
    else:
        print('CLEAN by scan (not proof: quiet or very short leaks can slip under; see docstring)')
    if a.mute:
        jaw = [[float(v) for v in p.split('-')] for p in a.jaw.split(',')] if a.jaw else []
        allr = merge(rg + jaw)
        expr = '+'.join(f'between(t,{s:.2f},{e:.2f})' for s, e in allr) or '0'
        os.makedirs(os.path.dirname(os.path.abspath(a.mute)), exist_ok=True)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', a.clip, '-c:v', 'copy',
                        '-af', f"volume=enable='{expr}':volume=0", '-c:a', 'aac', '-b:a', '160k', a.mute], check=True)
        print('muted', ', '.join(f'{s:.2f}-{e:.2f}' for s, e in allr) or 'nothing', '->', a.mute)
        sys.exit(0)
    sys.exit(1 if rg else 0)

if __name__ == '__main__':
    main()
