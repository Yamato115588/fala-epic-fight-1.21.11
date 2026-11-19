#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Build original player geometry and keyframes from dimensions, pivots and motion curves."""
from hashlib import sha256
import json
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


def skeleton():
    def node(name):
        parent, position = PIVOTS[name]
        origin = PIVOTS[parent][1] if parent else (0, 0, 0)
        x, y, z = [a-b for a,b in zip(position, origin)]
        # Only the root is converted by the reader. Bake the inverse basis into it.
        matrix = ([1,0,0,x, 0,0,-1,-z, 0,1,0,y, 0,0,0,1] if parent is None
                  else [1,0,0,x, 0,1,0,y, 0,0,1,z, 0,0,0,1])
        return {'name': name, 'transform': [round(v,6) for v in matrix],
                'children': [node(child) for child, (p, _) in PIVOTS.items() if p == name]}
    return {'armature_format': 'MATRIX', 'joints': JOINTS, 'hierarchy': [node('Root')]}


def player(slim):
    positions, normals, uvs, influences, counts, parts = [], [], [], [], [], {}
    # Six outward-facing cube faces and their skin-net rectangles.
    faces = [(0,3,2,1), (4,5,6,7), (0,4,7,3), (1,2,6,5), (3,7,6,2), (0,1,5,4)]
    dirs = [(0,0,-1),(0,0,1),(-1,0,0),(1,0,0),(0,1,0),(0,-1,0)]
    def box(part, joint, cx, low, high, width, depth, skin, dims, slice_y=(0.,1.), expand=0.):
        w, h, d = dims
        s, t = skin
        u0, u1 = s+d, s+d+w
        rects = [(u1+d,t+d,w,h), (u0,t+d,w,h), (s,t+d,d,h), (u1,t+d,d,h),
                 (u0,t,w,d), (u1,t,w,d)]
        x0, x1 = cx-width/2-expand, cx+width/2+expand
        y0, y1 = low-expand, high+expand
        z0, z1 = -depth/2-expand, depth/2+expand
        points = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                  (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
        base = len(positions)//3
        for point in points:
            positions.extend(file_coords(point))
            influences.extend((JOINTS.index(joint), 0))
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
                uvs.extend((round((u+du*column)/64,7), round((v+dv*row)/64,7)))
            for i in (0,1,2, 0,2,3):
                indices.extend((base+corners[i],uvbase+i,normal_idx))
    for outer in (False,True):
        gap=.011 if outer else 0
        box('hat' if outer else 'head','Head',0,1.53,1.99,.475,.455,
            (32,0) if outer else (0,0),(8,8,8),expand=gap)
        for j,low,hi,yrange in [('Torso',.91,1.22,(.5,1)),('Chest',1.22,1.53,(0,.5))]:
            box('jacket' if outer else 'torso',j,0,low,hi,.485,.24,(16,32) if outer else (16,16),(8,12,4),yrange,gap)
        for side, sign in [('R',-1),('L',1)]:
            prefix='right' if side=='R' else 'left'
            leg_skin = ((0,32) if outer else (0,16)) if side=='R' else ((0,48) if outer else (16,48))
            arm_skin = ((40,32) if outer else (40,16)) if side=='R' else ((48,48) if outer else (32,48))
            for j,lo,hi,yrange in [('Thigh',.47,.91,(0,.5)),('Leg',.045,.47,(.5,1))]:
                box(prefix+('Pants' if outer else 'Leg'),j+'_'+side,sign*.127,lo,hi,.228,.23,leg_skin,(4,12,4),yrange,gap)
            for j,lo,hi,yrange in [('Arm',1.12,1.49,(0,.5)),('Hand',.79,1.12,(.5,1))]:
                box(prefix+('Sleeve' if outer else 'Arm'),j+'_'+side,sign*.345,lo,hi,.166 if slim else .205,
                    .221,arm_skin,(3 if slim else 4,12,4),yrange,gap)
    return {'mesh_loader':'skinned_mesh','armature':skeleton(),
            'vertices':{**{k:{'array':v} for k,v in [('positions',positions),('normals',normals),('uvs',uvs),
                       ('vindices',influences),('vcounts',counts),('weights',[1])]},'parts':parts}}


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
        track('Coord',times,[frame((1,0,0),0,(0,0,round(sign*d,4))) for d in (0,.12,.6,1.15,1.48,1.55)]),
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
    tracks = [track('Coord', times, [frame((0, 1, 0), 0, (round(dx*d, 5), 0, round(dz*d, 5))) for d in distance]),
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
    for i,(heading,lift,duration) in enumerate(((78,58,.51),(-91,72,.55),(58,118,.79)),1):
        asset(f'animations/biped/combat/sword_auto{i}',attack(heading,lift,duration))
    for direction,sign in [('forward',1),('backward',-1)]:
        asset('animations/biped/skill/roll_'+direction,dodge(sign))
    asset('animations/biped/living/idle',{'format':'ATTRIBUTES','animation':[
        track('Chest',[0,1.1,2.2],[frame((1,0,0),a) for a in (0,2.3,0)])]})
    for name, running in [('walk', False), ('run', True)]:
        asset('animations/biped/living/' + name, gait(running))
    for name, dx, dz in [('left', 1, 0), ('right', -1, 0), ('forward', 0, 1), ('backward', 0, -1)]:
        asset('animations/biped/skill/step_' + name, step(dx, dz))
    asset('animations/biped/skill/guard_sword', sword_guard())
    write('assets/epicfight/textures/particle/swing_trail.png', trail_texture())
    for icon, (color, emblem) in BOOKS.items():
        for name, document in [('items/' + icon, {'model': {'type': 'minecraft:model', 'model': 'epicfight:item/' + icon}}),
                               ('models/item/' + icon, {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'epicfight:item/' + icon}})]:
            write(f'assets/epicfight/{name}.json', (json.dumps(document, separators=(',', ':')) + '\n').encode())
        write(f'assets/epicfight/textures/item/{icon}.png', book_texture(color, emblem))
    for name, rings, sides in [
            ('air_burst', [(0, .62), (.07, .91), (.23, 1.34)], 24),
            ('force_field', [(-.79, .18), (-.61, .66), (-.27, .95), (.22, .97), (.69, .66), (.85, .14)], 32),
            ('laser', [(0, .04), (.055, .14), (.91, .14), (1, .015)], 8)]:
        asset('particle/' + name, effect_mesh(rings, sides))
    write('assets/epicfight/textures/particle/air_burst.png', ripple_texture())
    write('assets/fala_epicfight/textures/utility/effect-white.png', png_rgba(1, 1, lambda x, y: (255, 255, 255, 255)))
    write('assets/fala_epicfight/textures/utility/angle-glint.png', glint_texture())
    write('assets/fala_epicfight/shaders/compute/skin.comp',(HERE/'skin.comp').read_bytes())
    notice=resources/'META-INF/fala-replacement-assets'
    notice.mkdir(parents=True,exist_ok=True)
    (notice/'CC0-1.0.txt').write_bytes((HERE/'CC0-1.0.txt').read_bytes())
    (notice/'manifest.json').write_text(json.dumps({'license':'CC0-1.0','origin':'Fala SiayaCraft independent procedural assets',
        'sha256':inventory},sort_keys=True,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    build(Path(sys.argv[1]))
