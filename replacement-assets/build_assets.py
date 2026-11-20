#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Build original player geometry and keyframes from dimensions, pivots and motion curves."""
from hashlib import sha256
import json
import boss_motions
import entity_models
import enderman_motions
import mob_motions
import sound_events
from math import cos, pi, radians, sin
import struct
import zlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = 'assets/epicfight/animmodels'
# Pivots in Minecraft model space (metres), from the feet to the head.
PIVOTS = {
    'Root': (None, (0, .91, 0)), 'Torso': ('Root', (0, 1.00, 0)),
    'Chest': ('Torso', (0, 1.30, 0)), 'Head': ('Chest', (0, 1.53, 0)),
}
for side, sign in [('R', -1), ('L', 1)]:
    def joint(name, parent, x, y, z=0):
        PIVOTS[name + '_' + side] = (parent if parent in ('Root', 'Chest') else parent + '_' + side, (sign*x, y, z))
    joint('Thigh', 'Root', .127, .91)
    joint('Leg', 'Thigh', .127, .47)
    joint('Knee', 'Leg', .127, .45, .025)
    joint('Shoulder', 'Chest', .285, 1.48)
    joint('Arm', 'Shoulder', .345, 1.43)
    joint('Hand', 'Arm', .35, 1.12)
    joint('Elbow', 'Hand', .35, 1.105, -.012)
    joint('Tool', 'Hand', .35, .83, .035)


# Vertex IDs consumed by VanillaModelTransformer and the optional armor renderers.
JOINTS = ('Root', 'Thigh_R', 'Leg_R', 'Knee_R', 'Thigh_L', 'Leg_L', 'Knee_L',
          'Torso', 'Chest', 'Head', 'Shoulder_R', 'Arm_R', 'Hand_R', 'Tool_R', 'Elbow_R',
          'Shoulder_L', 'Arm_L', 'Hand_L', 'Tool_L', 'Elbow_L')


def file_coords(p):
    return [round(p[0], 6), round(-p[2], 6), round(p[1], 6)]


def skeleton(pivots=PIVOTS, joints=JOINTS):
    def node(name):
        parent, position = pivots[name]
        origin = pivots[parent][1] if parent else (0, 0, 0)
        x, y, z = [a-b for a,b in zip(position, origin)]
        # Only the root is converted by the reader. Bake the inverse basis into it.
        matrix = ([1,0,0,x, 0,0,-1,-z, 0,1,0,y, 0,0,0,1] if parent is None
                  else [1,0,0,x, 0,1,0,y, 0,0,1,z, 0,0,0,1])
        return {'name': name, 'transform': [round(v,6) for v in matrix],
                'children': [node(child) for child, (p, _) in pivots.items() if p == name]}
    return {'armature_format': 'MATRIX', 'joints': joints, 'hierarchy': [node('Root')]}


