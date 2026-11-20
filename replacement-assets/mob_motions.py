# SPDX-License-Identifier: CC0-1.0
"""Keyframes designed for the port's replacement rigs and combat windows."""
from math import cos, pi, sin

PITCH, YAW, ROLL = (1, 0, 0), (0, 1, 0), (0, 0, 1)


def timeline(frame, track):
    def clip(times, *rotations, positions=None):
        positions = positions or {}
        channels = dict((joint, (axis, angles)) for joint, axis, angles in rotations)
        for joint in positions:
            channels.setdefault(joint, (PITCH, [0] * len(times)))
        return {'format': 'ATTRIBUTES', 'animation': [
            track(joint, times, [frame(axis, angle, position) for angle, position in zip(
                angles, positions.get(joint, [(0, 0, 0)] * len(times)), strict=True)])
            for joint, (axis, angles) in channels.items()]}
    return clip


def vertical(heights):
    return {'Root': [(0, y, 0) for y in heights]}


def advance(distances, heights=None):
    # The engine computes horizontal displacement as previous minus current.
    return [(0, y, -z) for z, y in zip(distances, heights or [0] * len(distances), strict=True)]


def cycle(period):
    return ([round(i * period / 8, 6) for i in range(9)], [i * pi / 4 for i in range(9)])


def recovery(clip, center, head, duration, tilt):
    return clip([0, .12, duration * .64, duration],
                (center, PITCH, (0, -tilt, tilt / 4, 0)),
                (head, YAW, (0, tilt / 2, -tilt / 5, 0)),
                positions=vertical((0, -.035, -.025, 0)))


def collapse(clip, fall, head, duration=1.2):
    return clip([0, .16, duration * .56, duration],
                ('Root', ROLL, (0, -12, -75, -91)), (head, PITCH, (0, -13, 12, 16)),
                positions=vertical((0, -fall * .08, -fall * .82, -fall)))


