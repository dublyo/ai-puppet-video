#!/usr/bin/env python3
"""Build one storyboard board per clip + the TRANSITIONS sheet, and (optionally) run the
within-clip camera check on every clip.

plan.json (next to selected.json and the <key>-vN.png frames, i.e. in the storyboard folder):
{"title": "«نظرية التصفية»", "footer": "Frames: ... refs: ...",
 "clips": [
   {"id": "1", "time": "0.0–3.5 s", "camera": "WIDE, 3/4 high ...", "sfx": "...",
    "frames": [{"label": "START", "key": "S1a", "action": "..."},
               {"label": "KEY POSE", "key": "S2a", "action": "..."},      # optional
               {"label": "END", "key": "S1b", "action": "..."}],
    "line": {"speaker": "البروفيسور", "text": "«...» (اختيارية)"},          # optional; default بدون كلام
    "next": "→ CLIP 2: continuation",
    "planned_move": {"type": "push-in", "max_pct": 15}},                  # optional: push-in | pull-back
   ...],
 "transitions": [{"from": "1", "to": "2", "why": "Same frame: continuous take."}]   # optional; auto otherwise
}
Frame files: each key resolves through selected.json ({"S1b": "S1b-v8.png"}), else the highest
<key>-vN.png in the plan folder, else <frames_dir>/<key>.png. The chosen files are also copied
to final/<key>.png so the selection is visible on disk.

Usage: storyboard_boards.py plan.json [--check]
--check runs frame_check.py pair on START->END of every clip. A clip is flagged when the check
fails to run, says CAMERA MOVED without a matching planned_move (type and size), says SLIGHT
DRIFT on a clip with no planned move AND a weak/uncertain note, or reports an uncertain direction.
Exit 1 if anything is flagged. Rendering needs headless Chrome (run with the sandbox off).
"""
import argparse, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def resolver(base, plan):
    sel_p = os.path.join(base, 'selected.json'); sel = json.load(open(sel_p)) if os.path.exists(sel_p) else {}
    fd = os.path.join(base, plan.get('frames_dir', 'final')); os.makedirs(os.path.join(base, 'final'), exist_ok=True)
    def img(k):
        src = None
        if k in sel: src = os.path.join(base, sel[k])
        else:
            vs = sorted((int(m.group(1)), f) for f in os.listdir(base) if (m := re.fullmatch(rf'{re.escape(k)}-v(\d+)\.png', f)))
            if vs: src = os.path.join(base, vs[-1][1])
            elif os.path.exists(os.path.join(fd, f'{k}.png')): src = os.path.join(fd, f'{k}.png')
        if not src or not os.path.exists(src): sys.exit(f'frame {k}: no file found (selected.json, {k}-vN.png or {fd}/{k}.png)')
        dst = os.path.join(base, 'final', f'{k}.png')
        if os.path.abspath(src) != os.path.abspath(dst): shutil.copy(src, dst)
        return dst
    return img