def mesh_builder(pivots, joints, texture_height=64):
    positions, normals, uvs, influences, counts, parts = [], [], [], [], [], {}
    # Six outward-facing cube faces and their skin-net rectangles.
    faces = [(0,3,2,1), (4,5,6,7), (0,4,7,3), (1,2,6,5), (3,7,6,2), (0,1,5,4)]
    dirs = [(0,0,-1),(0,0,1),(-1,0,0),(1,0,0),(0,1,0),(0,-1,0)]
    def box(part, joint, cx, low, high, width, depth, skin, dims, slice_y=(0.,1.), expand=0., cz=0., mirror_u=False):
        w, h, d = dims
        s, t = skin
        u0, u1 = s+d, s+d+w
        rects = [(u1+d,t+d,w,h), (u0,t+d,w,h), (s,t+d,d,h), (u1,t+d,d,h),
                 (u0,t,w,d), (u1,t,w,d)]
        if mirror_u:
            rects[2], rects[3] = rects[3], rects[2]
        x0, x1 = cx-width/2-expand, cx+width/2+expand
        y0, y1 = low-expand, high+expand
        z0, z1 = cz-depth/2-expand, cz+depth/2+expand
        points = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                  (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
        base = len(positions)//3
        for point in points:
            positions.extend(file_coords(point))
            influences.extend((joints.index(joint), 0))
            counts.append(1)
        indices = parts.setdefault(part, {'array': []})['array']
        for face_idx, (corners, direction, rect) in enumerate(zip(faces, dirs, rects)):
            normal_idx = len(normals)//3
            normals.extend(file_coords(direction))
            u,v,du,dv = rect
            lo,hi = slice_y if face_idx < 4 else (0.,1.)
            uvbase = len(uvs)//2
            # For vertical faces y chooses the image row, independent of face winding.
            for i, index in enumerate(corners):
                if face_idx < 4:
                    axis = 0 if face_idx < 2 else 2
                    min_axis = x0 if axis == 0 else z0
                    right = points[index][axis] != min_axis
                    flip = face_idx in (0,3)
                    column = int(right != flip)
                    row = lo if points[index][1] == y1 else hi
                else:
                    column, row = ((0,0),(0,1),(1,1),(1,0))[i]
                column = 1 - column if mirror_u else column
                uvs.extend((round((u+du*column)/64,7), round((v+dv*row)/texture_height,7)))
            for i in (0,1,2, 0,2,3):
                indices.extend((base+corners[i],uvbase+i,normal_idx))
    return box, {'mesh_loader':'skinned_mesh','armature':skeleton(pivots, joints),
            'vertices':{**{k:{'array':v} for k,v in [('positions',positions),('normals',normals),('uvs',uvs),
                       ('vindices',influences),('vcounts',counts),('weights',[1])]},'parts':parts}}

def player(slim, piglin=False, legacy_skin=False, drowned_overlay=False):
    pivots = dict(PIVOTS)
    if piglin:
        for side, sign in [('L', 1), ('R', -1)]:
            pivots['Ear_'+side] = ('Head', (sign*.225, 1.85, -.035))
    box, mesh = mesh_builder(pivots, (*JOINTS, 'Ear_L', 'Ear_R') if piglin else JOINTS,
                             texture_height=32 if legacy_skin else 64)
    if piglin:
        for side, sign in [('L', 1), ('R', -1)]:
            box('head', 'Ear_'+side, sign*.286, 1.68, 1.87, .14, .06, (39, 6), (4, 5, 1))
    for outer in ((True,) if drowned_overlay else (False, True)):
        gap = .033 if drowned_overlay else .011 if outer else 0
        overlay_uv = outer and not drowned_overlay
        box('hat' if outer else 'head','Head',0,1.53,1.99,.475,.455,
            (32,0) if outer else (0,0),(8,8,8),expand=gap)
        if legacy_skin and outer:
            continue
        for j,low,hi,yrange in [('Torso',.91,1.22,(.5,1)),('Chest',1.22,1.53,(0,.5))]:
            box('jacket' if outer else 'torso',j,0,low,hi,.485,.24,(16,32) if overlay_uv else (16,16),(8,12,4),yrange,gap)
        for side, sign in [('R',-1),('L',1)]:
            prefix='right' if side=='R' else 'left'
            mirror = legacy_skin and side == 'L'
            leg_skin = ((0,32) if overlay_uv else (0,16)) if side=='R' or mirror else ((0,48) if overlay_uv else (16,48))
            arm_skin = ((40,32) if overlay_uv else (40,16)) if side=='R' or mirror else ((48,48) if overlay_uv else (32,48))
            for j,lo,hi,yrange in [('Thigh',.47,.91,(0,.5)),('Leg',.045,.47,(.5,1))]:
                box(prefix+('Pants' if outer else 'Leg'),j+'_'+side,sign*.127,lo,hi,.228,.23,leg_skin,(4,12,4),yrange,gap,mirror_u=mirror)
            for j,lo,hi,yrange in [('Arm',1.12,1.49,(0,.5)),('Hand',.79,1.12,(.5,1))]:
                box(prefix+('Sleeve' if outer else 'Arm'),j+'_'+side,sign*.345,lo,hi,.166 if slim else .205,
                    .221,arm_skin,(3 if slim else 4,12,4),yrange,gap,mirror_u=mirror)
    return mesh


def robed_humanoid(kind):
    box, mesh = mesh_builder(PIVOTS, JOINTS)
    box('head', 'Head', 0, 1.5, 2.08, .46, .45, (0, 0), (8, 10, 8))
    box('head', 'Head', 0, 1.64, 1.86, .15, .18, (24, 0), (2, 4, 2), cz=-.29)
    if kind == 'witch':
        box('hat', 'Head', 0, 1.99, 2.09, .64, .61, (0, 32), (10, 2, 10))
        box('hat', 'Head', -.045, 2.06, 2.27, .37, .36, (2, 43), (6, 4, 6))
        box('hat', 'Head', -.105, 2.23, 2.48, .2, .19, (12, 47), (3, 4, 3))
    for joint, low, high, rows in (('Torso', .89, 1.19, (.53, 1)), ('Chest', 1.19, 1.54, (0, .53))):
        box('torso', joint, 0, low, high, .51, .28, (16, 20), (8, 12, 6), rows)
    if kind != 'zombie_villager':
        box('torso', 'Torso', 0, .69, 1.17, .55, .33, (0, 39), (8, 8, 6), (.45, 1))
    for side, sign, part in (('L', 1, 'left'), ('R', -1, 'right')):
        for joint, lo, hi, rows in (('Thigh', .46, .9, (0, .5)), ('Leg', .02, .46, (.5, 1))):
            box(part+'Leg', joint+'_'+side, sign*.13, lo, hi, .237, .24, (0, 22), (4, 12, 4), rows, mirror_u=sign > 0)
        for joint, lo, hi, rows in (('Arm', 1.12, 1.51, (0, .53)), ('Hand', .75, 1.12, (.53, 1))):
            box(part+'Arm', joint+'_'+side, sign*.347, lo, hi, .206, .225, (40, 19), (4, 12, 4), rows, mirror_u=sign > 0)
    return mesh


def enderman():
    # Rest pose and geometry authored here. Joint/part names are the Java rig ABI.
    pivots = {name: (parent, (x, y * 1.53, z)) for name, (parent, (x, y, z)) in PIVOTS.items()}
    pivots['Head_Top'] = ('Head', (0, 2.51, 0))
    joints = (*JOINTS, 'Head_Top')
    box, mesh = mesh_builder(pivots, joints, texture_height=32)
    box('headBottom', 'Head', 0, 2.33, 2.48, .47, .47, (0, 0), (8, 8, 8), (.7, 1))
    box('headTop', 'Head_Top', 0, 2.48, 2.82, .48, .48, (0, 0), (8, 8, 8), (0, .7))
    box('torso', 'Torso', 0, 1.39, 1.98, .47, .22, (32, 16), (8, 12, 4), (.5, 1))
    box('torso', 'Chest', 0, 1.98, 2.34, .47, .22, (32, 16), (8, 12, 4), (0, .5))
    for side, prefix, sign in [('R', 'right', -1), ('L', 'left', 1)]:
        for part, joint, x, low, high, rows in [
                ('Leg', 'Thigh', .127, .72, 1.39, (0, .5)),
                ('Leg', 'Leg', .127, .01, .72, (.5, 1)),
                ('Arm', 'Arm', .345, 1.71, 2.27, (0, .5)),
                ('Arm', 'Hand', .345, .95, 1.71, (.5, 1))]:
            box(prefix + part, joint + '_' + side, sign*x, low, high, .125, .125,
                (56, 0), (2, 30, 2), rows)
    return mesh

def frame(axis, degrees, pos=(0,0,0)):
    angle=radians(degrees)/2
    return {'loc':list(pos),'rot':[round(cos(angle),7)]+[round(-sin(angle)*v,7) for v in axis],'sca':[1,1,1]}


def track(name,times,values):
    return {'name':name,'time':times,'transform':values}


def attack(heading, lift, duration):
    times=[0,round(duration*.13,4),round(duration*.39,4),round(duration*.66,4),duration]
    def rotate(name,axis,angles):
        return track(name,times,[frame(axis,a) for a in angles])
    return {'format':'ATTRIBUTES','animation':[
        rotate('Root',(0,1,0),[0,-heading*.1,heading*.1,heading*.15,0]),
        rotate('Chest',(0,1,0),[0,-heading*.38,heading*.12,heading*.60,0]),
        rotate('Shoulder_R',(0,1,0),[0,-heading*.5,heading*.24,heading*.83,0]),
        rotate('Arm_R',(1,0,0),[0,-lift*.65,-lift,-lift*.42,0]),
        rotate('Hand_R',(0,0,1),[0,-15,5,28,0])]}


def dodge(sign):
    times=[0,.12,.27,.43,.62,.75]
    return {'format':'ATTRIBUTES','animation':[
        # MODEL_COORD subtracts the current coordinate from the previous one.
        track('Coord',times,[frame((1,0,0),0,(0,0,round(-sign*d,4))) for d in (0,.12,.6,1.15,1.48,1.55)]),
        track('Root',times,[frame((1,0,0),sign*a,(0,h,0)) for a,h in zip((0,45,130,215,310,360),(0,-.13,-.22,-.24,-.10,0))]),
        track('Thigh_R',times,[frame((1,0,0),a) for a in (0,-30,-62,-58,-18,0)]),
        track('Thigh_L',times,[frame((1,0,0),a) for a in (0,-22,-55,-63,-26,0)]),
        track('Arm_R',times,[frame((1,0,0),a) for a in (0,-30,-82,-78,-26,0)])]}


def gait(running):
    period = .54 if running else .92
    swing = 54 if running else 27
    lift = .065 if running else .022
    times = [round(i * period / 8, 5) for i in range(9)]
    phase = [i * pi / 4 for i in range(9)]
    tracks = [track('Root', times, [frame((1, 0, 0), 7 if running else 1,
                         (0, round(lift * sin(t) ** 2, 6), 0)) for t in phase])]
    for side, sign in [('R', 1), ('L', -1)]:
        tracks.extend([
            track('Thigh_' + side, times, [frame((1, 0, 0), sign * swing * cos(t)) for t in phase]),
            track('Leg_' + side, times, [frame((1, 0, 0), -max(0, sign * sin(t)) * swing) for t in phase]),
            track('Arm_' + side, times, [frame((1, 0, 0), -sign * swing * .75 * cos(t)) for t in phase]),
        ])
    return {'format': 'ATTRIBUTES', 'animation': tracks}


def step(dx, dz):
    times = [0, .065, .17, .28, .38, .47]
    distance = [0, .08, .51, .98, 1.13, 1.15]
    lean = [0, 10, 16, 9, 4, 0]
    tracks = [track('Coord', times, [frame((0, 1, 0), 0, (round(-dx*d, 5), 0, round(-dz*d, 5))) for d in distance]),
              track('Root', times, [frame((dz, 0, -dx), a, (0, -a * .004, 0)) for a in lean])]
    for side, sign in [('R', -1), ('L', 1)]:
        spread = (1.2 if dx * sign > 0 else -.65) if dx else sign
        tracks.append(track('Thigh_' + side, times, [frame((dz, 0, -dx), a * spread * 1.6) for a in lean]))
    return {'format': 'ATTRIBUTES', 'animation': tracks}


def sword_guard():
    times = [0, .45, .9]
    return {'format': 'ATTRIBUTES', 'animation': [
        track('Chest', times, [frame((0, 1, 0), a) for a in (-17, -20, -17)]),
        track('Shoulder_R', times, [frame((0, 0, 1), a) for a in (-34, -36, -34)]),
        track('Arm_R', times, [frame((1, 0, 0), a) for a in (-65, -67, -65)]),
        track('Hand_R', times, [frame((0, 1, 0), a) for a in (-22, -24, -22)]),
        track('Arm_L', times, [frame((1, 0, 0), a) for a in (-30, -32, -30)])]}


def png_rgba(width, height, pixel):
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            pixels.extend(pixel(x, y))

    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data)))
    return (bytes.fromhex('89504e470d0a1a0a') + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(pixels), 9)) + chunk(b'IEND', b''))


