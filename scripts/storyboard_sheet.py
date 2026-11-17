#!/usr/bin/env python3
"""Render an annotated storyboard sheet (PNG) from a JSON panel list, Arabic-safe.

panels.json:
{"title": "«البرطمان العنيد» — Take 3 storyboard",
 "subtitle": "9:16 · 20 s · Seedance 2.5 · 480p · one clip per shot · Sami LEFT, Professor RIGHT · audio = SFX only, NO voices",
 "footer": "Frames: GPT Image 2.6 Flare high 1k, refs = v1 masters + approved shot-1 frame",
 "panels": [
   {"shot": "SHOT 1", "time": "0.0–5.0 s", "image": "P1-v1.png",
    "camera": "medium two-shot, chest-up, eye level, locked",
    "action": "Prof shows the jar …",
    "speaker": "البروفيسور", "line": "«الموضوع بسيط جدًا.»",     # or "line": "بدون كلام" with no speaker
    "sfx": "room tone, glass clink, lid creak"}]}

Image paths are relative to the JSON file. Renders with headless Google Chrome because
Pillow here has no raqm (no Arabic shaping). Chrome must run outside the Bash sandbox
(it needs to create its profile socket); a fresh temp --user-data-dir is used.

Usage: storyboard_sheet.py panels.json out.png [--width 1800] [--cols 6]
"""
import argparse, html, json, os, subprocess, tempfile

CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

CSS = """body{margin:0;background:#16181c;color:#eee;font-family:-apple-system,"Helvetica Neue",Arial,sans-serif}
h1{margin:0;padding:22px 28px 6px;font-size:30px}.sub{padding:0 28px 18px;color:#aab;font-size:17px}
.grid{display:grid;gap:14px;padding:0 20px 24px}.card{background:#22252b;border-radius:10px;overflow:hidden}
.card img{width:100%;display:block}.num{background:#e0b341;color:#111;font-weight:700;padding:6px 10px;font-size:17px;display:flex;justify-content:space-between}
.t{padding:8px 10px;font-size:14px;line-height:1.35}.k{color:#e0b341;font-weight:600}
.ar{direction:rtl;unicode-bidi:plaintext;text-align:right;font-size:17px;color:#fff;background:#2d3139;border-radius:6px;padding:5px 7px;margin:5px 0}
.sfx{color:#8fd3a8}.foot{padding:0 28px 24px;color:#aab;font-size:15px}"""

def build(d, base, cols):
    e = html.escape; cards = []
    for p in d['panels']:
        img = 'file://' + os.path.abspath(os.path.join(base, p['image']))
        line = (f"<b>{e(p['speaker'])}</b> · شفايف فقط<br>{e(p['line'])}" if p.get('speaker') else e(p.get('line', 'بدون كلام')))
        cards.append(f"""<div class="card"><div class="num"><span>{e(p['shot'])}</span><span>{e(p['time'])}</span></div>
<img src="{img}"><div class="t"><span class="k">Camera:</span> {e(p['camera'])}<br><span class="k">Action:</span> {e(p['action'])}
<div class="ar">{line}</div><span class="sfx">SFX: {e(p.get('sfx', ''))}</span></div></div>""")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
.grid{{grid-template-columns:repeat({cols},1fr)}}</style></head><body>
<h1>{e(d.get('title', 'Storyboard'))}</h1><div class="sub">{e(d.get('subtitle', ''))}</div>
<div class="grid">{''.join(cards)}</div><div class="foot">{e(d.get('footer', ''))}</div></body></html>"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('panels'); ap.add_argument('out')
    ap.add_argument('--width', type=int, default=1800); ap.add_argument('--cols', type=int)
    ap.add_argument('--height', type=int, help='default: estimated from the panel count')
    a = ap.parse_args()
    d = json.load(open(a.panels)); base = os.path.dirname(os.path.abspath(a.panels))
    cols = a.cols or min(6, len(d['panels'])); rows = -(-len(d['panels']) // cols)
    card_w = (a.width - 40 - 14 * (cols - 1)) / cols
    height = a.height or int(130 + rows * (card_w * 16 / 9 + 330) + 60)
    page = os.path.join(base, os.path.splitext(os.path.basename(a.out))[0] + '.html')
    open(page, 'w').write(build(d, base, cols))
    prof = tempfile.mkdtemp()
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={prof}',
                    '--allow-file-access-from-files', f'--window-size={a.width},{height}',
                    f'--screenshot={os.path.abspath(a.out)}', 'file://' + page], check=True)
    print('wrote', a.out, 'and', page)

if __name__ == '__main__':
    main()
