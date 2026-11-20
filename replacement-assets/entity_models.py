# SPDX-License-Identifier: CC0-1.0
"""Independently dimensioned rest poses and weighted cuboids for Epic Fight mob rigs."""


class Body:
    def __init__(self, root_height):
        self.pivots = {'Root': (None, (0, root_height, 0))}
        self.boxes = []

    def joint(self, name, parent, x, y, z):
        self.pivots[name] = parent, (x, y, z)

    def segment(self, part, joint, width, height, depth, offset=(0, 0, 0)):
        x, y, z = self.pivots[joint][1]
        dx, dy, dz = offset
        self.boxes.append((part, joint, x + dx, y + dy - height/2, y + dy + height/2,
                           width, depth, z + dz))

    def mesh(self, mesh_builder):
        box, result = mesh_builder(self.pivots, tuple(self.pivots))
        for part, joint, x, low, high, width, depth, z in self.boxes:
            box(part, joint, x, low, high, width, depth, (0, 0), (8, 8, 8), cz=z)
        return result


def quadruped(kind):
    creeper = kind == 'creeper'
    ravager = kind == 'ravager'
    width, height, depth = {'creeper': (.48, .79, .35), 'hoglin': (.85, .69, 1.26),
                            'ravager': (1.47, 1.02, 1.88)}[kind]
    hip = {'creeper': .41, 'hoglin': .61, 'ravager': 1.04}[kind]
    b = Body(hip)
    b.joint('Torso', 'Root', 0, hip + height/2, 0)
    b.segment('torso' if creeper else 'body', 'Torso', width, height, depth)
    neck = 'Torso'
    if ravager:
        neck = 'Head_Root'
        b.joint(neck, 'Torso', 0, hip + .86, depth/2)
    b.joint('Head', neck, 0, hip + height + (.24 if creeper else -.15), 0 if creeper else depth*.66)
    b.segment('head', 'Head', width*.95, width*.95, width*.94)
    if ravager:
        for side, sign in [('L', 1), ('R', -1)]:
            joint = 'Ear_' + side
            b.joint(joint, 'Head', sign*.58, hip + 1.1, depth*.63)
            b.segment('head', joint, .23, .46, .21)
        b.joint('Chin', 'Head', 0, hip+.41, depth*.72)
        b.segment('head', 'Chin', .81, .25, .85)
    for side, sign in [('L', 1), ('R', -1)]:
        for end, forward in [('F', 1), ('B', -1)]:
            suffix = side + end
            part = ('leg'+suffix if creeper else
                    ('left' if sign == 1 else 'right') + ('FrontLeg' if forward == 1 else 'BackLeg'))
            x, z = sign*width*.36, forward*depth*.39
            leg = 'Leg_' + suffix
            if kind == 'hoglin':
                thigh = 'Thigh_'+suffix
                b.joint(thigh, 'Torso', x, hip, z)
                b.joint(leg, thigh, x, hip*.54, z)
                b.joint('Knee_'+suffix, leg, x, hip*.53, z+.03)
                b.segment(part, thigh, width*.3, hip*.46, width*.31, (0,-hip*.23,0))
                b.segment(part, leg, width*.25, hip*.54, width*.26, (0,-hip*.27,0))
            else:
                b.joint(leg, 'Torso', x, hip, z)
                b.segment(part, leg, width*.36, hip, width*.39, (0,-hip/2,0))
                if ravager:
                    foot = 'Foot_'+suffix
                    b.joint(foot, leg, x, .15, z)
                    b.joint(leg+'_F', foot, x, .09, z+.11)
                    b.segment(part, foot, .43, .24, .45)
    return b


def spider():
    b = Body(.43)
    b.joint('Stomach', 'Root', 0, .47, -.3)
    b.joint('Head', 'Root', 0, .44, .43)
    b.segment('middleStomach', 'Root', .33, .3, .39)
    b.segment('bottomStomach', 'Stomach', .61, .47, .63)
    b.segment('head', 'Head', .44, .39, .43)
    for side, sign, part in [('L', 1, 'leftLeg'), ('R', -1, 'rightLeg')]:
        for i in range(1, 5):
            joint = side+'L'+str(i)
            b.joint(joint, 'Root', sign*.15, .39, (i-2.5)*.15)
            b.segment(part+str(i), joint, .58, .09, .09, (sign*.28, 0, (i-2.5)*.045))
            b.segment(part+str(i), joint, .095, .37, .11, (sign*.53, -.16, (i-2.5)*.045))
    return b


