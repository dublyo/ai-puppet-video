#!/usr/bin/env python3
"""Call Higgsfield through the local Test Lab (higgsfield-connector, http://localhost:8790).

The Test Lab holds the OAuth session, so this script never touches tokens. Start the lab
with preview_start name "higgsfield-connector" first. Calls to localhost need the Bash
sandbox disabled in this environment.

Commands:
  hf_lab.py cost     params.json [KEY ...]      free price check (adds get_cost:true), prints TOTAL;
                                                exits 1 with no TOTAL if any key gets no price
  hf_lab.py generate params.json [KEY ...]      submit (PAID - price + get approval first)
  hf_lab.py upload   a.png b.png ...            -> {"<path>": "<media_id>"} (upload + PUT + confirm)
  hf_lab.py wait     JOB [JOB ...] --out DIR [--names n1 n2 ...]   wait, then download results
                     (zsh does not word-split $VAR: pass lists as ${=VAR} or type them out)
  hf_lab.py balance

params.json is either ONE params object ({"model": ..., ...}) or {"KEY": params, ...}.
--tool generate_video|generate_image overrides the tool guessed from the model name.
Every generate call is logged by the lab (credits before/after) under
higgsfield-connector/data/runs/<run id>/; the run id is printed before anything else.
"""
import argparse, json, os, re, subprocess, sys, time, urllib.request

LAB = os.environ.get('HF_LAB', 'http://localhost:8790')
TYPES = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'webp': 'image/webp',
         'mp4': 'video/mp4', 'mov': 'video/quicktime', 'mp3': 'audio/mpeg', 'wav': 'audio/wav', 'm4a': 'audio/mp4'}

def req(method, path, body=None, timeout=300):
    r = urllib.request.Request(f'{LAB}{path}', method=method, data=json.dumps(body).encode() if body is not None else None,
                               headers={'content-type': 'application/json'})
    try:
        return json.load(urllib.request.urlopen(r, timeout=timeout))
    except urllib.error.URLError as e:
        s = str(e).lower()
        if 'refused' in s:
            sys.exit(f'Test Lab not reachable at {LAB}. Start it: preview_start name "higgsfield-connector" '
                     '(and run this script with the Bash sandbox off). If it is up, check /api/status for sign-in.')
        if 'not permitted' in s or 'errno 1]' in s:
            sys.exit('Blocked by the Bash sandbox: calls to localhost need dangerouslyDisableSandbox: true.')
        raise

def call(tool, args, log=False):
    return req('POST', '/api/call', {'tool': tool, 'args': args, 'log': log})

def tool_for(p, forced=None):
    if forced: return forced
    video = r'seedance|kling|wan|video|minimax|veo|upscale|fps_boost|deflicker|sync_so|intone|topaz|motion_control'
    if 'model' not in p: sys.exit('params need a "model"; pass --tool for tools that take no model')
    return 'generate_video' if re.search(video, p['model']) else 'generate_image'

def load_params(path, keys):
    d = json.load(open(path))
    if 'model' in d: return {'_': d}
    missing = [k for k in keys if k not in d]
    if missing: sys.exit(f'keys not in {path}: {missing}')
    return {k: d[k] for k in (keys or d.keys())}

def cmd_cost(a):
    tot, missing = 0, []
    for k, p in load_params(a.params, a.keys).items():
        r = call(tool_for(p, a.tool), {'params': {**p, 'get_cost': True}})['raw']
        c = ((r.get('structuredContent') or {}).get('cost') or {}).get('credits')
        if c is None: missing.append(k); print(k, 'NO PRICE:', json.dumps(r)[:300])
        else: tot += c; print(k, c)
    # like cost(): a missing price is never counted as 0, so no TOTAL is printed
    if missing: sys.exit(f'NO TOTAL: no price returned for {missing}. Fix those params and run cost again.')
    print('TOTAL', tot)

def cmd_generate(a):
    out, bad = {}, False
    for k, p in load_params(a.params, a.keys).items():
        r = call(tool_for(p, a.tool), {'params': p}, log=True)
        run = r.get('id'); print(k, 'run', run, flush=True)
        raw = r.get('raw') or (req('GET', f'/api/runs/{run}').get('raw') if run else {}) or {}
        jobs = [x.get('id') for x in (raw.get('structuredContent') or {}).get('results', []) if x.get('id')]
        if not jobs or r.get('error'):
            bad = True; print(k, 'NO JOB IDS - check the run before resubmitting:', r.get('error') or json.dumps(raw)[:400])
        out[k] = {'run': run, 'jobs': jobs, 'before': r.get('creditsBefore'), 'after': r.get('creditsAfter')}
        print(k, jobs, r.get('creditsBefore'), '->', r.get('creditsAfter'), flush=True)
    print(json.dumps(out, indent=1)); sys.exit(1 if bad else 0)

def cmd_upload(a):
    print(json.dumps(upload_files(a.files), indent=1))