def humanoid_motions(clip):
    def idle(bias, turn, period):
        return clip([0, period / 2, period], ('Chest', PITCH, (0, 3, 0)),
                    ('Head', YAW, (-turn, turn, -turn)),
                    ('Arm_R', PITCH, (bias, bias - 5, bias)),
                    ('Arm_L', PITCH, (bias - 7, bias - 4, bias - 7)))

    def walk(period, stride, arms):
        times, phases = cycle(period)
        tracks = [('Chest', YAW, [5 * sin(t) for t in phases])]
        for side, sign in (('R', 1), ('L', -1)):
            tracks.extend([
                ('Thigh_' + side, PITCH, [sign * stride * cos(t) for t in phases]),
                ('Leg_' + side, PITCH, [-stride * .72 * max(0, sign * sin(t)) for t in phases]),
                ('Arm_' + side, PITCH, [arms - sign * stride * .42 * cos(t) for t in phases]),
            ])
        return clip(times, *tracks, positions=vertical([.045 * sin(t) ** 2 for t in phases]))

    def swing(side, times, load, reach, twist):
        other = 'L' if side == 'R' else 'R'
        t = -twist if side == 'L' else twist
        return clip(times, ('Chest', YAW, (0, -t * .63, t, t * .31, 0)),
                    ('Shoulder_' + side, YAW, (0, -t, t * .62, t * .24, 0)),
                    ('Arm_' + side, PITCH, (-22, load, reach, 27, -22)),
                    ('Hand_' + side, PITCH, (0, 26, -21, 3, 0)),
                    ('Arm_' + other, PITCH, (-16, -24, 20, 0, -16)))

    def held(times, body, right, left):
        return clip(times, ('Chest', YAW, body), ('Arm_R', PITCH, right), ('Arm_L', PITCH, left))

    return {
        'zombie': {
            'idle': idle(-42, 5, 1.52), 'walk': walk(1.05, 29, -50), 'chase': walk(.58, 42, -71),
            'attack1': swing('R', [0, .28, .48, .66, .85], 38, -83, 44),
            'attack2': swing('L', [0, .28, .5, .67, .85], 45, -89, 52),
            'attack3': clip([0, .32, .55, .74, 1.15], ('Chest', PITCH, (0, -20, 34, 20, 0)),
                            ('Head', PITCH, (0, -16, 29, 12, 0)),
                            ('Arm_R', PITCH, (-44, -52, 20, 14, -44)),
                            ('Arm_L', PITCH, (-47, -50, 19, 17, -47))),
        },
        'wither_skeleton': {
            'idle': idle(-19, 3, 1.87), 'walk': walk(1.19, 33, -20), 'chase': walk(.64, 55, -39),
            'special_spawn': clip([0, .25, .72, 1.45], ('Root', PITCH, (54, 43, -8, 0)),
                                  ('Arm_R', ROLL, (28, 64, 31, 6)), ('Arm_L', ROLL, (-28, -64, -31, -6)),
                                  positions=vertical((-.76, -.42, .12, 0))),
            'sword_attack1': swing('R', [0, .21, .35, .53, .72], -116, -55, 81),
            'sword_attack2': swing('R', [0, .19, .29, .48, .72], -45, -62, -90),
            'sword_attack3': swing('R', [0, .2, .31, .53, .74], -155, -86, 25),
        },
        'illager': {
            'idle': idle(-27, 4, 1.63), 'walk': walk(.9, 30, -23),
            'idle_aggressive': idle(-51, 8, .83), 'chase': walk(.55, 50, -41),
            'spellcast': clip([0, .26, .57, .88], ('Chest', PITCH, (-4, -17, -11, -4)),
                             ('Arm_R', ROLL, (-62, -116, -89, -62)),
                             ('Arm_L', ROLL, (62, 116, 89, 62)), ('Head', PITCH, (-6, -19, -15, -6))),
            'swing_axe1': swing('R', [0, .24, .34, .51, .9], -121, -59, 73),
            'swing_axe2': swing('R', [0, .23, .36, .56, .9], -57, -89, -72),
            'swing_axe3': swing('R', [0, .32, .52, .69, 1.05], -150, -75, 22),
        },
        'piglin': {
            'idle': idle(-17, 8, 1.74), 'walk': walk(.93, 35, -23),
            'zombified_idle': idle(-42, 4, 1.25), 'zombified_walk': walk(1.16, 30, -40),
            'zombified_chase': walk(.61, 47, -58),
            'celebrate1': held([0, .25, .5, .75], (0, -27, 25, 0), (-47, -126, -63, -47), (-62, -73, -123, -62)),
            'celebrate2': clip([0, .2, .42, .82], ('Arm_R', ROLL, (-34, -113, -65, -34)),
                               ('Arm_L', ROLL, (34, 113, 63, 34)), positions=vertical((0, .08, .16, 0))),
            'celebrate3': clip([0, .16, .43, .78], ('Head', PITCH, (0, -22, 16, 0)),
                               ('Torso', YAW, (0, 29, -28, 0)), ('Ear_L', ROLL, (0, 17, -7, 0)),
                               ('Ear_R', ROLL, (0, -11, 8, 0))),
            'admire': clip([0, .37, .78, 1.15], ('Arm_L', PITCH, (-55, -76, -65, -55)),
                           ('Hand_L', PITCH, (0, 12, -6, 0)), ('Head', PITCH, (16, 28, 22, 16))),
            'death': collapse(clip, .78, 'Head'),
        },
        'witch': {'drink': clip([0, .28, .57, .92], ('Head', PITCH, (0, -16, -24, 0)),
                               ('Arm_R', PITCH, (-28, -83, -91, -28)),
                               ('Hand_R', PITCH, (0, -12, -26, 0)))},
        'biped/combat': {
            'hit_short': recovery(clip, 'Chest', 'Head', .38, 25),
            'hit_long': recovery(clip, 'Chest', 'Head', .96, 45),
            'hit_on_mount': recovery(clip, 'Chest', 'Head', .71, 24),
            'knockdown': clip([0, .22, .7, 1.2, 1.55], ('Root', PITCH, (0, -61, -86, -35, 0)),
                              ('Thigh_R', PITCH, (0, -48, -59, -67, 0)), positions=vertical((0, -.48, -.76, -.47, 0))),
            'crossbow_aim': held([0, .4, .8], (-20, -22, -20), (-74, -76, -74), (-63, -65, -63)),
            'crossbow_reload': held([0, .28, .62, 1.15], (-12, -25, 7, -22), (-54, -35, -61, -74), (-65, -29, -69, -63)),
            'crossbow_shot': held([0, .09, .27, .55], (-20, -35, -18, -20), (-74, -101, -71, -74), (-63, -79, -60, -63)),
        },
        'biped/living': {
            'death': collapse(clip, .83, 'Head'), 'walk_twohand': walk(.94, 27, -53),
            'landing': clip([0, .16, .41], ('Chest', PITCH, (0, 24, 0)),
                            ('Thigh_R', PITCH, (0, -39, 0)), ('Thigh_L', PITCH, (0, -33, 0)),
                            positions=vertical((0, -.16, 0))),
            'mount': clip([0, .43, .86], ('Thigh_R', PITCH, (-66, -68, -66)),
                          ('Thigh_L', PITCH, (-66, -68, -66)), ('Leg_R', PITCH, (59, 61, 59)),
                          ('Leg_L', PITCH, (59, 61, 59)), ('Chest', PITCH, (5, 10, 5))),
        },
        'biped/skill': {'guard_break1': recovery(clip, 'Chest', 'Head', .95, 51)},
    }


