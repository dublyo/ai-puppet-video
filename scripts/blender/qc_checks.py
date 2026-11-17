"""Numeric QC for the previs scene. Run inside the live Blender:  exec(open(<this file>).read())  -> `result`.
- overlaps: world-space BVH overlap between mesh pairs over frame ranges (props passing through bodies/props)
- intruders: vertices of a character who must not be in a shot, inside that shot's camera frustum
- framing: where key points land in the frame (0..1, y up) at given frames
Characters absent from a shot have their ROOT keyed to z -10 (keyed hide_render does not stick in Blender 5; see blender-previs.md §3),
so a plain inside() check must return {} for them; skip_hidden only matters for objects whose hide_render is set statically.
TEMPLATE: the helper functions are generic; the check block after `R = lambda` uses test-video-06 object names, cameras and frame
ranges -- copy this file to <project>/scripts/qc_checks.py, rewrite that block, and save each result to review/qc-vNNN.json.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

sc = bpy.context.scene
C = bpy.data.objects

def tree(name):
    o = C[name]; dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); me = ev.to_mesh()
    mw = o.matrix_world; t = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    ev.to_mesh_clear(); return t

def overlaps(a_names, b_names, frames):
    hits = {}
    for f in frames:
        sc.frame_set(f)
        A = {n: tree(n) for n in a_names}; B = {n: tree(n) for n in b_names}
        for an, at in A.items():
            for bn, bt in B.items():
                if at.overlap(bt): hits.setdefault(f'{an}|{bn}', []).append(f)
    return {k: f'{v[0]}-{v[-1]} ({len(v)} frames)' for k, v in hits.items()}

def inside(cam, names, frames, skip_hidden=False):
    dg = bpy.context.evaluated_depsgraph_get(); h = {}
    for f in frames:
        sc.frame_set(f)
        for n in names:
            o = C[n]
            if skip_hidden and o.hide_render: continue
            me = o.evaluated_get(dg).data
            k = sum(1 for v in me.vertices if (lambda p: 0 < p.x < 1 and 0 < p.y < 1 and p.z > 0)(world_to_camera_view(sc, C[cam], o.matrix_world @ v.co)))
            if k: h.setdefault(n, []).append(f)
    return {k: f'{v[0]}-{v[-1]} ({len(v)})' for k, v in h.items()}

def where(cam, pts, f):
    sc.frame_set(f); out = {}
    for label, p in pts.items():
        q = world_to_camera_view(sc, C[cam], p() if callable(p) else p)
        out[label] = (round(q.x, 2), round(q.y, 2))
    return out

def bbox_extent(cam, names, f):
    """min/max frame x,y of the named objects' vertices (to judge edge margins)."""
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); xs, ys = [], []
    for n in names:
        o = C[n]; me = o.evaluated_get(dg).data
        for v in me.vertices:
            q = world_to_camera_view(sc, C[cam], o.matrix_world @ v.co); xs.append(q.x); ys.append(q.y)
    return (round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3))

R = lambda a, b, s=2: list(range(a, b + 1, s))
faucet = ['faucet', 'faucet_base', 'faucet_lever']
res = {}
res['pot_vs_world'] = overlaps(['pot_body'], ['colander_bowl', 'prof_body', 'nora_body', 'prof_face', 'counter', 'faucet_base', 'faucet_lever'], R(1, 480, 3))
try:
    res['pot_vs_faucet_curve'] = 'faucet is a curve; checked via faucet_base/lever + framing'
except Exception: pass
res['colander_vs_world'] = overlaps(['colander_bowl'], ['pot_body', 'nora_body', 'prof_body', 'nora_face', 'nora_bob', 'prof_face', 'nora_mitt_L', 'nora_mitt_R'], R(56, 360, 2))
res['lid_vs_pot'] = overlaps(['lid_dome'], ['pot_body'], R(196, 262, 1))
res['hands_handover'] = overlaps(['nora_mitt_L', 'nora_mitt_R'], ['prof_palm_L', 'prof_palm_R', 'prof_arm_L', 'prof_arm_R'], R(96, 150, 1))
res['prof_arm_vs_nora'] = overlaps(['prof_arm_R', 'prof_arm_L'], ['nora_body', 'nora_face', 'nora_bob'], R(100, 276, 4))
res['crown_arms_faces'] = overlaps(['nora_arm_L', 'nora_arm_R'], ['nora_face', 'nora_bob', 'prof_face'], R(334, 372, 2))
nora_parts = ['nora_mitt_L', 'nora_mitt_R', 'nora_bob', 'nora_body', 'nora_face', 'nora_arm_L', 'nora_arm_R']
res['shot4_nora_geom_in_frame'] = inside('CAM_TOPDOWN', nora_parts, R(197, 276, 3))
res['shot4_nora_rendered'] = inside('CAM_TOPDOWN', nora_parts, R(197, 276, 3), skip_hidden=True)
res['shot5_prof_or_pot'] = inside('CAM_NORA_CU', ['prof_face', 'prof_palm_L', 'prof_palm_R', 'pot_body', 'prof_body', 'prof_arm_R', 'prof_arm_L', 'prof_cuff_R', 'prof_cuff_L'], R(277, 324, 2))
res['shot7_nora_rendered'] = inside('CAM_PROF_CU', nora_parts, R(397, 480, 4), skip_hidden=True)
res['shot6_nora_after_exit_rendered'] = inside('CAM_WIDE', nora_parts, R(390, 396, 1), skip_hidden=True)
pot = C['POT']
res['shot4_points'] = {f: where('CAM_TOPDOWN', {
    'lip': lambda: pot.matrix_world @ Vector((0, -0.14, 0.072)), 'pot': lambda: pot.matrix_world.translation,
    'prof_face': lambda: C['prof_face'].matrix_world.translation, 'sink_floor': Vector((0, 0, 0.605))}, f) for f in (200, 210, 230, 250, 262, 276)}
res['shot4_pot_extent'] = {f: bbox_extent('CAM_TOPDOWN', ['pot_body', 'lid_dome'], f) for f in (200, 230, 250)}
res['shot2_extent_heads'] = {f: {'nora': bbox_extent('CAM_TWO', ['nora_bob'], f), 'prof': bbox_extent('CAM_TWO', ['prof_face'] + [f'prof_hair_{i}' for i in range(22)], f),
                                 'knob': where('CAM_TWO', {'k': lambda: C['lid_knob'].matrix_world.translation}, f)['k']} for f in (85, 100, 124, 144)}
res['wide_extent'] = {f: {'nora': bbox_extent('CAM_WIDE', ['nora_bob'], f), 'prof': bbox_extent('CAM_WIDE', ['prof_face'] + [f'prof_hair_{i}' for i in range(22)], f)} for f in (1, 84, 325)}
res['shot7_eyes_y'] = {f: where('CAM_PROF_CU', {'eye': lambda: C['prof_EYE_L'].matrix_world.translation, 'col_top': lambda: C['colander_foot'].matrix_world.translation,
                                               'bowtie': lambda: C['prof_BOWTIE'].matrix_world.translation}, f) for f in (397, 440, 466, 480)}
sc.frame_set(1)
result = res