def upload_files(files):
    """Upload local files; returns {path_as_given: media_id}. Importable."""
    names = []
    for i, f in enumerate(files):
        ext = f.rsplit('.', 1)[-1].lower()
        if ext not in TYPES: sys.exit(f'unknown extension: {f}')
        # unique upload name: masters all share the basename 00-master-full-body.png
        names.append(f'{i:02d}-{os.path.basename(os.path.dirname(os.path.abspath(f)))}-{os.path.basename(f)}')
    r = call('media_upload', {'files': [{'filename': n, 'content_type': TYPES[f.rsplit('.', 1)[-1].lower()]} for n, f in zip(names, files)]})['raw']
    txt = r['content'][0]['text']
    pairs = re.findall(r"- ([0-9a-f-]{36}):.*?--data-binary @(\S+) '(https://upload\.higgsfield\.ai/[^']+)'", txt)
    if len(pairs) != len(files): sys.exit(f'expected {len(files)} upload URLs, got {len(pairs)}:\n{txt[:500]}')
    byname = dict(zip(names, files)); ids = {}
    for mid, fn, url in pairs:
        f = byname.get(fn)
        if not f: sys.exit(f'upload reply names unknown file {fn}')
        ct = TYPES[f.rsplit('.', 1)[-1].lower()]
        code = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'PUT', '-H', f'Content-Type: {ct}',
                               '-H', 'If-None-Match: *', '--data-binary', '@' + f, url], capture_output=True, text=True).stdout
        if code != '200': sys.exit(f'PUT failed {code} for {f}')
        call('media_confirm', {'type': ct.split('/')[0] if ct.split('/')[0] in ('image', 'video', 'audio') else 'file', 'media_id': mid})
        ids[f] = mid
    return ids

def generate(params_by_key, tool=None):
    """Submit {key: params}; returns {key: {'run','jobs','before','after'}}. PAID. Importable."""
    out = {}
    for k, p in params_by_key.items():
        r = call(tool_for(p, tool), {'params': p}, log=True)
        run = r.get('id')
        raw = r.get('raw') or (req('GET', f'/api/runs/{run}').get('raw') if run else {}) or {}
        jobs = [x.get('id') for x in (raw.get('structuredContent') or {}).get('results', []) if x.get('id')]
        if not jobs: raise RuntimeError(f'{k}: no job ids (run {run}): {json.dumps(raw)[:300]}')
        out[k] = {'run': run, 'jobs': jobs, 'before': r.get('creditsBefore'), 'after': r.get('creditsAfter')}
    return out

def cost(params_by_key, tool=None):
    tot = 0
    for k, p in params_by_key.items():
        r = call(tool_for(p, tool), {'params': {**p, 'get_cost': True}})['raw']
        c = ((r.get('structuredContent') or {}).get('cost') or {}).get('credits')
        if c is None: raise RuntimeError(f'{k}: no price returned (do not treat as 0): {json.dumps(r)[:300]}')
        tot += c
    return tot

def cmd_wait(a):
    for n, (st, f) in wait_jobs(a.jobs, a.out, a.names).items(): print(n, st, f)

def wait_jobs(jobs, out, names=None):
    """Wait for jobs and download results; returns {name: (status, file)}. Importable."""
    os.makedirs(out, exist_ok=True); done = {}
    names = dict(zip(jobs, names or jobs))
    class A: pass
    a = A(); a.jobs = jobs; a.out = out
    for _ in range(120):
        pend = [j for j in a.jobs if j not in done]
        if not pend: break
        raw = call('jobs_wait', {'jobs': [{'index': i, 'job_id': j} for i, j in enumerate(pend)], 'timeout_seconds': 15})['raw']
        sc = raw.get('structuredContent') or {}
        for it in sc.get('jobs') or sc.get('results') or []:
            if it.get('status') in ('completed', 'failed', 'nsfw', 'canceled', 'cancelled'):
                done[it.get('job_id') or it.get('id')] = it
        # fallback: jobs_wait did not report every job when 13 were batched (2026-11-15); ask job_status directly
        for j in [j for j in pend if j not in done]:
            t = call('job_status', {'jobId': j})['raw'].get('content', [{}])[0].get('text', '')
            m = re.search(r'— (completed|failed|nsfw|canceled|cancelled)', t)
            if m: done[j] = {'job_id': j, 'status': m.group(1), 'text': t}
        print(f'{len(done)}/{len(a.jobs)} done', flush=True)
        if len(done) < len(a.jobs): time.sleep(5)
    res = {}
    for j in a.jobs:
        it = done.get(j, {})
        urls = [u for u in re.findall(r'https?://[^\s"\'\\]+\.(?:mp4|png|jpe?g|webp)', json.dumps(it)) if '_min.' not in u]
        f = None
        if urls:
            f = os.path.join(a.out, names[j] + os.path.splitext(urls[0])[1]); urllib.request.urlretrieve(urls[0], f)
        res[names[j]] = (it.get('status', 'still pending'), f)
    return res

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    for c in ('cost', 'generate'):
        s = sub.add_parser(c); s.add_argument('params'); s.add_argument('keys', nargs='*'); s.add_argument('--tool')
    s = sub.add_parser('upload'); s.add_argument('files', nargs='+')
    s = sub.add_parser('wait'); s.add_argument('jobs', nargs='+'); s.add_argument('--out', required=True); s.add_argument('--names', nargs='*')
    sub.add_parser('balance')
    a = ap.parse_args()
    if a.cmd == 'balance': print(json.dumps(call('balance', {})['raw'].get('structuredContent'), indent=1))
    else: globals()['cmd_' + a.cmd](a)

if __name__ == '__main__':
    main()
