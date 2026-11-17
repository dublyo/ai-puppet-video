#!/usr/bin/env python3
"""Generate storyboard frames in dependency rounds, each frame referenced to the frames it
must match (see references/storyboard-qc.md section 2).

spec.json  (relative paths resolve against the REPO ROOT = the folder that holds .claude/skills/
            ai-puppet-video, i.e. 4 levels above this script; override with PUPPET_REPO_ROOT):
{
 "out_dir": "campaign-puppet/production/<slug>/storyboard",
 "settings": {"model": "gpt_image_2_6_flare", "aspect_ratio": "9:16", "quality": "high", "resolution": "1k"},
 "header": "Storyboard keyframe ... full identity of every character, set, props locked by type/shape ...",
 "edit_header": "Photographed film still, vertical 9:16: real handmade felt puppets ... no text.",
 "masters": {"professor": "campaign-puppet/puppet-channel-concepts/professor/00-master-full-body.png",
             "nora": "campaign-puppet/puppet-channel-concepts/nora/00-master-full-body.png"},
 "frames": {
   "S1a": {"refs": ["professor", "nora"], "prompt": "WIDE shot ... (new setup: masters first)"},
   "S1b": {"mode": "edit", "refs": ["S1a"],
           "prompt": "Image 1 is the START of this same shot. EDIT Image 1, do not re-compose it: keep its camera, crop, set, light and both puppets' size, position and costumes pixel-identical. Change only this: ..."},
   "S3a": {"refs": ["professor", "S2b"], "prompt": "Image 2 is the previous shot ... (cut-in: masters first, then the frame it must match)"}
 }
}
- refs order = Image 1, 2, 3...; a ref is a master name, another frame key (dependency) or "file:<path>".
- "mode": "edit" uses edit_header (short, no identity restatement) instead of header. END frames of
  a clip should be edits of their START (0% camera drift in test-video-05, vs 6-14% otherwise).

Usage (sandbox off: it calls the local Test Lab):
  storyboard_rounds.py spec.json --dry-run                 # rounds + price, spends nothing
  storyboard_rounds.py spec.json                           # generate missing frames as <key>-v1.png
  storyboard_rounds.py spec.json --only S2b,S3b --tag v2   # re-roll frames as -v2 (refs use the selected versions)
  storyboard_rounds.py spec.json --resubmit-failed         # pay again for recorded jobs that ended failed/nsfw/canceled
  storyboard_rounds.py spec.json --resubmit S2b            # pay again for S2b even though a job is recorded (stuck job)
Selected version of a frame = <out>/selected.json {"S1b": "S1b-v8.png"}, else its highest -vN.
Re-runs never pay twice by default. Each job id is saved to <out>/jobs-<tag>.json right after its
submit. A re-run first waits on every recorded job whose <key>-<tag>.png is missing and downloads it.
If any of them is still pending, ended failed/nsfw/canceled, or completed without a saved PNG, the
script stops and submits nothing. A recorded frame is submitted again only when named in --resubmit,
or when it ended failed/nsfw/canceled and --resubmit-failed is given. The old job id is then kept in
<out>/jobs-<tag>-superseded.json before the new one replaces it in jobs-<tag>.json.
Uploaded media ids are cached in <out>/media-ids.json and re-uploaded after 6 h (their lifetime is unverified).
"""
import argparse, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hf_lab  # noqa: E402

def repo_root(_spec):
    # The skill lives at <repo>/.claude/skills/ai-puppet-video/scripts/, so the repo root is 4 levels up.
    # (Do not search for a ".claude" folder: Claude Code creates .claude/ in working directories.)
    return os.environ.get('PUPPET_REPO_ROOT') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))

def versions(out, key):
    return sorted((int(m.group(1)), f) for f in os.listdir(out) if (m := re.fullmatch(rf'{re.escape(key)}-v(\d+)\.png', f)))

def selected_file(out, key, sel):
    if key in sel: return os.path.join(out, sel[key])
    vs = versions(out, key)
    return os.path.join(out, vs[-1][1]) if vs else None