def trail_texture():
    def pixel(x, y):
        u, v = x / 63, y / 31
        ridge = max(0, 1 - abs(2 * v - 1))
        opacity = round(255 * ridge ** .75 * u ** .8)
        return round(156 + 99 * ridge), round(201 + 54 * ridge), 255, opacity
    return png_rgba(64, 32, pixel)


BOOKS = {
    'skillbook': ((72, 64, 107), ('01010', '10001', '10001', '01110', '00100')),
    'skillbook_dodge': ((33, 92, 120), ('00100', '01100', '11010', '00111', '00100')),
    'skillbook_passive': ((66, 106, 71), ('00100', '01110', '11111', '01010', '01010')),
    'skillbook_guard': ((128, 69, 50), ('11111', '10001', '10101', '01110', '00100')),
    'skillbook_mover': ((45, 105, 96), ('00100', '01110', '11111', '00100', '00100')),
    'skillbook_identity': ((104, 60, 114), ('00100', '01010', '10101', '01010', '00100')),
}


def book_texture(color, emblem):
    def pixel(x, y):
        y -= (x - 3) // 5
        if x < 3 or x > 20 or y < 3 or y > 18:
            return 0, 0, 0, 0
        if x in (3, 20) or y in (3, 18):
            return 33, 31, 42, 255
        if y in (15, 16, 17):
            return (189, 180, 146, 255) if y == 16 else (224, 211, 171, 255)
        if 9 <= x <= 13 and 7 <= y <= 11 and emblem[y - 7][x - 9] == '1':
            return 245, 209, 133, 255
        if x in (5, 17) or y == 5:
            return *(min(c + 31, 255) for c in color), 255
        return *color, 255
    return png_rgba(24, 24, pixel)


