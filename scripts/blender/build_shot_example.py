"""WORKED EXAMPLE (test-video-06 «نظرية التصفية», mockup v026) — copy into <project>/scripts/build_shot.py and adapt.
Route B of the ai-puppet-video skill: see references/blender-previs.md for the conventions this file encodes
(+X head rotation = down, puppet right hand = -X, keys from constants, custody by follow(), root to z-10 to remove a
character from a shot, render-only booleans, thin open water curves, numeric camera search).
Needs the blender-mcp-cinematic skill's live Blender + bridge.
"""
"""«نظرية التصفية» Blender pilot: colour-coded puppet mockups, kitchen set, props, cameras and blocking.
Run inside the live Blender:  PART='all'; exec(open(<this file>).read())
Parts: look, set, puppets, props, cameras, animate, all.
World: metres, Z up. Floor z=0, counter top z=0.80. Nora at -X, Professor at +X, cameras on -Y (180° rule).
Colour coding (unique per element) so Seedance maps mockup -> puppet: Nora plum/chestnut/PINK mitts,
Professor olive/brown ring hair/burgundy bow tie/bare orange-tan hands with olive cuffs, colander RED, knob RED.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

FPS, START, END = 24, 1, 480
CT = 0.80                      # counter top
SINK_X, SINK_Y, SINK_D = 0.28, 0.21, 0.20
D = math.radians
random.seed(7)

# ---------------------------------------------------------------- helpers
def hexcol(h, a=1.0):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]  # sRGB -> linear
    return (*c, a)

def mat(name, hx, alpha=1.0, rough=0.6, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    col = hexcol(hx, alpha); m.diffuse_color = col; m.roughness = rough; m.metallic = metal
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = col; b.inputs['Roughness'].default_value = rough
        b.inputs['Metallic'].default_value = metal; b.inputs['Alpha'].default_value = alpha
    if alpha < 1: m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    return m

def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
    else:
        c = bpy.data.collections.new(name); (parent or bpy.context.scene.collection).children.link(c)
    return c

def link(ob, c):
    for u in list(ob.users_collection): u.objects.unlink(ob)
    c.objects.link(ob); return ob

def prim(kind, name, c, loc=(0, 0, 0), size=(1, 1, 1), rot=(0, 0, 0), m=None, parent=None, seg=24, bevel=0.0):
    if kind == 'cube': bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == 'sphere': bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=seg, ring_count=max(8, seg // 2))
    elif kind == 'cyl': bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1, vertices=seg)
    elif kind == 'cone': bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0, depth=1, vertices=seg)
    elif kind == 'torus': bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.1, major_segments=seg, minor_segments=8)
    ob = bpy.context.active_object; ob.name = name; ob.data.name = name
    link(ob, c)
    ob.scale = size; ob.rotation_euler = Euler([D(a) for a in rot])
    if parent: ob.parent = parent
    ob.location = loc
    if m: ob.data.materials.append(m)
    if bevel:
        bv = ob.modifiers.new('bevel', 'BEVEL'); bv.width = bevel; bv.segments = 3
    bpy.ops.object.shade_smooth() if kind in ('sphere', 'cyl', 'torus') else None
    return ob

def empty(name, c, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None); c.objects.link(ob); ob.empty_display_size = 0.05
    if parent: ob.parent = parent
    ob.location = loc; ob.rotation_euler = Euler([D(a) for a in rot]); return ob

def cut_top(ob, z_local):
    """Delete faces above z_local (object space) -> open bowls/pots."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().z > z_local], context='FACES')
    bm.to_mesh(ob.data); bm.free()