def rounds_for(frames, todo):
    deps = {k: [r for r in frames[k].get('refs', []) if r in frames] for k in frames}
    ready = set(frames) - set(todo); rounds = []; left = list(todo)
    while left:
        rnd = [k for k in left if all(d in ready for d in deps[k])]
        if not rnd: sys.exit(f'dependency cycle or missing frames among: {left}')
        rounds.append(rnd); ready |= set(rnd); left = [k for k in left if k not in rnd]
    return rounds

FAILED = ('failed', 'nsfw', 'canceled', 'cancelled')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only'); ap.add_argument('--tag', default='v1')
    ap.add_argument('--resubmit', default='', help='K1,K2: pay again for these frames although a job is recorded')
    ap.add_argument('--resubmit-failed', action='store_true', help='pay again for recorded jobs that ended failed/nsfw/canceled')
    a = ap.parse_args()
    root = repo_root(a.spec); spec = json.load(open(a.spec))
    R = lambda p: p if os.path.isabs(p) else os.path.join(root, p)
    out = R(spec['out_dir']); os.makedirs(out, exist_ok=True)
    frames = spec['frames']; settings = spec['settings']
    sel_p = os.path.join(out, 'selected.json'); sel = json.load(open(sel_p)) if os.path.exists(sel_p) else {}
    todo = a.only.split(',') if a.only else [k for k in frames if not selected_file(out, k, sel)]
    for k in todo:
        if k not in frames: sys.exit(f'unknown frame {k}')
        for r in frames[k].get('refs', []):
            if r in spec.get('masters', {}) and not os.path.exists(R(spec['masters'][r])): sys.exit(f'{k}: master {r} not found')
            if r.startswith('file:') and not os.path.exists(R(r[5:])): sys.exit(f'{k}: {r} not found')
            if r not in frames and r not in spec.get('masters', {}) and not r.startswith('file:'): sys.exit(f'{k}: unknown ref {r}')
    resub = set(filter(None, a.resubmit.split(',')))
    for k in resub - set(todo): sys.exit(f'--resubmit {k}: not among the frames to generate {todo}')
    rounds = rounds_for(frames, todo)
    print('repo root:', root); print('frames to generate:', len(todo)); [print(f'  round {i+1}: {r}') for i, r in enumerate(rounds)]
    if not todo: return
    png = lambda k: os.path.join(out, f'{k}-{a.tag}.png')
    jobs_p = os.path.join(out, f'jobs-{a.tag}.json'); jobs = json.load(open(jobs_p)) if os.path.exists(jobs_p) else {}
    sup_p = os.path.join(out, f'jobs-{a.tag}-superseded.json')
    recorded = [k for k in todo if k in jobs and k not in resub]
    if recorded: print(f'already submitted (recovered, not paid again unless --resubmit/--resubmit-failed): {recorded}')
    per = hf_lab.cost({'x': {**settings, 'prompt': 'price check'}})
    n = len(todo) - len(recorded)
    print(f'price: {per} credits/frame x {n} = {per * n} credits (re-rolls{" and --resubmit-failed frames" if a.resubmit_failed else ""} extra)')
    if a.dry_run: return
    status = {}  # recovered status of recorded jobs whose PNG is missing
    pending = {k: j for k, j in jobs.items() if not os.path.exists(png(k))}
    if pending:
        print('recovering submitted frames:', list(pending))
        waitable = {k: j for k, j in pending.items() if not str(j).startswith('NO_JOB_ID')}
        res = hf_lab.wait_jobs(list(waitable.values()), out, [f'{k}-{a.tag}' for k in waitable]) if waitable else {}
        for k in pending:
            st, f = (('submitted but no job id (check the Test Lab run log)', None) if k not in waitable
                     else res.get(f'{k}-{a.tag}', ('still pending', None)))
            status[k] = st; print(f'  {k}: {st} {f or ""}')
    blocked = []
    for k, st in status.items():
        if os.path.exists(png(k)) or k in resub or (st in FAILED and a.resubmit_failed): continue
        why = (f'{st}; pay again only after checking, with --resubmit {k}' if str(jobs[k]).startswith('NO_JOB_ID')
               else f'ended {st}; pay again only with --resubmit {k} or --resubmit-failed' if st in FAILED
               else f'{st}; re-run the same command later' if st != 'completed'
               else f'completed but {k}-{a.tag}.png was not saved (look in {out} for another extension); re-run to retry the download')
        blocked.append(f'  {k} (job {jobs[k]}): {why}')
    if blocked: sys.exit('recovered jobs are not all done; nothing new was submitted:\n' + '\n'.join(blocked))
    cache_p = os.path.join(out, 'media-ids.json'); cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    def media_id(path):
        st = os.stat(path); key = f'{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}'
        c = cache.get(key)
        if not c or not isinstance(c, dict) or time.time() - c.get('t', 0) > 6 * 3600:
            cache[key] = {'id': list(hf_lab.upload_files([path]).values())[0], 't': time.time()}
            json.dump(cache, open(cache_p, 'w'), indent=1)
        return cache[key]['id']
    for i, rnd in enumerate(rounds):
        params = {}
        for k in rnd:
            if os.path.exists(png(k)): print(f'  {k}-{a.tag}.png exists, skipping'); continue
            if k in jobs and not (k in resub or (a.resubmit_failed and status.get(k) in FAILED)):
                sys.exit(f'{k}: job {jobs[k]} is already recorded in {jobs_p}; not paying again (use --resubmit {k})')
            med = []
            for r in frames[k].get('refs', []):
                if r in spec.get('masters', {}): p = R(spec['masters'][r])
                elif r in frames:
                    new = os.path.join(out, f'{r}-{a.tag}.png')
                    p = new if (r in todo and os.path.exists(new)) else selected_file(out, r, sel)
                else: p = R(r[5:])
                if not p or not os.path.exists(p): sys.exit(f'{k}: ref {r} has no file yet')
                med.append({'role': 'image_references', 'value': media_id(p)})
            head = spec.get('edit_header', '') if frames[k].get('mode') == 'edit' else spec.get('header', '')
            params[k] = {**settings, 'batch_size': 1, 'prompt': (head.rstrip() + ' ' + frames[k]['prompt']).strip(), 'medias': med}
        if not params: continue
        json.dump(params, open(os.path.join(out, f'params-{a.tag}-round{i+1}.json'), 'w'), ensure_ascii=False, indent=1)
        for k, p in params.items():  # submit one by one and record each job id at once (paid)
            if k in jobs:  # explicit resubmit: keep the old job id before it is replaced
                sup = json.load(open(sup_p)) if os.path.exists(sup_p) else {}
                sup.setdefault(k, []).append({'job': jobs[k], 'status': status.get(k, 'unknown'), 'replaced_at': time.strftime('%Y-%m-%d %H:%M:%S')})
                json.dump(sup, open(sup_p, 'w'), indent=1)
            try:
                sub = hf_lab.generate({k: p})
            except RuntimeError as e:   # the call went out (credits may be spent) but no job id came back: record it, stop
                m = re.search(r'run (\S+?)\)', str(e)); jobs[k] = f'NO_JOB_ID:{m.group(1) if m else "unknown"}'
                json.dump(jobs, open(jobs_p, 'w'), indent=1)
                sys.exit(f'{k}: submitted but no job id returned ({e}). Check the Test Lab run log and the balance before paying again with --resubmit {k}.')
            jobs[k] = sub[k]['jobs'][0]; json.dump(jobs, open(jobs_p, 'w'), indent=1)
            print(f'  submitted {k}: {jobs[k]}  credits {sub[k]["before"]} -> {sub[k]["after"]}', flush=True)
        res = hf_lab.wait_jobs([jobs[k] for k in params], out, [f'{k}-{a.tag}' for k in params])
        for n, (st, f) in res.items(): print(f'  {n}: {st} {f or ""}', flush=True)
        if any(st != 'completed' or not f for st, f in res.values()):
            sys.exit('a frame failed, is still pending or was not downloaded. Re-run the same command to recover it; '
                     'nothing is paid again. A failed/nsfw frame needs --resubmit KEY or --resubmit-failed.')
    print('DONE. Now select versions in selected.json and run stages A-D (references/storyboard-qc.md) before showing anything.')

if __name__ == '__main__':
    main()
