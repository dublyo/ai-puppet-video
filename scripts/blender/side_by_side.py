#!/usr/bin/env python3
"""Mandatory Route-B comparison: Blender mockup vs AI result, TIME-aligned.

Always run this after every Route-B generation (pilot and full) and send the outputs to the user with the report.
Outputs in --out:
  side-by-side.mp4      mockup LEFT | AI RIGHT, same height, AI audio (so the SFX can be judged too); the mockup is resampled to the AI fps
  shot-NN.png           per shot: mockup row on TOP, AI row BELOW, at the same moments (start, quarter, mid, three-quarter, end)
  cuts.png              every cut pair (last frame before | first frame after), mockup on top, AI below
  overview.png          one start/mid/end column per shot, all shots in one sheet
  compare.json          frame counts, fps, durations, shot ranges, the sampled frame indices (mockup + AI), the alignment
                        method and the measured cut offsets (in mockup frames and in seconds)
Usage:
  side_by_side.py --mockup refs/full-20s.mp4 --ai clips/full-v1.mp4 --out review/full-v1 --cuts 85,145,197,277,325,397
  (--cuts = first frame index (0-based) of every shot after the first, in MOCKUP frames; omit for a single shot)
Alignment: everything is counted in mockup frames. Mockup frame i is the moment t = i / mockup_fps (from each file's
first frame); its AI partner is AI frame round(t * ai_fps), clamped to the AI length. With equal fps that is the same
index, so the results match the old frame-index comparison exactly.
Cache: grabbed thumbnails live in --out/_frames, keyed by _frames/signature.json (absolute path, size and mtime of each
input + --thumb). Re-running into the same --out with a changed or different video wipes that side's stale thumbnails.
Requires ffmpeg/ffprobe. No drawtext needed (the order is fixed: mockup left/top, AI right/bottom).
"""
import argparse, glob, json, math, os, subprocess, sys

def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_frames,r_frame_rate,width,height:format=duration', '-of', 'json', path],
                       capture_output=True, text=True, check=True)
    j = json.loads(r.stdout); s = j['streams'][0]; num, den = s['r_frame_rate'].split('/')
    return {'frames': int(s['nb_read_frames']), 'fps': float(num) / float(den), 'w': s['width'], 'h': s['height'],
            'duration': float(j['format']['duration'])}