def cut_front(ob, y_local, z_min):
    """Open a face window: delete faces in front (y < y_local) and below z_min (object space)."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().y < y_local and f.calc_center_median().z < z_min], context='FACES')
    bm.to_mesh(ob.data); bm.free()

def K(ob, f, loc=None, rot=None, sc=None, interp=None):
    if loc is not None: ob.location = loc; ob.keyframe_insert('location', frame=f)
    if rot is not None: ob.rotation_euler = Euler([D(a) for a in rot]); ob.keyframe_insert('rotation_euler', frame=f)
    if sc is not None: ob.scale = sc; ob.keyframe_insert('scale', frame=f)

def KW(ob, f, M):
    """Key ob so its WORLD matrix at frame f equals M (works with animated parents)."""
    sc = bpy.context.scene; sc.frame_set(f)
    ob.matrix_world = M
    ob.keyframe_insert('location', frame=f); ob.keyframe_insert('rotation_euler', frame=f); ob.keyframe_insert('scale', frame=f)

def follow(ob, owner, f0, f1, offset=None):
    """Bake ob rigidly attached to owner for frames f0..f1 (prop custody). Returns the offset used."""
    sc = bpy.context.scene; sc.frame_set(f0)
    if offset is None: offset = owner.matrix_world.inverted() @ ob.matrix_world
    for f in range(f0, f1 + 1):
        sc.frame_set(f); M = owner.matrix_world @ offset; KW(ob, f, M)
    return offset

def world(ob, f):
    bpy.context.scene.frame_set(f); return ob.matrix_world.copy()

def LR(loc, rot=(0, 0, 0)):
    return Matrix.LocRotScale(Vector(loc), Euler([D(a) for a in rot]), Vector((1, 1, 1)))

def noise(ob, path, idx, strength, scale=40.0, phase=0.0):
    bpy.context.scene.frame_set(START)          # key the frame-1 value, not whatever frame is current
    if path == 'scale': ob.scale[idx] = 1.0      # unanimated channel: reset, a previous run leaves it drifted
    ob.keyframe_insert(path, index=idx, frame=START)
    fc = ob.animation_data.action.fcurves.find(path, index=idx) if hasattr(ob.animation_data.action, 'fcurves') else None
    if fc is None:  # Blender 5 layered actions
        for layer in ob.animation_data.action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for f in cb.fcurves:
                        if f.data_path == path and f.array_index == idx: fc = f
    if fc:
        mo = fc.modifiers.new('NOISE'); mo.strength = strength; mo.scale = scale; mo.phase = phase

# ---------------------------------------------------------------- parts
def build_look():
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 720, 1280, 100
    sc.render.fps = FPS; sc.frame_start, sc.frame_end = START, END
    sh = sc.display.shading
    sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_shadows = True; sh.show_cavity = True
    sc.display.light_direction = (0.15, 0.35, 0.92); sc.display.shadow_shift = 0.1; sh.shadow_intensity = 0.35   # high key: no wall silhouettes
    sh.cavity_type = 'BOTH'; sh.show_object_outline = True; sh.show_specular_highlight = True
    try: sc.display.render_aa = '8'
    except Exception: pass
    sc.view_settings.view_transform = 'Standard'
    try: sc.view_settings.look = 'None'
    except Exception: pass
    sc.render.film_transparent = False
    w = sc.world or bpy.data.worlds.new('World'); sc.world = w; w.color = hexcol('#EFE3CC')[:3]
    sc.render.use_motion_blur = False; sc.render.use_stamp = False
    for n in ('Cube', 'Light', 'Camera'):
        o = bpy.data.objects.get(n)
        if o and not o.users_collection or (o and o.users_collection[0] == sc.collection): bpy.data.objects.remove(o, do_unlink=True)
    return {'look': 'workbench 720x1280'}

def build_set():
    c = coll('SET')
    marble = mat('marble', '#ECE8E1', rough=0.3); steel = mat('steel', '#A9AEB3', rough=0.25, metal=0.6)
    gold = mat('gold', '#C9A24A', rough=0.3, metal=0.8); cream = mat('wall_cream', '#EFE3CC')
    cab = mat('cabinet', '#E6DCC8'); floor = mat('floor_tile', '#C9B9A0'); sky = mat('window_sky', '#DCE8F0')
    curtain = mat('curtain', '#E9C9C0'); plate = mat('plate_blue', '#3E5FA0'); plate_w = mat('plate_white', '#F4F1EA')
    wood = mat('shelf_wood', '#B88A55'); frame = mat('picture_frame', '#8A6A3A'); pic = mat('picture', '#B9A57E')
    jar = mat('jar_blue_white', '#5B7BB8')
    prim('cube', 'floor', c, (0, 0.3, -0.005), (6, 6, 0.01), m=floor)
    prim('cube', 'back_wall', c, (0, 1.40, 2.5), (6, 0.02, 5), m=cream)
    prim('cube', 'side_wall_L', c, (-1.6, 0.4, 2.5), (0.02, 3, 5), m=cream)
    # counter slab with sink hole (boolean) + cabinets
    slab = prim('cube', 'counter', c, (0, 0.025, CT - 0.02), (2.6, 0.65, 0.04), m=marble)
    hole = prim('cube', 'sink_hole_cutter', c, (0, 0, CT - 0.02), (2 * SINK_X, 2 * SINK_Y, 0.2))
    b = slab.modifiers.new('hole', 'BOOLEAN'); b.object = hole; b.operation = 'DIFFERENCE'; hole.hide_render = True; hole.hide_viewport = True
    prim('cube', 'cabinet_front', c, (0, -0.27, (CT - 0.04) / 2), (2.6, 0.06, CT - 0.04), m=cab)
    # sink basin (open box) + rim
    basin = prim('cube', 'sink_basin', c, (0, 0, CT - SINK_D / 2), (2 * SINK_X, 2 * SINK_Y, SINK_D), m=steel)
    cut_top(basin, 0.45)
    bm = bmesh.new(); bm.from_mesh(basin.data); bmesh.ops.reverse_faces(bm, faces=bm.faces[:]); bm.to_mesh(basin.data); bm.free()
    rim = prim('cube', 'sink_rim', c, (0, 0, CT + 0.004), (2 * SINK_X + 0.08, 2 * SINK_Y + 0.08, 0.008), m=steel)
    r2 = prim('cube', 'rim_cutter', c, (0, 0, CT), (2 * SINK_X, 2 * SINK_Y, 0.1)); r2.hide_render = r2.hide_viewport = True
    br = rim.modifiers.new('hole', 'BOOLEAN'); br.object = r2; br.operation = 'DIFFERENCE'
    prim('cyl', 'drain', c, (0, 0, CT - SINK_D + 0.002), (0.07, 0.07, 0.004), m=mat('drain', '#6E7378'))
    # gold gooseneck faucet on the right rim
    cu = bpy.data.curves.new('faucet', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.014; cu.bevel_resolution = 4
    sp = cu.splines.new('BEZIER'); pts = [(0.36, 0.0, CT), (0.36, 0.0, CT + 0.30), (0.30, 0.0, CT + 0.36), (0.22, 0.0, CT + 0.28)]
    sp.bezier_points.add(len(pts) - 1)
    for p, co in zip(sp.bezier_points, pts): p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
    fo = bpy.data.objects.new('faucet', cu); c.objects.link(fo); cu.materials.append(gold)
    prim('cyl', 'faucet_base', c, (0.36, 0.0, CT + 0.015), (0.06, 0.06, 0.03), m=gold)
    prim('cube', 'faucet_lever', c, (0.36, 0.05, CT + 0.05), (0.015, 0.08, 0.015), m=gold)
    # back wall dressing (S1a geography)
    prim('cube', 'window', c, (-0.70, 1.385, 1.75), (0.50, 0.01, 0.90), m=sky)
    prim('cube', 'window_frame_v', c, (-0.70, 1.38, 1.75), (0.03, 0.01, 0.90), m=plate_w)
    prim('cube', 'curtain_L', c, (-1.0, 1.37, 1.75), (0.14, 0.02, 1.0), m=curtain)
    prim('cube', 'curtain_top', c, (-0.70, 1.37, 2.23), (0.66, 0.02, 0.14), m=curtain)
    prim('cyl', 'plate', c, (-0.10, 1.38, 1.95), (0.30, 0.30, 0.02), rot=(90, 0, 0), m=plate)
    prim('cyl', 'plate_center', c, (-0.10, 1.37, 1.95), (0.18, 0.18, 0.02), rot=(90, 0, 0), m=plate_w)
    prim('cube', 'shelf', c, (0.30, 1.30, 1.60), (0.70, 0.18, 0.03), m=wood)
    for i, x in enumerate((0.10, 0.28, 0.46)):
        prim('cyl', f'jar_{i}', c, (x, 1.30, 1.70), (0.09, 0.09, 0.16 + 0.03 * i), m=jar)
    prim('cube', 'picture_frame', c, (0.85, 1.38, 1.80), (0.34, 0.02, 0.42), m=frame)
    prim('cube', 'picture', c, (0.85, 1.37, 1.80), (0.28, 0.02, 0.36), m=pic)
    prim('cube', 'back_cabinets', c, (0, 1.12, 0.45), (2.6, 0.55, 0.9), m=cab)
    prim('cube', 'back_counter', c, (0, 1.12, 0.92), (2.6, 0.56, 0.04), m=marble)
    return {'set': len(c.objects)}

PUP = {
 'nora': dict(x=-0.28, yaw=30, skin='#E3A46B', top='#5E2A3E', shirt='#F1E7D2', legs='#2F3D3A', hair='#5A2E1C', hand='mitt'),
 'prof': dict(x=0.30, yaw=-30, skin='#E3A46B', top='#4B4A1E', shirt='#F1E7D2', legs='#3A2A1E', hair='#4A3020', hand='bare'),
}

def build_puppet(key):
    p = PUP[key]; c = coll('PUP_' + key)
    skin = mat(f'{key}_skin', p['skin']); top = mat(f'{key}_top', p['top']); shirt = mat(f'{key}_shirt', p['shirt'])
    legs = mat(f'{key}_legs', p['legs']); hair = mat(f'{key}_hair', p['hair']); white = mat('eye_white', '#FAFAF7', rough=0.2)
    pupil = mat('pupil', '#3B2314', rough=0.2); dark = mat('mouth_line', '#4A2418'); shoe = mat('shoe', '#4A3222')
    root = empty(f'{key}_ROOT', c, (p['x'], 0.45, 0), rot=(0, 0, p['yaw']))
    torso = empty(f'{key}_TORSO', c, (0, 0, 0.62), parent=root)
    prim('cube', f'{key}_legs', c, (0, 0, -0.27), (0.30, 0.20, 0.54), m=legs, parent=torso, bevel=0.04)
    for s in (-1, 1): prim('cube', f'{key}_shoe_{s}', c, (0.08 * s, -0.04, -0.585), (0.11, 0.18, 0.07), m=shoe, parent=torso, bevel=0.02)
    prim('cyl', f'{key}_body', c, (0, 0, 0.26), (0.42, 0.30, 0.52), m=top, parent=torso)
    prim('cube', f'{key}_shirt', c, (0, -0.135, 0.30), (0.13, 0.04, 0.42), m=shirt, parent=torso)
    neck = empty(f'{key}_NECK', c, (0, 0, 0.53), parent=torso)
    head = empty(f'{key}_HEAD', c, (0, 0, 0.02), parent=neck)
    prim('sphere', f'{key}_face', c, (0, 0, 0.20), (0.34, 0.32, 0.40), m=skin, parent=head, seg=32)
    prim('sphere', f'{key}_nose', c, (0, -0.165, 0.18), (0.075, 0.07, 0.07), m=skin, parent=head)
    prim('cube', f'{key}_mouth', c, (0, -0.15, 0.09), (0.10, 0.01, 0.012), m=dark, parent=head)
    for s in (-1, 1):  # ears
        prim('sphere', f'{key}_ear_{s}', c, (0.17 * s, 0.0, 0.20), (0.05, 0.03, 0.08), m=skin, parent=head)
    eyes = {}
    for s, side in ((-1, 'R'), (1, 'L')):
        piv = empty(f'{key}_EYE_{side}', c, (0.065 * s, -0.125, 0.26), parent=head)
        prim('sphere', f'{key}_eyewhite_{side}', c, (0, 0, 0), (0.085, 0.07, 0.085), m=white, parent=piv)
        prim('sphere', f'{key}_pupil_{side}', c, (0, -0.032, 0), (0.035, 0.02, 0.035), m=pupil, parent=piv)
        lid = prim('sphere', f'{key}_lid_{side}', c, (0, -0.004, 0.012), (0.092, 0.078, 0.06), m=skin, parent=piv)
        lid.scale = (0.001, 0.001, 0.001)  # open = no lid geometry (a lid line read as spectacles); closed = (0.095, 0.085, 0.10)
        brow = prim('cube', f'{key}_brow_{side}', c, (0.065 * s, -0.15, 0.335), (0.09, 0.02, 0.018), rot=(0, 8 * s, 0),
                    m=mat(f'{key}_brow', '#3A2212' if key == 'nora' else '#141010'), parent=head, bevel=0.005)
        eyes[side] = (piv, lid, brow)
    if key == 'nora':  # chestnut bob helmet (silhouette marker)
        bob = prim('sphere', 'nora_bob', c, (0, 0.03, 0.23), (0.46, 0.42, 0.50), m=hair, parent=head, seg=32)
        cut_front(bob, -0.15, 0.22)
        bs_ = bob.modifiers.new('thick', 'SOLIDIFY'); bs_.thickness = 0.02
        prim('sphere', 'nora_fringe', c, (0.03, -0.13, 0.37), (0.30, 0.12, 0.10), m=hair, parent=head, rot=(0, -10, 0))
        prim('cube', 'nora_collar', c, (0, -0.14, 0.50), (0.20, 0.05, 0.05), m=shirt, parent=torso, bevel=0.02)
    else:  # bald dome + clumpy dark ring of hair (silhouette marker) + burgundy bow tie
        for i in range(22):   # wispy dark-brown fringe around the back and sides, bald dome on top
            a = D(-125 + i * (250 / 21)); r = 0.165
            prim('sphere', f'prof_hair_{i}', c, (r * math.sin(a), r * math.cos(a) * 0.85 + 0.03, 0.27 + 0.05 * math.cos(a) + 0.015 * (i % 2)),
                 (0.065, 0.065, 0.075), m=hair, parent=head, seg=10)
        bow = empty('prof_BOWTIE', c, (0, -0.16, 0.50), parent=torso, rot=(0, -30, 0))
        bt = mat('bowtie_burgundy', '#7A1F2B')
        for s in (-1, 1):
            prim('cone', f'prof_bow_{s}', c, (0.045 * s, 0, 0), (0.09, 0.05, 0.09), rot=(0, 90 * s, 0), m=bt, parent=bow, seg=3)
        prim('sphere', 'prof_bow_knot', c, (0, -0.01, 0), (0.035, 0.03, 0.035), m=bt, parent=bow)
        prim('cube', 'prof_lapel', c, (0, -0.15, 0.38), (0.24, 0.02, 0.26), m=top, parent=torso, bevel=0.01)
    # arms: shoulder empties (on torso) + hand empties (parented to torso, re-keyed in world for custody)
    hands = {}
    for s, side in ((-1, 'R'), (1, 'L')):
        sh_ = empty(f'{key}_SHOULDER_{side}', c, (0.20 * s, 0, 0.46), parent=torso)
        hand = empty(f'{key}_HAND_{side}', c, (0.24 * s, -0.10, 0.20), parent=torso)
        if p['hand'] == 'mitt':
            mm = mat('mitt_pink', '#E58FA6', rough=0.8)
            prim('sphere', f'nora_mitt_{side}', c, (0, 0, 0), (0.14, 0.10, 0.21), m=mm, parent=hand)
            prim('sphere', f'nora_mitt_thumb_{side}', c, (-0.07 * s, -0.01, 0.02), (0.06, 0.06, 0.09), m=mm, parent=hand)
            prim('cyl', f'nora_mitt_cuff_{side}', c, (0, 0, 0.12), (0.13, 0.09, 0.06), m=mm, parent=hand)
            sleeve = top
        else:
            prim('cube', f'prof_palm_{side}', c, (0, 0, 0), (0.08, 0.035, 0.08), m=skin, parent=hand, bevel=0.015)
            for i, fx in enumerate((-0.025, 0.0, 0.025)):
                prim('cyl', f'prof_finger_{side}_{i}', c, (fx, 0, -0.065), (0.022, 0.022, 0.06), m=skin, parent=hand)
            prim('cyl', f'prof_thumb_{side}', c, (-0.05 * s, -0.01, -0.01), (0.022, 0.022, 0.05), rot=(0, 50 * s, 0), m=skin, parent=hand)
            prim('cyl', f'prof_cuff_{side}', c, (0, 0, 0.06), (0.075, 0.075, 0.05), m=top, parent=hand)
            sleeve = top
        wrist = empty(f'{key}_WRIST_{side}', c, (0, 0, 0.07), parent=hand)
        # arm = unit cylinder along +Y, copy location of shoulder, stretch to wrist
        bpy.ops.mesh.primitive_cylinder_add(radius=0.036, depth=1, vertices=16)   # thinner: a thick long stretch arm came back as a dark slab
        arm = bpy.context.active_object; arm.name = f'{key}_arm_{side}'; link(arm, c)
        arm.data.transform(Matrix.Translation((0, 0, 0.5))); arm.data.transform(Matrix.Rotation(D(-90), 4, 'X'))
        arm.data.materials.append(sleeve); bpy.ops.object.shade_smooth()
        cl = arm.constraints.new('COPY_LOCATION'); cl.target = sh_
        st = arm.constraints.new('STRETCH_TO'); st.target = wrist; st.rest_length = 1.0; st.volume = 'NO_VOLUME'
        hands[side] = hand
    return {'puppet': key, 'objects': len(c.objects)}

def torus(name, c, loc, R, r, m=None, parent=None, rot=(0, 0, 0), seg=24):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=8)
    ob = bpy.context.active_object; ob.name = name; ob.data.name = name; link(ob, c)
    ob.rotation_euler = Euler([D(a) for a in rot])
    if parent: ob.parent = parent
    ob.location = loc
    if m: ob.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return ob

def elbow_mesh(pasta):
    """One chunky elbow macaroni (half torus, ~3 cm) shared by every pasta piece."""
    me = bpy.data.meshes.get('elbow_mesh')
    if me is None:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.012, minor_radius=0.0048, major_segments=14, minor_segments=6)
        tmp = bpy.context.active_object
        bm = bmesh.new(); bm.from_mesh(tmp.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.002], context='VERTS')
        bm.to_mesh(tmp.data); bm.free()
        me = tmp.data; me.name = 'elbow_mesh'; bpy.data.objects.remove(tmp, do_unlink=True)
    if not me.materials: me.materials.append(pasta)
    return me

def build_props():
    coll('WATER'); coll('PASTA')   # clear first: a leftover object would push the new one to a '.001' name
    c = coll('PROPS')
    alu = mat('pot_aluminium', '#C3C7CB', rough=0.3, metal=0.7); inner = mat('pot_inner', '#5E6368', rough=0.4)
    red = mat('colander_red', '#E02424', rough=0.4); holes = mat('colander_holes', '#2B2B2B')
    knob = mat('lid_knob_red', '#D21F26', rough=0.3); glass = mat('lid_glass', '#C9D6DE', alpha=0.4, rough=0.05)
    steel = mat('lid_rim_steel', '#5F656B', rough=0.3, metal=0.6); pasta = mat('pasta_yellow', '#F2D27A', rough=0.6)
    wat = mat('water', '#3FB7E6', alpha=0.75, rough=0.05); jet = mat('water_stream', '#E8FAFF', alpha=0.85, rough=0.05)
    pud = mat('water_puddle', '#8ADCF4', alpha=0.45, rough=0.05)
    # pot: darker inner wall so the open crescent of the gap contrasts
    pot = empty('POT', c, (-0.08, 0.02, 0.98))
    body = prim('cyl', 'pot_body', c, (0, 0, 0), (0.26, 0.26, 0.16), m=alu, parent=pot, seg=32); cut_top(body, 0.45)
    body.data.materials.append(inner)
    sol = body.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = 0.01; sol.material_offset = 1
    for s in (-1, 1):
        prim('torus', f'pot_handle_{s}', c, (0.155 * s, 0, 0.05), (0.08, 0.08, 0.25), rot=(90, 0, 0), m=alu, parent=pot)
    prim('cyl', 'pot_water', c, (0, 0, 0.062), (0.245, 0.245, 0.006), m=wat, parent=pot, seg=32)
    torus('pot_wetline', c, (0, 0, 0.062), 0.121, 0.003, m=mat('wetline', '#2F5A6E'), parent=pot, seg=40)
    # pasta visible in the pot from frame 1 (pieces poke through the water): one joined mesh
    me = elbow_mesh(pasta); ev = [v.co.copy() for v in me.vertices]; ef = [tuple(p.vertices) for p in me.polygons]
    V, Fc = [], []
    for i in range(130):
        a = random.uniform(0, 2 * math.pi); r = 0.105 * math.sqrt(random.random())
        M = Matrix.LocRotScale(Vector((r * math.cos(a), r * math.sin(a), random.uniform(0.02, 0.068))),
                               Euler([random.uniform(0, 6.28) for _ in range(3)]), Vector((1, 1, 1)))
        b0 = len(V); V += [M @ v for v in ev]; Fc += [tuple(b0 + k for k in f) for f in ef]
    pm = bpy.data.meshes.new('pot_pasta'); pm.from_pydata(V, [], Fc); pm.materials.append(pasta)
    po = bpy.data.objects.new('pot_pasta', pm); c.objects.link(po); po.parent = pot
    # lid: near-clear glass dome + opaque steel rim + red knob (reads as a lid, not as water)
    lid = empty('LID', c, (-0.08, 0.02, 0.98 + 0.085))
    prim('sphere', 'lid_dome', c, (0, 0, 0), (0.275, 0.275, 0.06), m=glass, parent=lid, seg=32)
    torus('lid_rim', c, (0, 0, -0.004), 0.137, 0.011, m=steel, parent=lid, seg=40)
    prim('sphere', 'lid_knob', c, (0, 0, 0.035), (0.05, 0.05, 0.04), m=knob, parent=lid)
    # colander: red bowl with rings of holes (inside and out) and flat tab handles
    col = empty('COLANDER', c, (0.02, 0.0, CT - SINK_D + 0.005))
    bowl = prim('sphere', 'colander_bowl', c, (0, 0, 0.11), (0.22, 0.22, 0.22), m=red, parent=col, seg=32); cut_top(bowl, 0.0)
    bowl.data.materials.append(mat('colander_inner', '#F06A5A', rough=0.4))   # lighter inside: dark discs read as openings
    bs = bowl.modifiers.new('thick', 'SOLIDIFY'); bs.thickness = 0.012; bs.material_offset = 1
    torus('colander_foot', c, (0, 0, 0.012), 0.06, 0.008, m=red, parent=col)
    for s in (-1, 1):
        prim('cube', f'colander_tab_{s}', c, (0.13 * s, 0, 0.105), (0.06, 0.045, 0.012), m=red, parent=col, bevel=0.004)
    cc = coll('COLANDER_CUTTERS'); k = 0          # real perforations: you can see through them (round-3: dark discs read as polka dots)
    for th, cnt in ((0, 1), (14, 6), (30, 10), (46, 14), (62, 18)):
        for j in range(cnt):
            ph = D(j * 360 / cnt + (8 if th in (30, 62) else 0)); t = D(th)
            n = Vector((math.sin(t) * math.cos(ph), math.sin(t) * math.sin(ph), -math.cos(t)))
            h = prim('cyl', f'colander_cut_{k}', cc, tuple(Vector((0, 0, 0.11)) + n * 0.104), (0.013, 0.013, 0.06), parent=col, seg=10)
            h.rotation_euler = n.to_track_quat('Z', 'Y').to_euler(); h.hide_render = True; h.display_type = 'WIRE'; k += 1
    bb = bowl.modifiers.new('holes', 'BOOLEAN'); bb.operation = 'DIFFERENCE'; bb.operand_type = 'COLLECTION'; bb.collection = cc
    bb.solver = 'FLOAT' if 'FLOAT' in [i.identifier for i in bb.bl_rna.properties['solver'].enum_items] else bb.solver
    bb.show_viewport = False   # render-only: evaluating 49 cutters on every frame_set made baking hang the live bridge
    # pasta pieces that pour out (share one mesh)
    pc = coll('PASTA')
    for i in range(200):
        ob = bpy.data.objects.new(f'pasta_{i:03d}', me); pc.objects.link(ob); ob.location = (0, 0, -5)
    # water: thinning stream (origin at top), splash ring, puddle, droplets
    wc = coll('WATER')
    for nm in ('water_stream', 'water_gush_L', 'water_gush_R'):   # open tubes (no caps), points + radii keyed per frame in animate()
        cu = bpy.data.curves.new(nm, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.01; cu.bevel_resolution = 3
        cu.use_fill_caps = False; cu.resolution_u = 10
        sp = cu.splines.new('NURBS'); sp.points.add(4); sp.order_u = 3; sp.use_endpoint_u = True
        for p in sp.points: p.co = (0, 0, -5, 1); p.radius = 0.0
        cu.materials.append(jet); so = bpy.data.objects.new(nm, cu); wc.objects.link(so)
    torus('water_splash', wc, (0, 0, -5), 0.5, 0.08, m=jet, seg=24)
    prim('cyl', 'water_puddle', wc, (0.0, 0.0, CT - SINK_D + 0.004), (0.001, 0.001, 0.006), m=pud, seg=32)
    for i in range(6):
        prim('sphere', f'water_drop_{i}', wc, (0, 0, -5), (0.013, 0.013, 0.017), m=jet, seg=8)   # round-ish falling drops
    for i in range(32):
        prim('sphere', f'water_blob_{i}', wc, (0, 0, -5), (0.02, 0.02, 0.036), m=jet, seg=10)   # gush break-up
    return {'props': len(c.objects), 'pasta': len(pc.objects), 'water': len(wc.objects)}

# ---------------------------------------------------------------- layout constants (each checked by BVH overlap / frustum tests)
COL_COUNTER = (0.10, 0.23, CT)                   # colander rest: between them, clear of both bellies, the pot and Nora's idle mitts
POT_LIFT_MID = (0.20, 0.06, 1.28)                # empty pot lifted above the faucet (gooseneck top ~1.16)
POT_SET_ABOVE = (0.60, 0.0, 0.94)
POT_REST = (0.66, 0.0, CT + 0.08)                # set down on the counter right of the faucet; his hands are then free
NORA_GRAB_ROOT = (-0.22, 0.47, 0)                # Nora's small step toward the colander (clear of his hanging right arm)
# Nora lets go of the pot: mitts drop into the sink under the pot, then come back on her own side (never cross his arm)
NORA_RELEASE = {'L': ((130, (0.03, -0.02, 0.88)), (136, (-0.12, 0.18, 0.90))),
                'R': ((130, (-0.11, -0.02, 0.88)), (136, (-0.26, 0.16, 0.90)))}
CROWN_MID1 = (0.06, 0.22, 1.18)                  # flip at chest height, in front of the gap between them
CROWN_MID2 = (0.08, 0.28, 1.76)                  # straight up, above both heads
CROWN_MID3 = (0.20, 0.42, 1.78)                  # across above his head, then down onto it
# colander lift: (frame, centre, yaw deg) - turns 90 deg so the side tabs clear the sink wall and the pot
COLANDER_PATH = ((65, (0.14, 0.02, 0.62), 90), (69, (0.20, 0.05, 0.86), 90), (73, (0.14, 0.20, 0.87), 0), (76, COL_COUNTER, 0))
CAM_TWO_LOC, CAM_TWO_AIM, CAM_TWO_LENS = (1.10, -1.00, 1.40), (0.0, 0.42, 1.24), 32   # from HIS side, 36 deg off the wide axis: colander stands clear of the pot

CAMS = {  # name: (location, aim, lens)
 'CAM_WIDE': ((0.03, -1.40, 1.46), (0.01, 0.35, 1.14), 28),   # establishing: >=10% side margin, room for the colander arc
 'CAM_TWO': (CAM_TWO_LOC, CAM_TWO_AIM, CAM_TWO_LENS),
 'CAM_PROF_LOW': ((-0.15, -0.75, 1.05), (0.30, 0.45, 1.30), 50),
 'CAM_TOPDOWN': ((0.10, -0.62, 1.30), (0.0, 0.0, 0.90), 38),   # front-right, lower: the front pour lip faces the lens
 'CAM_NORA_CU': ((0.12, -0.68, 1.42), (-0.28, 0.45, 1.31), 45),   # colander fully out (no clipped red fragment)
 'CAM_PROF_CU': ((-0.25, -0.62, 1.50), (0.30, 0.45, 1.22), 36),   # eyes on the upper third, bow tie well inside
}
CUTS = [(1, 'CAM_WIDE'), (85, 'CAM_TWO'), (145, 'CAM_PROF_LOW'), (197, 'CAM_TOPDOWN'), (277, 'CAM_NORA_CU'), (325, 'CAM_WIDE'), (397, 'CAM_PROF_CU')]

def build_cameras():
    c = coll('CAMERAS'); sc = bpy.context.scene
    for n, (loc, aim, lens) in CAMS.items():
        cd = bpy.data.cameras.get(n) or bpy.data.cameras.new(n); cd.lens = lens; cd.sensor_fit = 'AUTO'; cd.sensor_width = 36
        cd.clip_start = 0.02
        cam = bpy.data.objects.new(n, cd); c.objects.link(cam); cam.location = loc
        if aim:
            t = empty(n + '_AIM', c, aim); tc = cam.constraints.new('TRACK_TO'); tc.target = t
            tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
        else:
            cam.rotation_euler = (0, 0, 0)
    sc.timeline_markers.clear()
    for f, n in CUTS:
        m = sc.timeline_markers.new(n, frame=f); m.camera = bpy.data.objects[n]
    sc.camera = bpy.data.objects['CAM_WIDE']
    cam = bpy.data.objects['CAM_PROF_LOW']; K(cam, 145, loc=(-0.15, -0.75, 1.05)); K(cam, 196, loc=(-0.15 + 0.045, -0.75 + 0.11, 1.05 + 0.02))
    return {'cameras': len(CAMS)}

# ---------------------------------------------------------------- animation (blocking)
def O(n): return bpy.data.objects[n]

def clear_anim():
    for o in bpy.data.objects:
        if o.animation_data and not o.name.startswith('CAM_'): o.animation_data_clear()   # camera moves are keyed in build_cameras

def hand_rest(key, side, f, pose='rest'):
    """Key a hand in torso-local space."""
    s = -1 if side == 'R' else 1; h = O(f'{key}_HAND_{side}')
    P = {'rest': ((0.24 * s, -0.10, 0.20), (0, 0, 0)), 'chest': ((0.16 * s, -0.24, 0.42), (-20, 0, 0)),
         'raised': ((0.20 * s, -0.20, 0.62), (-10, 0, 0)), 'belly': ((0.09 * s, -0.15, 0.32), (-60, 0, 0))}[pose]
    K(h, f, loc=P[0], rot=P[1])

def animate():
    sc = bpy.context.scene; clear_anim()
    pot, lid, col = O('POT'), O('LID'), O('COLANDER')
    nroot, proot = O('nora_ROOT'), O('prof_ROOT')
    nhead, phead = O('nora_HEAD'), O('prof_HEAD'); ntorso, ptorso = O('nora_TORSO'), O('prof_TORSO')
    NL, NR, PL, PR = O('nora_HAND_L'), O('nora_HAND_R'), O('prof_HAND_L'), O('prof_HAND_R')
    A = (-0.08, 0.02, 1.06)                       # pot hold position (Nora), over the sink; high enough for the colander to pass under
    COL_SINK = (0.08, 0.0, CT - SINK_D + 0.005)  # colander in the sink, right of centre (his side)
    FLOOR = CT - SINK_D + 0.005
    GRIP = 127                                    # he has both handles
    # ---- Nora is not in shots 4 and 7: her root drops 10 m under the floor for those frames (keyed hide_render did not stick in
    #      Blender 5: each insert made a detached action). Insurance against the AI adding her; also kills her shadow after the exit.
    # ---- roots (body blocking)
    K(nroot, 1, loc=(-0.28, 0.45, 0), rot=(0, 0, 30)); K(proot, 1, loc=(0.30, 0.45, 0), rot=(0, 0, -30))
    K(proot, 12, loc=(0.30, 0.45, 0)); K(proot, 22, loc=(0.30, 0.45, 0.04)); K(proot, 40, loc=(0.30, 0.45, 0.04)); K(proot, 50, loc=(0.30, 0.45, 0))
    K(ptorso, 12, rot=(0, 0, 0)); K(ptorso, 26, rot=(8, 0, 0)); K(ptorso, 44, rot=(8, 0, 0)); K(ptorso, 60, rot=(12, 0, 0)); K(ptorso, 80, rot=(0, 0, 0))
    K(nroot, 318, loc=(-0.28, 0.45, 0), rot=(0, 0, 30)); K(nroot, 334, loc=NORA_GRAB_ROOT, rot=(0, 0, 45))
    K(nroot, 346, loc=NORA_GRAB_ROOT, rot=(0, 0, 60)); K(nroot, 372, loc=NORA_GRAB_ROOT, rot=(0, 0, 65))
    K(nroot, 380, loc=(-0.26, 0.48, 0.0), rot=(0, 0, -60))
    for i, (f, x) in enumerate(((384, -0.40), (388, -0.70), (392, -1.05))):
        K(nroot, f, loc=(x, 0.48, 0.015 if i % 2 == 0 else 0.0), rot=(0, 0, -90))   # profile, face-first to screen-left
    K(nroot, 393, loc=(-3.0, 0.48, -10.0)); K(nroot, 480, loc=(-3.0, 0.48, -10.0))
    for f, z in ((196, 0.0), (197, -10.0), (276, -10.0), (277, 0.0)):
        K(nroot, f, loc=(-0.28, 0.45, z), rot=(0, 0, 30))
    # ---- heads. List convention: negative X = looks down, positive = chin up (keyed as -X)
    for f, r in ((1, (0, 0, 0)), (12, (0, 0, 0)), (20, (-6, 0, 0)), (30, (-6, 0, 0)), (34, (-6, 0, 18)), (39, (-6, 0, -18)),
                 (44, (-6, 0, 18)), (48, (-6, 0, 0)),                                       # slow pitying head shake at the colander
                 (76, (-10, 0, 0)), (79, (-2, 0, 0)), (82, (-10, 0, 0)), (90, (-8, 0, 10)),
                 (100, (-6, 0, 12)), (104, (4, 0, 12)), (112, (4, 0, 14)), (118, (2, 0, 12)), (122, (-10, 0, 0)),
                 (178, (-6, 0, 0)), (186, (16, 0, 5)), (191, (7, 0, 6)), (196, (16, 0, 6)),   # chin up, deliberate smug nod
                 (214, (8, 0, 10)), (240, (8, 0, 12)), (256, (12, 0, 0)), (266, (12, 0, 0)), (272, (-4, 0, 0)),
                 (277, (-18, 0, 0)), (325, (-22, 0, 0)), (410, (-22, 0, 0)), (420, (-22, 0, 0)), (424, (-24, 0, 0)), (434, (-10, 0, -22)),
                 (446, (8, 0, -15)), (466, (12, 0, -12)), (480, (13, 0, -12))):   # slow smug chin-up settle in the hold
        K(phead, f, rot=(-r[0], r[1], r[2]))
    for f, r in ((1, (-15, 0, 0)), (70, (-15, 0, 0)), (84, (-5, 0, 15)), (126, (-5, 0, 15)), (138, (-8, 0, 10)), (276, (-8, 0, 10)),
                 (277, (-6, 0, 5)), (324, (-6, 0, 5)), (325, (-10, 0, 10)), (356, (5, 0, 0)), (372, (0, 0, 0))):
        K(nhead, f, rot=(-r[0], r[1], r[2]))
    # ---- eyes: pupils (eye pivots), lids (open = no lid geometry; closed = lid covers the eye and the pupil is hidden), brows
    def gaze(key, f, rx, rz):
        for side in ('L', 'R'): K(O(f'{key}_EYE_{side}'), f, rot=(-rx, 0, rz))
    def lids(key, f, l, r):
        for side, v in (('L', l), ('R', r)):
            K(O(f'{key}_lid_{side}'), f, sc=(0.001, 0.001, 0.001) if v == 0 else (0.095, 0.085, 0.001 + 0.1 * v))
            K(O(f'{key}_pupil_{side}'), f, sc=(0.001, 0.001, 0.001) if v >= 0.9 else (0.035, 0.02, 0.035))
    for f, rx, rz in ((1, -25, 0), (70, -25, 0), (78, -5, 25), (132, -5, 25), (138, -20, 30), (276, -20, 30), (277, 0, 10),
                      (300, 0, 10), (306, -22, 28), (316, -22, 28), (320, 0, 10), (324, 0, 10), (325, -15, 25), (372, -15, 25)):
        gaze('nora', f, rx, rz)
    for f, rx, rz in ((1, -25, -10), (12, -30, 0), (76, -10, -25), (120, -20, -10), (212, -20, -10), (272, -30, 0), (325, -30, -5),
                      (420, -30, -5), (428, -35, 0), (440, -5, -30), (480, -5, -30)):
        gaze('prof', f, rx, rz)
    lids('nora', 1, 0, 0); lids('nora', 480, 0, 0)
    for f, l, r in ((1, 0, 0), (145, 0, 0), (150, 1, 0), (182, 1, 0), (186, 1, 1), (266, 1, 1), (271, 0, 0), (408, 0, 0),
                    (410, 1, 1), (413, 0, 0), (418, 0, 0), (420, 1, 1), (423, 0, 0), (444, 0, 0), (450, 0.5, 0.5), (480, 0.5, 0.5)):
        lids('prof', f, l, r)
    nb = O('nora_brow_L'); B = (0.065, -0.15, 0.335); K(nb, 1, loc=B); K(nb, 132, loc=B); K(nb, 140, loc=(B[0], B[1], B[2] + 0.03))
    for s, side, up in ((-1, 'R', 0.012), (1, 'L', 0.025)):   # asymmetric smug brows (shot 3 + the final hold), drop at the 'what?'
        pb = O(f'prof_brow_{side}'); PB = (0.065 * s, -0.15, 0.335)
        K(pb, 1, loc=PB); K(pb, 180, loc=PB); K(pb, 188, loc=(PB[0], PB[1], PB[2] + up)); K(pb, 266, loc=(PB[0], PB[1], PB[2] + up)); K(pb, 272, loc=PB)
        K(pb, 444, loc=PB); K(pb, 452, loc=(PB[0], PB[1], PB[2] + up * 0.8))
    pm = O('prof_mouth'); MB = (0, -0.15, 0.09)   # smirk: one corner up
    for f, rz in ((1, 0), (182, 0), (188, 10), (266, 10), (272, 0), (444, 0), (452, 10), (480, 10)): K(pm, f, loc=MB, rot=(0, -rz, 0))
    # ---- pot master animation. The pour tilts about X (the handle axis): +X rotation lowers the FRONT (-Y) lip toward the camera
    for f, loc, rx in ((1, A, 0), (112, A, 0), (120, (-0.04, 0.0, 1.06), 0), (GRIP, (-0.04, 0.0, 1.06), 0), (142, (0.0, 0.02, 1.02), 0),
                       (166, (0.0, 0.02, 1.01), 2), (182, (0.0, 0.02, 1.00), -2), (196, (0.0, 0.02, 1.00), 0), (204, (0.0, 0.02, 1.00), 2),
                       (212, (0.0, 0.02, 1.01), 6), (216, (0.0, 0.02, 1.01), 12), (228, (0.0, 0.02, 1.02), 18), (240, (0.0, 0.02, 1.02), 24),
                       (244, (0.0, 0.02, 1.02), 28), (248, (0.0, 0.02, 1.02), 40), (252, (0.0, 0.02, 1.02), 56), (258, (0.0, 0.02, 1.02), 70),
                       (264, (0.0, 0.02, 1.02), 72), (268, POT_LIFT_MID, 30), (274, POT_SET_ABOVE, 0), (278, POT_REST, 0), (480, POT_REST, 0)):
        K(pot, f, loc=loc, rot=(rx, 0, 0))
    # ---- lid rides the pot (keyed before anything reads its pose)
    sc.frame_set(1); lid.location = (A[0], A[1], A[2] + 0.085); lid.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
    lid_off = pot.matrix_world.inverted() @ lid.matrix_world   # from constants, never from a stale pose of a previous run
    follow(lid, pot, 1, 203, offset=lid_off)
    GAP = 0.03                                     # a SLIVER: the lid's front rim still overhangs the pasta and holds it back
    def lid_at(f, dy, dx=0.0, dz=0.0): KW(lid, f, world(pot, f) @ Matrix.Translation(Vector((dx, dy, dz))) @ lid_off)
    lid_at(210, GAP)                               # his hand on the lid rim pushes it back: thin crescent opens on the front pour lip
    follow(lid, pot, 210, 242, offset=Matrix.Translation(Vector((0, GAP, 0))) @ lid_off)
    def lid_roll(f, dy, dx, dz, ry):
        KW(lid, f, world(pot, f) @ Matrix.Translation(Vector((dx, dy, dz))) @ Matrix.Rotation(D(ry), 4, 'Y') @ lid_off)
    for f, dy, dx, dz, ry in ((244, 0.015, 0, 0, 0), (246, 0.0, 0, 0, 0), (247, 0.0, 0, 0, 0),              # creep, hitch at the lip
                              (249, -0.02, -0.10, -0.02, -25), (251, -0.04, -0.22, -0.06, -55), (253, -0.05, -0.32, -0.10, -70)):
        lid_roll(f, dy, dx, dz, ry)                                   # slips off SIDEWAYS (screen-left), turning edge-on to the lens
    KW(lid, 255, LR((-0.20, 0.02, 0.90), (0, -50, 0)))
    KW(lid, 258, LR((-0.12, 0.05, FLOOR + 0.05), (0, -14, 0)))
    KW(lid, 262, LR((-0.12, 0.05, FLOOR + 0.035), (0, -6, 0)))     # lands nearly flat at the back-left of the basin, whole rim visible
    LID_LAND = Vector((-0.12, 0.05))
    # ---- Nora's mitts cradle the pot from below (the side handles stay free for him)
    for side, mx in (('L', 0.08), ('R', -0.08)):
        h = O(f'nora_HAND_{side}')
        KW(h, 1, world(pot, 1) @ LR((mx * 0.85, -0.02, -0.135), (90, 0, 0)))   # palms up under the pot: the pot stays fully visible
        follow(h, pot, 1, GRIP)
        for f, p in NORA_RELEASE[side]: KW(h, f, LR(p, (90, 0, 0)))   # stays flat (palms up) while it clears the pot base
        hand_rest('nora', side, 142, 'belly'); hand_rest('nora', side, 200, 'belly'); hand_rest('nora', side, 318, 'belly')
    # ---- Professor hands: rest; right hand lifts the colander out (low, behind the pot) to the counter between them
    for side in ('L', 'R'): hand_rest('prof', side, 1, 'rest'); hand_rest('prof', side, 44, 'rest')
    K(col, 1, loc=COL_SINK, rot=(0, 0, 0)); K(col, 62, loc=COL_SINK, rot=(0, 0, 0))
    KW(PR, 62, LR(Vector(COL_SINK) + Vector((0.12, -0.02, 0.17)), (0, 0, 0)))
    off = follow(col, PR, 62, 62)
    for f, p, yaw in COLANDER_PATH:
        KW(PR, f, LR(p, (0, 0, yaw)) @ off.inverted())
    follow(col, PR, 62, 76, offset=off)
    K(col, 77, loc=COL_COUNTER, rot=(0, 0, 0)); K(col, 324, loc=COL_COUNTER, rot=(0, 0, 0))
    hand_rest('prof', 'R', 79, 'rest')
    knob = lambda f: (world(lid, f).translation + Vector((0.02, -0.03, 0.09)))
    for f, up in ((82, 0.05), (85, 0.0), (89, 0.05), (92, 0.0), (97, 0.06)):   # the cut at f85 lands on the first tap
        KW(PR, f, LR(knob(f) + Vector((0, 0, up)), (0, 0, 0)))
    # 'the lid IS the strainer': ONE index finger up beside (not over) his head, held f104-118 with a small wag
    # LEFT hand (camera side in shot 2) raises the index finger beside his head: the arm never crosses his face
    hd = lambda f: world(phead, f).translation
    hand_rest('prof', 'R', 103, 'chest'); hand_rest('prof', 'R', 121, 'chest')   # right hand waits at chest height, well above the colander
    up_at = lambda f, dz=0.0: LR(hd(f) + Vector((0.26, -0.14, 0.25 + dz)), (180, 0, 0))    # beside his head (his left), temple height
    KW(PL, 101, LR(hd(101) + Vector((0.34, -0.18, 0.02)), (150, 0, 0)))                    # rises out to the side
    for f, dz in ((104, 0.0), (108, 0.02), (110, 0.0), (114, 0.02), (116, 0.0), (119, 0.0)): KW(PL, f, up_at(f, dz))
    KW(PL, 121, LR(hd(121) + Vector((0.34, -0.18, 0.02)), (150, 0, 0)))                    # comes down the same outside path
    fingers = [O('prof_finger_L_1'), O('prof_finger_L_2'), O('prof_thumb_L')]   # finger_L_0 (thumb side) stays up = index finger
    for o in fingers:   # curl the other fingers + thumb so the silhouette is a single index finger
        L0, S0 = o.location.copy(), o.scale.copy()
        if not o.name.startswith('prof_thumb'): L0.z, S0.z = -0.065, 0.06
        else: L0.z, S0.z = -0.01, 0.05
        Lc = Vector((L0.x, L0.y, -0.042 if 'finger' in o.name else -0.005)); Sc = Vector((S0.x, S0.y, 0.018 if 'finger' in o.name else 0.015))
        for f, (l, s_) in ((1, (L0, S0)), (99, (L0, S0)), (101, (Lc, Sc)), (121, (Lc, Sc)), (123, (L0, S0))):
            K(o, f, loc=tuple(l), sc=tuple(s_))
    hand_rest('prof', 'L', 98, 'rest')
    # grips: OUTSIDE the side handles, so the arms stay beside the pot (never across its mouth) while it tips toward the lens
    for side, hx in (('R', -0.20), ('L', 0.20)):
        h = O(f'prof_HAND_{side}'); hp = world(pot, GRIP) @ Vector((hx, 0.03, 0.06))
        KW(h, 124 if side == 'R' else 125, LR(hp + Vector((0, -0.02, 0.14)), (0, 0, 0)))   # short, fast reach that comes down from ABOVE the handle
        KW(h, GRIP, LR(hp, (0, 0, 0)))
    offR = follow(PR, pot, GRIP, 200); follow(PL, pot, GRIP, 278); hand_rest('prof', 'L', 288, 'rest')
    # his right hand ON the lid's front-left rim pushes the lid back (hand and lid move together), then returns to the handle
    on_rim = LR((-0.06, -0.11, 0.11), (80, 0, 0))   # palm-down on the front-left rim, fingers lying along the glass
    KW(PR, 201, world(lid, 201) @ Matrix.Translation(Vector((0, 0, 0.05))) @ on_rim)
    for f in (203, 206, 210, 212): KW(PR, f, world(lid, f) @ on_rim)
    KW(PR, 216, world(pot, 216) @ offR)
    follow(PR, pot, 217, 238, offset=offR)
    KW(PR, 242, world(pot, 242) @ LR((-0.18, 0.12, -0.10), (0, 0, 0)))   # hand under/behind the base: lifts the bottom to tip it
    follow(PR, pot, 242, 278); hand_rest('prof', 'R', 288, 'rest'); hand_rest('prof', 'R', 426, 'rest')
    # bow tie: pinch the wing from the side while it straightens (earlier), hand clears, ~1 s hold of the straight tie + smug lids
    bt = O('prof_BOWTIE')
    K(bt, 1, rot=(0, -30, 0)); K(bt, 434, rot=(0, -30, 0)); K(bt, 442, rot=(0, 0, 0))
    for f in (432, 442):
        KW(PR, f, LR(world(bt, f).translation + Vector((-0.08, -0.05, 0.0)), (0, 0, 0)))
    hand_rest('prof', 'R', 448, 'rest')   # 32-frame smug hold f448-480
    # ---- water. Level drops clearly while it drains (pasta stays above it); the stream is a curve tube that starts INSIDE the pot
    #      at the water surface, runs over the lip through the gap and falls under gravity (no caps); the gush is the same tube, wide
    pw = O('pot_water'); WZ = {1: 0.062, 214: 0.062, 244: 0.02}
    K(pw, 1, loc=(0, 0, 0.062), sc=(0.245, 0.245, 0.006)); K(pw, 214, loc=(0, 0, 0.062), sc=(0.245, 0.245, 0.006))
    K(pw, 240, loc=(0, 0, 0.004), sc=(0.215, 0.215, 0.004)); K(pw, 251, loc=(0, 0, 0.004), sc=(0.215, 0.215, 0.004))
    K(pw, 252, loc=(0, -0.06, 0.012), sc=(0.21, 0.15, 0.004)); K(pw, 253, loc=(0, -0.12, 0.03), sc=(0.19, 0.06, 0.003))
    K(pw, 254, loc=(0, -0.12, 0.03), sc=(0.001, 0.001, 0.001))   # remaining water leaves over the lip, then is gone
    def wz(f): return 0.062 if f <= 214 else (0.062 + (0.004 - 0.062) * min(1, (f - 214) / 26))
    streams = [O('water_stream'), O('water_gush_L'), O('water_gush_R')]
    for s_ in streams:
        if s_.data.animation_data: s_.data.animation_data_clear()
    def key_curve(ob, f, pts, radii):
        for p, co, rr in zip(ob.data.splines[0].points, pts, radii):
            p.co = (co.x, co.y, co.z, 1.0); p.radius = rr
            p.keyframe_insert('co', frame=f); p.keyframe_insert('radius', frame=f)
    def path(f, dx=0.0, deep=False, fan=0.0, wob=0.0):
        M = world(pot, f)
        if not deep:   # trickle: water surface -> visibly ON the lip -> hangs off it with air between stream and wall
            p0 = M @ Vector((dx, -0.075, wz(f) + 0.004)); p1 = M @ Vector((dx, -0.135, 0.105)); p2 = M @ Vector((dx, -0.19, 0.085))
            p3 = Vector((p2.x + fan * 0.5 + wob, p2.y - 0.04, FLOOR + (p2.z - FLOOR) * 0.45)); p4 = Vector((p2.x + fan + wob * 0.5, p2.y - 0.05 - abs(fan) * 0.3, FLOOR))
        else:          # gush: starts AT the lip, arcs forward, breaks up (radius 0) well above the floor
            p0 = M @ Vector((dx, -0.12, 0.08)); p1 = M @ Vector((dx, -0.15, 0.10)); p2 = p1 + Vector((0, -0.06, -0.06))
            p3 = p1 + Vector((0, -0.10, -(p1.z - FLOOR) * 0.5)); p4 = Vector((p1.x, p1.y - 0.12, FLOOR + 0.06))
        return [p0, p1, p2, p3, p4]
    ring, pud = O('water_splash'), O('water_puddle')
    for s_ in streams: key_curve(s_, 1, path(1), [0] * 5); key_curve(s_, 215, path(215), [0] * 5)
    K(ring, 1, loc=(0, 0, -5), sc=(0.001, 0.001, 0.001)); K(ring, 215, loc=(0, 0, -5), sc=(0.001, 0.001, 0.001))
    K(pud, 1, loc=(0, 0, FLOOR - 0.001), sc=(0.001, 0.001, 0.006))
    for f in range(216, 264):
        if f < 252:   # trickle: thin at the lip, thinning as the water runs out
            w = 1.1 * (1 - 0.3 * max(0, f - 236) / 15) * (1 + 0.25 * math.sin(f * 2.9))
            key_curve(streams[0], f, path(f), [0.6 * w, 1.0 * w, 0.9 * w, 0.7 * w, 0.35 * w])
            for s_ in streams[1:]: key_curve(s_, f, path(f), [0] * 5)
            land = path(f)[4]; rs = 0.05 + 0.01 * math.sin(f * 2.3)
        else:         # gush: three THIN streams over the lip, same look as the trickle (pilot v1: a thick tube + blobs came back as a
                      # white tube with egg shapes; the thin trickle came back as real water). The pasta pieces carry the volume.
            g = min(1, (f - 251) / 3) * (1 - max(0, f - 260) / 3)   # starts ~4 frames AFTER the lid has slipped (cause, then effect)
            for s_, dx, k, fan, f_on, f_off in ((streams[0], 0.0, 1.7, 0.02, 252, 262), (streams[1], -0.05, 1.1, -0.09, 254, 259),
                                               (streams[2], 0.055, 0.9, 0.10, 256, 261)):   # fanned, uneven, staggered: water, not rods
                gg = min(1, max(0, f - f_on + 1) / 3) * (1 - max(0, f - f_off + 3) / 3) if f_on <= f <= f_off else 0.0
                wob = 0.012 * math.sin(f * 1.9 + dx * 40)
                key_curve(s_, f, path(f, dx, fan=fan, wob=wob), [0.8 * k * gg, 1.0 * k * gg, 0.85 * k * gg, 0.6 * k * gg, 0.3 * k * gg])
            land = path(f)[4]; rs = 0.06 + 0.01 * g
        K(ring, f, loc=(land.x, land.y, FLOOR + 0.002), sc=(rs, rs, 0.35))
        centre = Vector((land.x, land.y, FLOOR - 0.001)).lerp(Vector((-0.02, -0.03, FLOOR - 0.001)), max(0.0, min(1.0, (f - 240) / 22)))
        K(pud, f, loc=tuple(centre))
    for s_ in streams: key_curve(s_, 264, path(264), [0] * 5)
    K(ring, 264, loc=(0, 0, -5), sc=(0.001, 0.001, 0.001))
    for f, sxy in ((216, (0.001, 0.001)), (240, (0.20, 0.15)), (248, (0.24, 0.18)), (262, (0.52, 0.38)), (324, (0.48, 0.34)), (480, (0.32, 0.22))):
        K(pud, f, sc=(sxy[0], sxy[1], 0.006))
    for k in range(32):  # gush blobs disabled: pilot v1 rendered them as white eggs
        K(O(f'water_blob_{k}'), 1, loc=(0, 0, -5))
    for k in range(6):   # droplets leave from the lip and fall clear of the wall, beside the stream
        dr = O(f'water_drop_{k}'); K(dr, 1, loc=(0, 0, -5))
        for f in range(218 + k, 245, 6):
            p2 = path(f)[2]; side = (-1 if k % 2 else 1) * random.uniform(0.04, 0.06)
            K(dr, f - 1, loc=(0, 0, -5)); K(dr, f, loc=(p2.x + side, p2.y - 0.03, p2.z - 0.01))
            K(dr, f + 4, loc=(p2.x + side * 1.2, p2.y - 0.04, FLOOR + 0.012)); K(dr, f + 5, loc=(0, 0, -5))
    # ---- pasta: stays in the pot through the drain, then SLIDES out over the lip with the gush (never shrinks in place)
    pp = O('pot_pasta')
    K(pp, 1, loc=(0, 0, 0), sc=(1, 1, 1)); K(pp, 214, loc=(0, 0, 0), sc=(1, 1, 1)); K(pp, 240, loc=(0, 0, -0.02), sc=(1, 1, 1))
    K(pp, 251, loc=(0, 0, -0.02), sc=(1, 1, 1)); K(pp, 254, loc=(0, -0.12, 0.05), sc=(1, 1, 1)); K(pp, 257, loc=(0, -0.24, -0.04), sc=(1, 1, 1))
    K(pp, 258, loc=(0, -0.24, -0.04), sc=(0.001, 0.001, 0.001))   # hidden only once it is outside the rim
    pieces = sorted([o for o in bpy.data.collections['PASTA'].objects if o.name.startswith('pasta_')], key=lambda o: o.name)
    for i, ob in enumerate(pieces):
        f0 = 252 + int(i * 0.045); f1 = f0 + 6 + random.randint(0, 3)
        start = world(pot, f0) @ Vector((random.uniform(-0.08, 0.08), -0.13, 0.09))
        x, y = random.uniform(-0.21, 0.21), random.uniform(-0.17, 0.12)
        dl = math.hypot(x - LID_LAND.x, y - LID_LAND.y)
        if dl < 0.07:   # keep the knob clear so the landed lid still reads as a lid
            x, y = LID_LAND.x + (x - LID_LAND.x) / max(dl, 1e-3) * 0.16, LID_LAND.y + (y - LID_LAND.y) / max(dl, 1e-3) * 0.16
            dl = 0.16
        if dl < 0.15:
            land = Vector((x, y, FLOOR + 0.07 + random.uniform(0, 0.01)))     # lands on top of the fallen lid, not inside it
        else:
            heap = 0.03 * max(0.0, 1 - math.hypot(x, y + 0.03) / 0.22)
            land = Vector((x, y, FLOOR + 0.01 + random.uniform(0, 0.015) + heap))
        r0 = [random.uniform(0, 360) for _ in range(3)]; r1 = [a + random.uniform(-200, 200) for a in r0]
        K(ob, 1, loc=(0, 0, -5)); K(ob, f0 - 1, loc=(0, 0, -5)); K(ob, f0, loc=start, rot=r0); K(ob, f1, loc=land, rot=r1)
    # ---- colander: Nora grabs it (f334), flips it at chest height (f340), lifts it above both heads (f346-352), crowns him (f358)
    sc.frame_set(334)
    def colM(loc, rx): return Matrix.LocRotScale(Vector(loc), Euler((D(rx), 0, 0)), Vector((1, 1, 1)))
    KW(NL, 334, LR((COL_COUNTER[0] + 0.12, COL_COUNTER[1] - 0.05, CT + 0.10), (0, -90, 0)))
    KW(NR, 334, LR((COL_COUNTER[0] - 0.12, COL_COUNTER[1] - 0.05, CT + 0.10), (0, 90, 0)))
    hand_rest('nora', 'L', 326, 'belly'); hand_rest('nora', 'R', 326, 'belly')
    coff = follow(col, NL, 334, 334)
    sc.frame_set(358); head_top = phead.matrix_world @ Vector((0, 0.0, 0.40))
    for f, M in ((340, colM(CROWN_MID1, 90)), (346, colM(CROWN_MID2, 180)), (352, colM(CROWN_MID3, 180)), (358, colM(head_top + Vector((0, 0, 0.11)), 180))):
        KW(NL, f, M @ coff.inverted())
    follow(col, NL, 334, 358, offset=coff)
    follow(NR, col, 334, 358)
    follow(col, phead, 358, 480)
    # pat on the colander's near side rim (her arm stays low, beside her own head, not across her face)
    KW(NL, 366, LR(world(col, 366).translation + Vector((-0.125, 0.0, -0.03)), (0, 0, 90)))   # palm flat on the colander's upper side
    KW(NL, 367, LR(world(col, 367).translation + Vector((-0.15, 0.0, -0.02)), (0, 0, 90)))
    KW(NL, 369, LR(world(col, 369).translation + Vector((-0.125, 0.0, -0.03)), (0, 0, 90)))
    KW(NL, 372, LR(world(col, 372).translation + Vector((-0.28, 0.02, -0.18)), (0, 0, 0)))
    hand_rest('nora', 'L', 378, 'rest'); hand_rest('nora', 'R', 366, 'belly'); hand_rest('nora', 'R', 384, 'rest')
    # ---- life: breathing + micro sway (avoid mannequin stillness and dead tails)
    for key, ph in (('nora', 0.0), ('prof', 3.0)):
        noise(O(f'{key}_TORSO'), 'scale', 2, 0.02, 36, ph); noise(O(f'{key}_HEAD'), 'rotation_euler', 2, 0.02, 30, ph + 1)
    sc.frame_set(1)
    return {'animated': True}

def scene_report():
    sc = bpy.context.scene
    return {'objects': len(bpy.data.objects), 'frames': [sc.frame_start, sc.frame_end], 'camera': sc.camera.name if sc.camera else None,
            'markers': [(m.frame, m.camera.name if m.camera else None) for m in sc.timeline_markers], 'file': bpy.data.filepath}

PART = globals().get('PART', 'all')
out = {}
if PART in ('look', 'all'): out.update(build_look())
if PART in ('set', 'all'): out.update(build_set())
if PART in ('puppets', 'all'): out.update({'nora': build_puppet('nora'), 'prof': build_puppet('prof')})
if PART in ('props', 'all'): out.update(build_props())
if PART in ('cameras', 'all'): out.update(build_cameras())
if PART in ('animate', 'all'): out.update(animate())
out.update(scene_report())
result = out