WEAPON_METALS = {
    'wooden': (159, 103, 57), 'stone': (130, 138, 151), 'iron': (177, 193, 207),
    'golden': (217, 168, 66), 'diamond': (52, 188, 176), 'netherite': (103, 83, 127),
}

# Contours use axes along and across the blade. Each silhouette is drawn independently.
WEAPON_CONTOURS = {
    'greatsword': (((11, -3.6), (27, -3.6), (34, 0), (27, 3.6), (11, 3.6), (10, 1.5), (10, -1.5)), 9, 5.0),
    'longsword': (((11, -2.3), (27, -1.8), (33, 0), (27, 1.8), (11, 2.3)), 9, 4.7),
    'dagger': (((8, -2.8), (16, -2.1), (22, 0), (16, 2.1), (8, 2.8)), 7, 3.4),
    'tachi': (((10, -1.8), (20, -1.8), (29, -.8), (34, 1.5), (30, 3.2), (21, 1.4), (10, 1.0)), 8, 3.0),
    'spear': (((20, -1.0), (26, -3.1), (34, 0), (26, 3.1), (20, 1.0)), 20, 2.4),
    'bokken': (((10, -1.5), (27, -1.7), (33, -.1), (32, 1.2), (26, 1.7), (10, 1.3)), 9, 2.7),
    'sheath': (((7, -1.6), (22, -1.9), (33, -.3), (34, 1.0), (29, 2.7), (22, 1.1), (7, 1.6)), 7, 2.8),
}