def golem():
    b = Body(1.18)
    b.joint('Chest', 'Root', 0, 1.94, 0)
    b.joint('Head', 'Chest', 0, 2.47, .05)
    b.segment('core', 'Root', .77, .47, .54, (0,.18,0))
    b.segment('chest', 'Chest', 1.03, .83, .56)
    b.segment('head', 'Head', .47, .55, .47)
    for side, sign, part in [('L', 1, 'left'), ('R', -1, 'right')]:
        for limb, ys, width, length, label, parent in [
                ('A', [2.17, 1.74, 1.31, .88], .36, .43, 'Arm', 'Chest'),
                ('R', [1.22, .61], .33, .61, 'Leg', 'Root')]:
            for i,y in enumerate(ys, 1):
                name = side+limb+str(i)
                b.joint(name, parent, sign*(.67 if limb == 'A' else .22), y, 0)
                b.segment(part+label, name, width, length, width, (0,-length/2,0))
                parent = name
    return b


def wither():
    b = Body(1.64)
    b.joint('Torso', 'Root', 0, 1.81, 0)
    b.segment('ribcage', 'Torso', .49, .92, .36)
    b.segment('ribcage', 'Torso', 1.45, .19, .24, (0,.31,0))
    for suffix, part, x in [('M', 'centerHead', 0), ('L', 'leftHead', .7), ('R', 'rightHead', -.7)]:
        b.joint('Head_'+suffix, 'Torso', x, 2.64 if x == 0 else 2.21, .06)
        b.segment(part, 'Head_'+suffix, .48, .5, .49)
    b.joint('Tail', 'Torso', 0, 1.39, -.13)
    b.segment('tail', 'Tail', .22, 1.16, .24, (0,-.55,0))
    return b


def dragon():
    b = Body(2.8)
    b.joint('Torso', 'Root', 0, 2.91, 0)
    b.segment('torso', 'Torso', 2.52, 1.96, 4.43)
    for prefix, count, direction, part in [('Neck', 5, 1, 'neck'), ('Tail', 12, -1, 'tail')]:
        parent = 'Torso'
        for i in range(1, count+1):
            name = prefix + str(i)
            b.joint(name, parent, 0, 3.12+i*.043, direction*(1.85+i*.61))
            breadth = .89 - i*(.043 if direction < 0 else .024)
            b.segment(part, name, breadth, breadth*.86, .76)
            parent = name
    b.joint('Head', 'Neck5', 0, 3.38, 5.51)
    b.segment('head', 'Head', 1.09, .97, 1.21)
    for suffix, y in [('Upper', 3.44), ('Lower', 3.03)]:
        name = 'Mouth_'+suffix
        b.joint(name, 'Head', 0, y, 5.82)
        b.segment('head', name, .83, .28, 1.16, (0,0,.43))
    for side, sign, part in [('L',1,'left'), ('R',-1,'right')]:
        for end, z in [('Front', 1.28), ('Back', -1.38)]:
            parent = 'Torso'
            for i,(y, bend, length) in enumerate([(2.57,0,1.13),(1.49,-.33,.89),(.64,.07,.64)], 1):
                name = 'Leg_'+end+'_'+side+str(i)
                b.joint(name, parent, sign*.91, y, z+bend)
                b.segment(part+'Leg'+end, name, .52, length, .68, (0,-length/2,0))
                parent = name
        parent = 'Torso'
        for i, x in enumerate([.98, 4.37], 1):
            joint = 'Wing_'+side+str(i)
            b.joint(joint, parent, sign*x, 3.58-(i-1)*.19, .35)
            b.segment(part+'Wing', joint, 3.42, .12, 2.25/i, (sign*1.68,0,-.43))
            parent = joint
    return b


def vex(pivots):
    b = Body(.5)
    for name, (parent, (x, y, z)) in pivots.items():
        if not name.startswith(('Thigh','Leg','Knee')):
            b.joint(name, parent, x*.52, y*.52, z*.52)
    b.segment('torso','Chest',.29,.32,.18)
    b.segment('head','Head',.29,.28,.28,(0,.11,0))
    b.joint('Tail','Root',0,.45,-.06)
    b.segment('tail','Tail',.16,.36,.14,(0,-.16,0))
    for side, sign, part in [('L',1,'left'),('R',-1,'right')]:
        b.joint('Wing_'+side,'Chest',sign*.09,.71,-.07)
        b.segment(part+'Wing','Wing_'+side,.34,.25,.028,(sign*.16,.05,-.05))
        for joint in ['Arm','Hand']:
            b.segment(part+'Arm',joint+'_'+side,.087,.17,.09,(0,-.08,0))
    return b