def judge(c, out):
    v = next((l for l in out.splitlines() if l.startswith('VERDICT')), None)
    if not v: return 'check did not run'
    notes = [l.strip() for l in out.splitlines() if l.strip().startswith('note:')]
    m = re.search(r'whole frame: zoom ([+-]\d+)%', out); z = int(m.group(1)) if m else 0
    pm = c.get('planned_move')
    if 'CAMERA MOVED' in v:
        if not pm: return 'unplanned camera move'
        want = 1 if pm.get('type') == 'push-in' else -1
        if any('DIRECTION uncertain' in n for n in notes): return f"planned {pm.get('type')}: direction uncertain, confirm by eye"
        if z * want < 0: return f"planned {pm.get('type')} but measured {z:+d}%"
        if abs(z) > pm.get('max_pct', 15): return f"planned {pm.get('type')} up to {pm.get('max_pct', 15)}% but measured {z:+d}%"
        return None
    if any('weak match' in n for n in notes): return 'weak match: confirm blend.jpg by eye'
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.plan)); plan = json.load(open(a.plan))
    bd = os.path.join(base, 'boards'); os.makedirs(bd, exist_ok=True); img = resolver(base, plan)
    clips = plan['clips']; flagged = []
    for c in clips:
        ps = []
        for fr in c['frames']:
            e = {'shot': f"CLIP {c['id']} · {fr['label']}", 'time': c['time'], 'image': img(fr['key']),
                 'camera': c['camera'] if fr['label'] == 'START' else ('Same camera and framing as START.' if fr['label'] == 'END' else 'Mid-shot key pose (reference)'),
                 'action': fr['action'], 'sfx': c.get('sfx', '')}
            if fr['label'] == 'END' and c.get('line'): e.update({'speaker': c['line']['speaker'], 'line': c['line']['text']})
            else: e['line'] = 'بدون كلام'
            ps.append(e)
        d = {'title': f"{plan['title']} — CLIP {c['id']}", 'subtitle': f"{c['time']} · 9:16 · start → end frame · {c.get('next', '')}",
             'footer': plan.get('footer', ''), 'panels': ps}
        j = os.path.join(bd, f"clip{c['id']}.json"); json.dump(d, open(j, 'w'), ensure_ascii=False, indent=1)
        cols = len(ps)
        subprocess.run([sys.executable, os.path.join(HERE, 'storyboard_sheet.py'), j, os.path.join(bd, f"CLIP-{c['id']}.png"), '--width', str(450 * cols), '--cols', str(cols)], check=True, capture_output=True)
        print('board', f"CLIP-{c['id']}.png")
        if a.check:
            s, e = c['frames'][0]['key'], c['frames'][-1]['key']
            r = subprocess.run([sys.executable, os.path.join(HERE, 'frame_check.py'), 'pair', img(s), img(e), '--out', os.path.join(base, 'review', f"clip{c['id']}")], capture_output=True, text=True)
            out = r.stdout if r.returncode == 0 else ''
            for l in out.splitlines():
                if l.startswith('VERDICT') or l.strip().startswith(('whole frame', 'note:')): print('   ', l.strip())
            problem = judge(c, out) if out else f'check failed: {r.stderr.strip()[:200]}'
            if problem: flagged.append(f"clip {c['id']}: {problem}"); print(f'    -> FLAG: {problem}')
    T = plan.get('transitions') or [{'from': clips[i]['id'], 'to': clips[i + 1]['id'], 'why': ''} for i in range(len(clips) - 1)]
    byid = {c['id']: c for c in clips}; P = []
    for t in T:
        e, s = byid[t['from']]['frames'][-1]['key'], byid[t['to']]['frames'][0]['key']
        lab = f"{t['from']}→{t['to']}"
        P.append({'shot': f"END {t['from']}", 'time': lab, 'image': img(e), 'camera': 'Last frame of the clip', 'action': t.get('why', ''), 'line': '—', 'sfx': ''})
        P.append({'shot': f"START {t['to']}", 'time': lab, 'image': img(s), 'camera': 'First frame of the next clip', 'action': t.get('why', ''), 'line': '—', 'sfx': ''})
    j = os.path.join(bd, 'transitions.json')
    json.dump({'title': f"{plan['title']} — transitions: END of each clip → START of the next", 'subtitle': f'{len(T)} cuts · positions, props, eyelines, light, cut type',
               'footer': 'Read in pairs, left to right', 'panels': P}, open(j, 'w'), ensure_ascii=False, indent=1)
    cols = min(len(P), 8)
    subprocess.run([sys.executable, os.path.join(HERE, 'storyboard_sheet.py'), j, os.path.join(bd, 'TRANSITIONS.png'), '--width', str(400 * cols), '--cols', str(cols)], check=True, capture_output=True)
    for f in os.listdir(bd):
        if f.endswith('.html'): os.remove(os.path.join(bd, f))
    print('board TRANSITIONS.png')
    if a.check:
        print('CAMERA CHECK:', 'all clips pass' if not flagged else 'FLAGGED -> ' + '; '.join(flagged))
        sys.exit(1 if flagged else 0)

if __name__ == '__main__':
    main()
