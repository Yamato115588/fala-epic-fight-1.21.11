# SPDX-License-Identifier: CC0-1.0
"""Original poses for the replacement Enderman rig, in seconds and degrees."""
from math import cos, pi, sin

PITCH = (1, 0, 0)
YAW = (0, 1, 0)
ROLL = (0, 0, 1)


def clips(frame, track):
    def motion(times, *rotations, heights=None):
        channels = []
        for joint, axis, angles in rotations:
            poses = [frame(axis, angle, (0, heights[i], 0) if joint == 'Root' and heights else (0, 0, 0))
                     for i, angle in enumerate(angles)]
            channels.append(track(joint, times, poses))
        return {'format': 'ATTRIBUTES', 'animation': channels}

    def stride(period, reach, alert):
        times = [round(i * period / 8, 5) for i in range(9)]
        phases = [i * pi / 4 for i in range(9)]
        joints = [('Chest', YAW, [5 * cos(phase) for phase in phases]),
                  ('Head_Top', PITCH, [alert] * 9)]
        for side, sign in (('R', 1), ('L', -1)):
            joints.extend([
                ('Thigh_' + side, PITCH, [sign * reach * cos(phase) for phase in phases]),
                ('Leg_' + side, PITCH, [-.48 * reach * max(0, sign * sin(phase)) for phase in phases]),
                ('Arm_' + side, PITCH, [-(alert / 2) - sign * .7 * reach * cos(phase) for phase in phases]),
            ])
        return motion(times, *joints)

    def kick(side, times, lift, bend, height):
        return motion(times,
                      ('Root', PITCH, (0, 8, -12, -5, 0)),
                      ('Thigh_' + side, PITCH, (0, -37, -lift, -26, 0)),
                      ('Leg_' + side, PITCH, (0, 66, bend, 28, 0)),
                      ('Arm_' + side, PITCH, (0, -28, 24, 9, 0)),
                      ('Head_Top', PITCH, (9, 24, 31, 20, 9)),
                      heights=(0, -.08, height, -.08, 0))

    return {
        'idle': motion([0, .65, 1.3, 1.95], ('Chest', PITCH, (1, 3, 0, 1)), ('Head', YAW, (0, 3, -3, 0))),
        'walk': stride(1.12, 22, 0),
        'rage_idle': motion([0, .3, .6], ('Chest', PITCH, (11, 16, 11)),
                            ('Arm_R', PITCH, (-16, -21, -16)), ('Arm_L', PITCH, (-17, -23, -17)),
                            ('Head_Top', PITCH, (25, 32, 25))),
        'rage_walk': stride(.72, 38, 27),
        'hit_short': motion([0, .085, .21, .4], ('Chest', PITCH, (0, -19, 6, 0)), ('Head', YAW, (0, 19, -5, 0))),
        'hit_long': motion([0, .1, .43, .94], ('Root', ROLL, (0, 16, -9, 0)),
                           ('Chest', PITCH, (0, -27, 20, 0)), ('Arm_R', PITCH, (0, 36, -27, 0)),
                           heights=(0, -.04, -.19, 0)),
        'neutralized': motion([0, .18, .86, 1.3], ('Root', PITCH, (0, 20, 23, 0)),
                              ('Thigh_L', PITCH, (0, -72, -63, 0)), ('Leg_L', PITCH, (0, 97, 82, 0)),
                              ('Thigh_R', PITCH, (0, -60, -61, 0)), ('Leg_R', PITCH, (0, 84, 91, 0)),
                              heights=(0, -.66, -.70, 0)),
        'convert_rage': motion([0, .2, .42, .87, 1.1], ('Chest', PITCH, (0, 28, -12, 16, 11)),
                               ('Head_Top', PITCH, (0, 6, 42, 29, 25)),
                               ('Arm_L', ROLL, (0, 15, 59, 24, 11)), ('Arm_R', ROLL, (0, -15, -59, -24, -11))),
        'tp_kick1': kick('R', [0, .15, .33, .57, 1.0], 67, 9, .04),
        'tp_kick2': kick('R', [0, .15, .29, .55, 1.0], 58, 17, .09),
        'rush_kick': kick('L', [0, .47, .75, 1.03, 1.6], 73, 12, .04),
        'jump_kick': kick('R', [0, .53, .85, 1.05, 1.3], 82, 11, .28),
        'knee': kick('R', [0, .19, .27, .56, 1.0], 81, 96, -.01),
        'kick_twice': motion([0, .14, .2, .39, .58, .78, 1.12, 1.6],
                             ('Root', PITCH, (0, 8, -9, 8, 10, -12, 5, 0)),
                             ('Thigh_R', PITCH, (0, -34, -66, -26, 0, 17, 0, 0)),
                             ('Leg_R', PITCH, (0, 63, 15, 26, 0, 0, 0, 0)),
                             ('Thigh_L', PITCH, (0, 0, 16, 0, -33, -73, -23, 0)),
                             ('Leg_L', PITCH, (0, 0, 0, 0, 65, 13, 16, 0)),
                             heights=(0, -.07, .02, -.07, -.09, .02, -.03, 0)),
        'grasp': motion([0, .24, .46, .62, 1.04], ('Chest', PITCH, (0, -15, 22, 25, 0)),
                        ('Arm_R', PITCH, (0, -23, -79, -66, 0)), ('Arm_L', PITCH, (0, -27, -64, -71, 0)),
                        ('Hand_R', PITCH, (0, 16, 4, -26, 0)), ('Head_Top', PITCH, (0, 8, 31, 26, 0))),
        'teleport': motion([0, .13, .32, .57], ('Root', PITCH, (25, 14, -8, 0)),
                           ('Thigh_R', PITCH, (-29, -32, -10, 0)), ('Thigh_L', PITCH, (-36, -19, -14, 0)),
                           ('Arm_R', ROLL, (-39, -46, -19, 0)), ('Arm_L', ROLL, (38, 45, 16, 0)),
                           heights=(-.37, -.26, .05, 0)),
        'death': motion([0, .24, .58, .91, 1.55], ('Root', ROLL, (0, -16, -51, -89, -92)),
                        ('Arm_R', PITCH, (0, 30, 16, -18, -10)), ('Arm_L', PITCH, (0, -38, -22, 8, 5)),
                        ('Head_Top', PITCH, (18, 30, 16, 9, 9)), heights=(0, -.09, -.61, -1.18, -1.18)),
    }
