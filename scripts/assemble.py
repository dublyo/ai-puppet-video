#!/usr/bin/env python3
"""Assemble shot clips into one cut from an edit list, and print the voice windows.

edit.json (paths relative to the edit.json folder, or absolute):
{"output": "final-sfx-only.mp4", "size": "480x854", "fps": 24,
 "shots": [{"name": "S1", "file": "clips-sfx-only/S1.mp4", "in": 0.0, "out": 4.96,
            "jaw": [[0.0, 0.54]], "line": "Professor: ...",
            "mute": [[0.0, 0.4]]}]}       # optional extra mute windows (clip time)

- in/out are snapped to whole frames and 'out' is clamped to the clip length, so the
  printed timeline matches the real cut.
- Every input is scaled/padded to "size" and resampled to "fps" (default: first clip's),
  so finalised 720p/1080p takes can be mixed with 480p ones.
- Clips without an audio stream (generate_audio:false) get silent audio.
- 'jaw' = measured jaw-open windows in CLIP time (jaw_windows.py); converted to cut time.
Writes <output> and <edit>.timeline.md (timeline + voice-window table).
Requires ffmpeg/ffprobe.
"""
import json, os, subprocess, sys

def probe(f):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,r_frame_rate:format=duration',
                          '-of', 'json', f], capture_output=True, text=True, check=True).stdout
    d = json.loads(out); v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    n, m = v['r_frame_rate'].split('/')
    return {'w': v['width'], 'h': v['height'], 'fps': float(n) / float(m), 'dur': float(d['format']['duration']),
            'audio': any(s['codec_type'] == 'audio' for s in d['streams'])}

def main(path):
    base = os.path.dirname(os.path.abspath(path)); e = json.load(open(path))
    shots = e['shots']; out = os.path.join(base, e.get('output', 'final.mp4'))
    files = [os.path.join(base, s['file']) for s in shots]; info = [probe(f) for f in files]
    W, H = (int(v) for v in e.get('size', f"{info[0]['w']}x{info[0]['h']}").split('x'))
    fps = float(e.get('fps', info[0]['fps']))
    args, filt, t, timeline, voice, cat = ['ffmpeg', '-loglevel', 'error', '-y'], [], 0.0, [], [], ''
    for i, (s, f, p) in enumerate(zip(shots, files, info)):
        a_in = round(s['in'] * fps) / fps
        a_out = round(min(s['out'], p['dur']) * fps) / fps
        dur = round(a_out - a_in, 4)
        args += ['-ss', f'{a_in:.4f}', '-t', f'{dur:.4f}', '-i', f]
        filt.append(f'[{i}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},setpts=PTS-STARTPTS[v{i}]')
        if p['audio']:
            mute = s.get('mute') or []
            vol = (",volume=enable='" + '+'.join(f"between(t,{m[0]-a_in:.3f},{m[1]-a_in:.3f})" for m in mute) + "':volume=0") if mute else ''
            filt.append(f'[{i}:a]aresample=48000,asetpts=PTS-STARTPTS{vol}[a{i}]')
        else:
            filt.append(f'anullsrc=r=48000:cl=stereo,atrim=0:{dur:.4f}[a{i}]')
        cat += f'[v{i}][a{i}]'
        timeline.append((s.get('name', f'S{i+1}'), s['file'], a_in, a_out, t, t + dur))
        for j0, j1 in s.get('jaw', []):
            b0, b1 = max(j0, a_in), min(j1, a_out)
            if b1 > b0: voice.append((s.get('line', s.get('name', '')), t + b0 - a_in, t + b1 - a_in))
        t += dur
    filt.append(f'{cat}concat=n={len(shots)}:v=1:a=1[v][a]')
    args += ['-filter_complex', ';'.join(filt), '-map', '[v]', '-map', '[a]',
             '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', out]
    subprocess.run(args, check=True)
    real = probe(out)['dur']
    md = ['| Shot | Source | In-Out (clip) | Final cut |', '|---|---|---|---|']
    md += [f'| {n} | {f} | {a:.2f}-{b:.2f} | {c:.2f}-{d:.2f} |' for n, f, a, b, c, d in timeline]
    md += ['', '| Line | Mouth window in final cut |', '|---|---|']
    md += [f'| {l} | {a:.2f} -> {b:.2f} s ({b-a:.2f} s) |' for l, a, b in voice]
    txt = f'Output: {os.path.basename(out)} ({real:.2f} s, planned {t:.2f} s, {W}x{H} @ {fps:g} fps)\n\n' + '\n'.join(md) + '\n'
    open(os.path.splitext(path)[0] + '.timeline.md', 'w').write(txt)
    print(txt)

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(sys.argv[1])