def covered(poly, x, y):
    inside = False
    ax, ay = poly[-1]
    for bx, by in poly:
        if (ay > y) != (by > y) and x < ax + (bx - ax) * (y - ay) / (by - ay):
            inside = not inside
        ax, ay = bx, by
    return inside


def shade(color, adjustment):
    return *(max(0, min(255, value + adjustment)) for value in color), 255


def weapon_texture(family, material):
    blade, guard, guard_width = WEAPON_CONTOURS[family]
    metal = WEAPON_METALS[material] if isinstance(material, str) else material

    def material_at(s, t):
        if covered(blade, s, t):
            return shade(metal, (34 if t > .55 else -21 if t < -.6 else 8) + int(s) % 3)
        if abs(s - guard) < 1.15 and abs(t) < guard_width:
            return (208, 155, 79, 255) if s > guard else (158, 106, 59, 255)
        if 0 <= s <= guard and abs(t) < (1.15 if family == 'spear' else 1.42):
            if s < 2.4 or (family == 'spear' and abs(s - 13) < 1.0):
                return 191, 139, 69, 255
            return (114, 77, 57, 255) if int(s) % 3 else (77, 59, 54, 255)
        return None

    def pixel(x, y):
        s, t = (x - y + 22) * .70710678, (x + y - 32) * .70710678
        color = material_at(s, t)
        if color:
            return color
        if any(material_at(s + ds, t + dt) for ds, dt in ((.78, 0), (-.78, 0), (0, .78), (0, -.78))):
            return 37, 33, 43, 255
        return 0, 0, 0, 0
    return png_rgba(32, 32, pixel)


def glove_texture():
    palm = ((7, 19), (8, 10), (11, 8), (12, 12), (12, 6), (15, 5), (17, 7),
            (19, 5), (22, 6), (24, 8), (25, 15), (23, 24), (20, 27), (10, 27))

    def pixel(x, y):
        if covered(palm, x + .5, y + .5):
            if y > 22:
                return (179, 130, 72, 255) if y in (23, 26) else (66, 48, 47, 255)
            if 13 <= x <= 22 and 9 <= y <= 14 and (x + y) % 5 < 2:
                return 197, 159, 103, 255
            return shade((117, 68, 54), 13 if x > 18 else -3)
        return 0, 0, 0, 0
    return png_rgba(32, 32, pixel)


