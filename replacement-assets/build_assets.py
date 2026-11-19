#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Build original player geometry and keyframes from dimensions, pivots and motion curves."""
from hashlib import sha256
import json
from math import cos, radians, sin
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
    return {'armature_format': 'MATRIX', 'joints': list(PIVOTS), 'hierarchy': [node('Root')]}


def player(slim):
    positions, normals, uvs, influences, counts, parts = [], [], [], [], [], {}
    # Six outward-facing cube faces and their skin-net rectangles.
    faces = [(0,3,2,1), (4,5,6,7), (0,4,7,3), (1,2,6,5), (3,7,6,2), (0,1,5,4)]
    dirs = [(0,0,-1),(0,0,1),(-1,0,0),(1,0,0),(0,1,0),(0,-1,0)]
    names = list(PIVOTS)
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
            influences.extend((names.index(joint), 0))
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
    write('assets/fala_epicfight/shaders/compute/skin.comp',(HERE/'skin.comp').read_bytes())
    notice=resources/'META-INF/fala-replacement-assets'
    notice.mkdir(parents=True,exist_ok=True)
    (notice/'CC0-1.0.txt').write_bytes((HERE/'CC0-1.0.txt').read_bytes())
    (notice/'manifest.json').write_text(json.dumps({'license':'CC0-1.0','origin':'Fala SiayaCraft independent procedural assets',
        'sha256':inventory},sort_keys=True,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    build(Path(sys.argv[1]))