def frame_diffs(path, w=64):
    """Mean absolute grey-level change between consecutive frames (index i = change from frame i-1 to i)."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={w}:-2,format=gray', '-f', 'rawvideo', '-'],
                       capture_output=True, check=True)
    raw = r.stdout
    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path],
                        capture_output=True, text=True, check=True)
    W, H = map(int, pr.stdout.strip().split(','))
    hh = int(round(H * w / W / 2) * 2); size = w * hh
    frames = [raw[i:i + size] for i in range(0, len(raw) - size + 1, size)]
    d = [0.0]
    for p, q in zip(frames, frames[1:]):
        d.append(sum(abs(x - y) for x, y in zip(p, q)) / size)
    return d

def grab(src, n, out, w):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', f'select=eq(n\\,{n}),scale={w}:-2', '-frames:v', '1', out], check=True)

def grid(pairs, out):
    """pairs = [(mockup_png, ai_png), ...] -> columns, each mockup over AI."""
    a, fl = [], ''
    for k, (m, g) in enumerate(pairs):
        a += ['-i', m, '-i', g]; fl += f'[{2 * k}][{2 * k + 1}]vstack[c{k}];'
    fl += ''.join(f'[c{k}]' for k in range(len(pairs))) + (f'hstack={len(pairs)}' if len(pairs) > 1 else 'copy')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *a, '-filter_complex', fl, out], check=True)

def signature(path, thumb):
    st = os.stat(path)
    return {'path': os.path.abspath(path), 'size': st.st_size, 'mtime_ns': st.st_mtime_ns, 'thumb': thumb}

def sync_cache(tmp, sig):
    """Wipe cached thumbnails whose source changed (m_ = mockup, g_ = AI). No/unreadable signature = wipe everything."""
    sp = os.path.join(tmp, 'signature.json')
    try: old = json.load(open(sp))
    except (OSError, ValueError): old = {}
    wiped = []
    for key, prefix in (('mockup', 'm_'), ('ai', 'g_')):
        if old.get(key) != sig[key]:
            stale = glob.glob(os.path.join(tmp, prefix + '*.png'))
            for f in stale: os.remove(f)
            if stale: wiped.append(key)
    json.dump(sig, open(sp, 'w'), indent=1)
    return wiped

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mockup', required=True); ap.add_argument('--ai', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--cuts', default='', help='comma-separated first frame index of each shot after the first')
    ap.add_argument('--thumb', type=int, default=220, help='thumbnail width for the sheets')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); tmp = os.path.join(a.out, '_frames'); os.makedirs(tmp, exist_ok=True)
    wiped = sync_cache(tmp, {'mockup': signature(a.mockup, a.thumb), 'ai': signature(a.ai, a.thumb)})
    pm, pa = probe(a.mockup), probe(a.ai)
    ratio = pa['fps'] / pm['fps']                      # AI frames per mockup frame
    def ai_idx(i):                                     # AI frame showing the same moment as mockup frame i
        return min(pa['frames'] - 1, max(0, int(math.floor(i * ratio + 0.5 + 1e-9))))
    n = min(pm['frames'], int(math.floor(pa['frames'] / ratio + 1e-9)))   # mockup frames that the AI clip still covers
    warn = []
    if abs(pm['frames'] - pa['frames'] / ratio) > 2 + 1e-6:   # more than 2 mockup frames of length difference
        warn.append(f"frame counts differ: mockup {pm['frames']} vs AI {pa['frames']} "
                    f"({pm['frames'] / pm['fps']:.2f} s vs {pa['frames'] / pa['fps']:.2f} s)")
    if abs(pm['fps'] - pa['fps']) > 0.01:
        warn.append(f"fps differ: mockup {pm['fps']:g} vs AI {pa['fps']:g}; the comparison is TIME-aligned (AI frame = "
                    f"round(mockup frame x {ratio:.4f})), all frame numbers and cut offsets below are in mockup frames")

    # 1) side-by-side video (mockup left | AI right), AI audio, length of the shorter stream
    h = max(pa['h'], 640)
    vid = os.path.join(a.out, 'side-by-side.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.mockup, '-i', a.ai, '-filter_complex',
                    f'[0:v]scale=-2:{h},setsar=1,fps={pa["fps"]}[m];[1:v]scale=-2:{h},setsar=1[g];[m][g]hstack=2[v]',
                    '-map', '[v]', '-map', '1:a?', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                    '-shortest', vid], check=True)

    # 2) per-shot sheets at the same moments (indices are mockup frames; the AI partner is ai_idx(i))
    starts = [0] + [int(c) for c in a.cuts.split(',') if c.strip()]
    shots = [(s, (starts[i + 1] - 1) if i + 1 < len(starts) else n - 1) for i, s in enumerate(starts)]
    def pair(i):
        j = ai_idx(i)
        m, g = os.path.join(tmp, f'm_{i:04d}.png'), os.path.join(tmp, f'g_{j:04d}.png')   # each named by its own frame index
        if not os.path.exists(m): grab(a.mockup, i, m, a.thumb)
        if not os.path.exists(g): grab(a.ai, j, g, a.thumb)
        return m, g
    sampled, sampled_ai = {}, {}
    for k, (s, e) in enumerate(shots, 1):
        idx = sorted({s, s + (e - s) // 4, (s + e) // 2, s + 3 * (e - s) // 4, e})
        sampled[f'shot-{k:02d}'] = idx; sampled_ai[f'shot-{k:02d}'] = [ai_idx(i) for i in idx]
        grid([pair(i) for i in idx], os.path.join(a.out, f'shot-{k:02d}.png'))
    # 3) every cut pair: last frame of shot k | first frame of shot k+1
    if len(shots) > 1:
        cut_pairs = []
        for s, _ in shots[1:]: cut_pairs += [pair(s - 1), pair(s)]
        grid(cut_pairs, os.path.join(a.out, 'cuts.png'))
    # 4) overview: start / mid / end of every shot
    ov = []
    for s, e in shots: ov += [pair(s), pair((s + e) // 2), pair(e)]
    grid(ov, os.path.join(a.out, 'overview.png'))

    # 5) measured cut timing: where the AI actually cuts vs where the mockup cuts (peak frame difference within +-12 mockup
    #    frames = +-0.5 s at 24 fps). The AI peak is searched in AI frames around the same moment, then converted to mockup frames.
    cut_check = []
    if len(shots) > 1:
        da, dm = frame_diffs(a.ai), frame_diffs(a.mockup)
        def peak(d, c, r):   # d[i] = change between frame i-1 and i -> i = first frame of new shot
            lo, hi = max(1, c - r), min(len(d) - 1, c + r)
            return max(range(lo, hi + 1), key=lambda i: d[i])
        def num(x):          # whole numbers stay ints (equal fps -> same JSON as before)
            x = round(x, 2); return int(x) if x == int(x) else x
        for s, _ in shots[1:]:
            pm_ = peak(dm, s, 12)
            pa_ = peak(da, ai_idx(s), int(math.ceil(12 * ratio)))
            pa_m = pa_ / ratio                                    # AI cut expressed in mockup frames
            cut_check.append({'planned_first_frame': s, 'mockup_cut': pm_, 'ai_cut': pa_, 'ai_cut_in_mockup_frames': num(pa_m),
                              'offset_frames': num(pa_m - pm_), 'offset_seconds': round(pa_ / pa['fps'] - pm_ / pm['fps'], 3)})
        offs = sorted(c['offset_frames'] for c in cut_check); shift = offs[len(offs) // 2]
        if abs(shift) >= 0.5: warn.append(f"global timeline shift: AI cuts {shift:+g} mockup frame(s) vs the mockup on most cuts "
                              "(test-video-06 saw -1 on the 20 s film and +1 on the 10 s pilot: harmless, re-time in the edit if needed)")
        bad = [c for c in cut_check if abs(c['offset_frames']) > 1]   # more than +-1 frame from the mockup's cut = re-time or re-roll
        if bad: warn.append(f"{len(bad)} cut(s) off by more than 1 frame: " + ', '.join(f"{c['mockup_cut']}->{c['ai_cut_in_mockup_frames']}" for c in bad))

    rep = {'mockup': {'file': a.mockup, **pm}, 'ai': {'file': a.ai, **pa}, 'shots_0based': shots, 'sampled_frames': sampled,
           'sampled_frames_ai': sampled_ai, 'cuts': cut_check,
           'alignment': {'method': 'time', 'mockup_fps': pm['fps'], 'ai_fps': pa['fps'],
                         'rule': 'mockup frame i = t = i / mockup_fps from the first frame; AI frame = round(t * ai_fps), clamped',
                         'units': 'shots_0based, sampled_frames, mockup_cut, ai_cut_in_mockup_frames and offset_frames are mockup '
                                  'frames; sampled_frames_ai and ai_cut are AI frames',
                         'video': 'mockup resampled to the AI fps (ffmpeg fps filter), both streams start at their first frame'},
           'cache': {'dir': tmp, 'wiped': wiped},
           'layout': 'video: mockup LEFT | AI RIGHT; sheets: mockup TOP, AI BOTTOM', 'warnings': warn}
    json.dump(rep, open(os.path.join(a.out, 'compare.json'), 'w'), indent=1)
    print(json.dumps({'out': a.out, 'shots': len(shots), 'warnings': warn}, indent=1))

if __name__ == '__main__':
    sys.exit(main())