def stray_fabric(x, y):
    base = (62, 88, 99) if (x // 3 + y // 3) % 4 else (75, 106, 110)
    if (x + 3 * y) % 37 in (0, 1):
        return 174, 151, 101, 255
    return shade(base, (x + y) % 5)


def stray_icon(item):
    outlines = {
        'stray_hat': ((4, 11), (5, 6), (9, 3), (15, 3), (19, 6), (20, 17), (16, 20), (15, 15), (8, 15), (7, 20), (4, 17)),
        'stray_robe': ((3, 6), (8, 3), (10, 5), (14, 5), (16, 3), (21, 6), (23, 13), (19, 15), (17, 13), (17, 22), (7, 22), (7, 13), (5, 15), (1, 13)),
        'stray_pants': ((5, 4), (19, 4), (20, 21), (13, 21), (12, 12), (11, 12), (10, 21), (4, 21)),
    }
    return png_rgba(24, 24, lambda x, y: stray_fabric(x, y) if covered(outlines[item], x + .5, y + .5) else (0, 0, 0, 0))


def effect_mesh(rings, segments):
    positions, normals, uvs, indices = [], [], [], []
    for ring, (z, radius) in enumerate(rings):
        for spoke in range(segments + 1):
            angle = spoke * 2 * pi / segments
            positions.extend(file_coords((radius * cos(angle), radius * sin(angle), z)))
            normals.extend(file_coords((cos(angle), sin(angle), 0)))
            uvs.extend((round(spoke / segments, 6), round(ring / (len(rings) - 1), 6)))
    for ring in range(len(rings) - 1):
        for spoke in range(segments):
            start = ring * (segments + 1) + spoke
            end = start + segments + 1
            for index in (start, start + 1, end, start + 1, end + 1, end):
                indices.extend((index, index, index))
    return {'vertices': {key: {'array': values} for key, values in
                         [('positions', positions), ('normals', normals), ('uvs', uvs), ('indices', indices)]}}


def ripple_texture():
    def pixel(x, y):
        wave = sin(pi * y / 31) ** 1.7
        spark = .53 + .47 * cos((x / 64 * 9 + y / 31) * 2 * pi) ** 2
        return 177, 230, 246, round(208 * wave * spark)
    return png_rgba(64, 32, pixel)


def glint_texture():
    def pixel(x, y):
        lane = (x + 2 * y) % 16
        light = round(224 * max(0, 1 - abs(lane - 7) / 4) ** 1.4)
        return light, light, light, 255
    return png_rgba(32, 32, pixel)


def meter_pixel(x, y, width, height, color):
    if x in (0, width - 1) and y in (0, height - 1):
        return 0, 0, 0, 0
    if y in (0, height - 1) or x in (0, width - 1):
        return 26, 32, 42, 255
    shade = 1.0 if y == 1 else .86
    return tuple(round(channel * shade) for channel in color) + (255,)


def healthbars(fills):
    def pixel(x, y):
        if y >= 59:
            return meter_pixel(x, y - 59, 64, 5, (227, 173, 65))
        row, v = divmod(y, 10)
        return meter_pixel(x, v % 5, 64, 5, fills[row] if v >= 5 else (48, 58, 71))
    return png_rgba(64, 64, pixel)


def battle_icons():
    bars = ((1, 0, 62, 5, (46, 54, 66)), (1, 5, 62, 5, (111, 173, 238)),
            (2, 38, 237, 9, (34, 49, 57)), (2, 47, 237, 9, (81, 219, 168)),
            (1, 57, 238, 13, (242, 167, 83)), (1, 71, 238, 13, (49, 58, 72)))

    def pixel(x, y):
        for u, v, width, height, color in bars:
            if u <= x < u + width and v <= y < v + height:
                return meter_pixel(x - u, y - v, width, height, color)
        for cx, cy, color in ((112, 17, (245, 242, 217)), (149, 18, (255, 188, 98))):
            distance = abs(x - cx) + abs(y - cy)
            if 7 <= distance <= 11:
                return (*color, 255) if 8 <= distance <= 10 else (27, 33, 43, 255)
        return 0, 0, 0, 0
    return png_rgba(256, 256, pixel)


def particle_descriptions():
    smoke = [f'minecraft:generic_{i}' for i in reversed(range(8))]
    arc = [f'minecraft:sweep_{i}' for i in range(8)]
    return {
        'enderman_death_emit': smoke,
        'hit_blunt': ['minecraft:flash', 'minecraft:critical_hit'],
        'cut': arc,
        'dust_normal': smoke,
        'dust_expansive': smoke,
        'dust_contractive': smoke,
        'blood': ['minecraft:drip_hang', 'minecraft:drip_fall'],
        'blade_rush': arc,
        'breath_flame': ['minecraft:soul_fire_flame', 'minecraft:flame'],
        'tsunami_splash': [f'minecraft:splash_{i}' for i in range(4)],
        'feather': ['epicfight:replacement_feather'],
        'ash_directional': smoke[:4],
        'catharsis': [f'minecraft:spell_{i}' for i in range(6)],
    }


def feather_mask():
    def pixel(x, y):
        stem = 11 - .56 * y
        span = 3.6 * sin(pi * y / 17) if 0 < y < 17 else 0
        edge = span - abs(x - stem)
        alpha = round(232 * min(1, max(0, edge)))
        shade = 248 if abs(x - stem) < .7 else 217 + (y % 3) * 9
        return shade, shade, 238, alpha
    return png_rgba(16, 16, pixel)


def build(resources):
    inventory={}
    def write(name,data):
        path=resources/name
        if path.exists():
            raise ValueError(f'Replacement asset collides with another source: {name}')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        inventory[name]=sha256(data).hexdigest()
    def asset(name,doc):
        write(f'{BASE}/{name}.json',(json.dumps(doc,separators=(',',':'),allow_nan=False)+'\n').encode())
    for model,slim in [('biped',False),('biped_slim_arm',True)]:
        asset('entity/'+model,player(slim))
    asset('entity/biped_old_texture', player(False, legacy_skin=True))
    asset('entity/biped_outlayer', player(False, drowned_overlay=True))
    for model in ('zombie_villager', 'illager', 'witch'):
        asset('entity/'+model, robed_humanoid(model))
    asset('entity/enderman', enderman())
    for name, clip in enderman_motions.clips(frame, track).items():
        asset('animations/enderman/' + name, clip)
    asset('entity/skeleton', player(True))
    asset('entity/piglin', player(False, piglin=True))
    for name in ('creeper', 'hoglin', 'ravager'):
        asset('entity/'+name, entity_models.quadruped(name).mesh(mesh_builder))
    for name, rig in [('dragon', entity_models.dragon()), ('wither', entity_models.wither()),
                      ('iron_golem', entity_models.golem()), ('spider', entity_models.spider()),
                      ('vex', entity_models.vex(PIVOTS))]:
        asset('entity/'+name, rig.mesh(mesh_builder))
    for family, clips in {**mob_motions.clips(frame, track), **boss_motions.clips(frame, track)}.items():
        for name, clip in clips.items():
            asset(f'animations/{family}/{name}', clip)
    for i,(heading,lift,duration) in enumerate(((78,58,.51),(-91,72,.55),(58,118,.79)),1):
        asset(f'animations/biped/combat/sword_auto{i}',attack(heading,lift,duration))
    for direction,sign in [('forward',1),('backward',-1)]:
        asset('animations/biped/skill/roll_'+direction,dodge(sign))
    asset('animations/biped/living/idle',{'format':'ATTRIBUTES','animation':[
        track('Chest',[0,1.1,2.2],[frame((1,0,0),a) for a in (0,2.3,0)])]})
    times = [0, .32, .64]
    fall_tracks = [track('Chest', times, [frame((1, 0, 0), a) for a in (-7, -10, -7)])]
    for side, sign in [('L', 1), ('R', -1)]:
        fall_tracks.extend([
            track('Arm_'+side, times, [frame((0, 0, 1), sign*a) for a in (48, 55, 48)]),
            track('Thigh_'+side, times, [frame((1, 0, 0), sign*a) for a in (15, 18, 15)]),
            track('Leg_'+side, times, [frame((1, 0, 0), a) for a in (-17, -22, -17)])])
    asset('animations/biped/living/fall', {'format':'ATTRIBUTES', 'animation':fall_tracks})
    equip_times = [0, .12, .25, .4]
    def equip_track(joint, axis, degrees):
        return track(joint, equip_times, [frame(axis, angle) for angle in degrees])
    asset('animations/biped/living/equip_item', {'format':'ATTRIBUTES', 'animation':[
        equip_track('Shoulder_R', (0, 1, 0), [0, -14, -7, 0]),
        equip_track('Arm_R', (1, 0, 0), [12, 24, -47, -8]),
        equip_track('Hand_R', (0, 0, 1), [0, -16, 12, 0])]})
    # MirroredAnimation and ReversedAnimation derive the other three clips from this one.
    for name in ('equip_item', 'unequip_item', 'equip_item_offhand', 'unequip_item_offhand'):
        asset('animations/biped/living/data/'+name, {
            'layer': 'COMPOSITE_LAYER', 'priority': 'HIGHEST' if name.endswith('_offhand') else 'HIGH'})
    for name, running in [('walk', False), ('run', True)]:
        asset('animations/biped/living/' + name, gait(running))
    for name, dx, dz in [('left', 1, 0), ('right', -1, 0), ('forward', 0, 1), ('backward', 0, -1)]:
        asset('animations/biped/skill/step_' + name, step(dx, dz))
    asset('animations/biped/skill/guard_sword', sword_guard())
    write('assets/epicfight/textures/gui/healthbars1.png', healthbars((
        (224, 84, 85), (231, 140, 86), (154, 202, 113), (101, 177, 230), (202, 135, 229), (122, 214, 184))))
    write('assets/epicfight/textures/gui/healthbars2.png', healthbars(((220, 102, 91),) * 6))
    write('assets/epicfight/textures/gui/battle_icons.png', battle_icons())
    write('assets/epicfight/textures/particle/swing_trail.png', trail_texture())
    for icon, (color, emblem) in BOOKS.items():
        for name, document in [('items/' + icon, {'model': {'type': 'minecraft:model', 'model': 'epicfight:item/' + icon}}),
                               ('models/item/' + icon, {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'epicfight:item/' + icon}})]:
            write(f'assets/epicfight/{name}.json', (json.dumps(document, separators=(',', ':')) + '\n').encode())
        write(f'assets/epicfight/textures/item/{icon}.png', book_texture(color, emblem))
    def item(name, texture, handheld=False):
        model_type = 'handheld' if handheld else 'generated'
        model = {'parent': 'minecraft:item/' + model_type, 'textures': {'layer0': 'epicfight:item/' + name}}
        declaration = {'model': {'type': 'minecraft:model', 'model': 'epicfight:item/' + name}}
        write(f'assets/epicfight/items/{name}.json', (json.dumps(declaration, separators=(',', ':')) + '\n').encode())
        write(f'assets/epicfight/models/item/{name}.json', (json.dumps(model, separators=(',', ':')) + '\n').encode())
        write(f'assets/epicfight/textures/item/{name}.png', texture)
    for family in ('greatsword', 'longsword', 'dagger', 'tachi', 'spear'):
        for metal in WEAPON_METALS:
            item(f'{metal}_{family}', weapon_texture(family, metal), True)
    item('uchigatana', weapon_texture('tachi', (101, 168, 194)), True)
    item('uchigatana_sheath', weapon_texture('sheath', (77, 52, 93)), True)
    item('bokken', weapon_texture('bokken', 'wooden'), True)
    item('glove', glove_texture(), True)
    for name in ('stray_hat', 'stray_robe', 'stray_pants'):
        item(name, stray_icon(name))
    for layer in ('humanoid', 'humanoid_leggings'):
        write(f'assets/epicfight/textures/entity/equipment/{layer}/stray_cloth.png', png_rgba(64, 32, stray_fabric))
    for name, rings, sides in [
            ('air_burst', [(0, .62), (.07, .91), (.23, 1.34)], 24),
            ('force_field', [(-.79, .18), (-.61, .66), (-.27, .95), (.22, .97), (.69, .66), (.85, .14)], 32),
            ('laser', [(0, .04), (.055, .14), (.91, .14), (1, .015)], 8)]:
        asset('particle/' + name, effect_mesh(rings, sides))
    write('assets/epicfight/textures/particle/air_burst.png', ripple_texture())
    write('assets/fala_epicfight/textures/utility/effect-white.png', png_rgba(1, 1, lambda x, y: (255, 255, 255, 255)))
    write('assets/fala_epicfight/textures/utility/angle-glint.png', glint_texture())
    write('assets/fala_epicfight/shaders/compute/skin.comp',(HERE/'skin.comp').read_bytes())
    write('assets/epicfight/sounds.json', (json.dumps(sound_events.definitions(), indent=2) + '\n').encode())
    write('assets/epicfight/sounds/compat/silence.ogg', (HERE/'silence.ogg').read_bytes())
    for particle, textures in particle_descriptions().items():
        write(f'assets/epicfight/particles/{particle}.json', (json.dumps({'textures': textures}) + '\n').encode())
    write('assets/epicfight/textures/particle/replacement_feather.png', feather_mask())
    notice=resources/'META-INF/fala-replacement-assets'
    notice.mkdir(parents=True,exist_ok=True)
    (notice/'CC0-1.0.txt').write_bytes((HERE/'CC0-1.0.txt').read_bytes())
    (notice/'manifest.json').write_text(json.dumps({'license':'CC0-1.0','origin':'Fala SiayaCraft independent procedural assets',
        'sha256':inventory},sort_keys=True,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    build(Path(sys.argv[1]))