def creature_motions(clip):
    def idle(center, period, angle):
        return clip([0, period / 2, period], (center, PITCH, (0, angle, 0)),
                    ('Head', YAW, (-angle, angle, -angle)), positions=vertical((0, .034, 0)))

    def quadruped_walk(period, stride, segmented=False):
        times, phases = cycle(period)
        joints = [('Torso', ROLL, [2.5 * cos(t) for t in phases])]
        for foot, sign in (('LF', 1), ('RF', -1), ('LB', -1), ('RB', 1)):
            upper = 'Thigh_' if segmented else 'Leg_'
            joints.append((upper + foot, PITCH, [sign * stride * cos(t) for t in phases]))
            if segmented:
                joints.append(('Leg_' + foot, PITCH, [-stride * max(0, sign * sin(t)) for t in phases]))
        return clip(times, *joints, positions=vertical([.041 * sin(t) ** 2 for t in phases]))

    def head_charge(times, body, head, neck=None, reach=0):
        rotations = [('Torso', PITCH, body), ('Head', PITCH, head)]
        if neck:
            rotations.append((neck, PITCH, (0, 15, -22, -7, 0)))
        return clip(times, *rotations, positions={'Coord': advance((0, 0, reach * .82, reach, reach))} if reach else None)

    def spider_walk():
        times, phases = cycle(.72)
        legs = []
        for side, sign in (('L', 1), ('R', -1)):
            for i in range(1, 5):
                legs.append((f'{side}L{i}', YAW, [sign * 24 * cos(t + i * pi) for t in phases]))
        return clip(times, *legs, ('Head', PITCH, [3 * cos(t) for t in phases]),
                    positions=vertical([.038 * sin(t) ** 2 for t in phases]))

    def spider_crouch(times, head, pitch, spread, travel=None):
        tracks = [('Root', PITCH, pitch), ('Head', PITCH, head), ('Stomach', PITCH, [angle * -.32 for angle in pitch])]
        for side, sign in (('L', 1), ('R', -1)):
            tracks.append((side + 'L1', ROLL, [angle * sign for angle in spread]))
            tracks.append((side + 'L2', YAW, [angle * .65 * sign for angle in spread]))
        return clip(times, *tracks, positions={'Coord': travel} if travel else None)

    def golem_walk():
        times, phases = cycle(1.34)
        return clip(times, ('Chest', ROLL, [4 * cos(t) for t in phases]),
                    ('LR1', PITCH, [26 * cos(t) for t in phases]), ('RR1', PITCH, [-26 * cos(t) for t in phases]),
                    ('LA1', PITCH, [-16 * cos(t) for t in phases]), ('RA1', PITCH, [20 * cos(t) for t in phases]),
                    positions=vertical([.065 * sin(t) ** 2 for t in phases]))

    def golem_strike(side, times, lift, landing, twist):
        return clip(times, ('Chest', YAW, (0, -twist, twist * .65, twist * .38, 0)),
                    (side + 'A1', PITCH, (0, lift, landing, 11, 0)),
                    (side + 'A2', PITCH, (0, -24, 11, 21, 0)),
                    ('Head', PITCH, (0, -11, 26, 13, 0)))

    def vex_flight(times, bank, flap, lean, positions=None):
        return clip(times, ('Root', ROLL, bank), ('Chest', PITCH, lean),
                    ('Wing_L', YAW, flap), ('Wing_R', YAW, [-a for a in flap]),
                    ('Tail', PITCH, [-a * .37 for a in lean]), positions=positions)

    return {
        'creeper': {'idle': idle('Torso', 1.35, 3.4), 'walk': quadruped_walk(.67, 37),
                    'hit_short': recovery(clip, 'Torso', 'Head', .37, 19),
                    'hit_long': recovery(clip, 'Torso', 'Head', .85, 41), 'death': collapse(clip, .37, 'Head')},
        'spider': {
            'idle': idle('Stomach', 1.08, 5), 'crawl': spider_walk(),
            'attack': spider_crouch([0, .22, .32, .37, .46], (0, -15, 26, 19, 0),
                                     (0, -13, 18, 9, 0), (0, 22, -24, 13, 0)),
            'jump_attack': spider_crouch([0, .24, .51, .64, 1.0], (0, -14, 24, 16, 0),
                                          (0, -23, 25, 7, 0), (0, 41, -25, -16, 0),
                                          advance((0, .05, .82, 1.24, 1.24), (0, .11, .58, .34, 0))),
            'hit': recovery(clip, 'Stomach', 'Head', .34, 21),
            'neutralized': spider_crouch([0, .2, .72, 1.28], (0, 29, 22, 0), (0, 14, 10, 0), (0, -36, -42, 0)),
            'death': collapse(clip, .22, 'Head', .91),
        },
        'iron_golem': {
            'idle': idle('Chest', 2.17, 2.1), 'walk': golem_walk(),
            'attack1': clip([0, .14, .27, .46, .9], ('Root', PITCH, (0, -14, 27, 8, 0)),
                            ('Head', PITCH, (0, -24, 31, 11, 0)),
                            ('RA1', PITCH, (0, 12, -43, 16, 0)), ('LA1', PITCH, (0, 16, -36, 19, 0))),
            'attack2': golem_strike('L', [0, .31, .51, .79, 1.3], -148, -61, 47),
            'attack3': golem_strike('R', [0, .28, .46, .65, .9], -72, -79, -64),
            'attack4': golem_strike('L', [0, .29, .47, .66, .9], -98, -54, 68),
            'death': collapse(clip, 1.07, 'Head', 1.52),
        },
        'hoglin': {'idle': idle('Torso', 1.57, 6), 'walk': quadruped_walk(.86, 29, segmented=True),
                   'attack': head_charge([0, .19, .35, .56, 1.0], (0, 14, -11, -4, 0), (0, 24, -36, -18, 0)),
                   'death': collapse(clip, .51, 'Head', 1.27)},
        'ravager': {
            'idle': idle('Torso', 1.82, 3.7), 'walk': quadruped_walk(1.03, 22),
            'attack1': head_charge([0, .25, .43, .49, .57], (0, 16, -25, -14, 0), (0, 29, -36, -14, 0), 'Head_Root'),
            'attack2': head_charge([0, .24, .47, .79, 1.3], (0, 16, -29, -6, 0), (0, 31, -42, -18, 0), 'Head_Root', .63),
            'attack3': head_charge([0, .68, 1.13, 1.34, 1.6], (0, 24, -21, -17, 0), (0, 28, -48, -25, 0), 'Head_Root', .94),
            'groggy': recovery(clip, 'Torso', 'Head', 1.8, 40), 'death': collapse(clip, .97, 'Head', 1.44),
        },
        'vex': {
            'idle': vex_flight([0, .105, .21, .315, .42], (0, 3, 0, -3, 0), (14, 69, 18, -34, 14), (0, 3, 0, -3, 0)),
            'flip': vex_flight([0, .14, .28, .42, .56], (0, 80, 177, 277, 360), (14, 30, -12, 46, 14), (0, -19, 3, 17, 0)),
            'charge': vex_flight([0, .27, .41, .66, 1.5], (0, -19, 5, 10, 0), (14, 44, -32, 53, 14),
                                 (0, -18, 31, 13, 0), {'Coord': advance((0, .03, .56, 1.28, 1.28))}),
            'hit': recovery(clip, 'Chest', 'Head', .32, 33), 'neutralized': recovery(clip, 'Chest', 'Head', 1., 50),
            'death': collapse(clip, .37, 'Head', .87),
        },
    }


def clips(frame, track):
    clip = timeline(frame, track)
    return {**humanoid_motions(clip), **creature_motions(clip)}
