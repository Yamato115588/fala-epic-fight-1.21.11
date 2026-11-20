# SPDX-License-Identifier: CC0-1.0
"""Independent boss poses with keyframes at the port's phase and IK boundaries."""
from math import cos, sin
from mob_motions import PITCH, ROLL, YAW, advance, cycle, timeline, vertical


def dragon_clips(clip):
    def flight(times, body, wing, jaw, heights, travel=None, braced=False):
        tracks = [('Torso', PITCH, body), ('Head', PITCH, [a * -.6 for a in body]),
                  ('Mouth_Lower', PITCH, jaw), ('Neck3', PITCH, [a * .37 for a in body])]
        for index in (2, 5, 9, 12):
            tracks.append((f'Tail{index}', YAW, [sin(i * .97 + index * .22) * 4.2 for i in range(len(times))]))
        for side, sign in (('L', 1), ('R', -1)):
            tracks.extend([
                (f'Wing_{side}1', ROLL, [a * sign for a in wing]),
                (f'Wing_{side}2', ROLL, [-a * .56 * sign for a in wing]),
            ])
            for end, bend in (('Front', 15), ('Back', 21)):
                leg = f'Leg_{end}_{side}'
                fold = [.68 * a - (0 if braced else bend) for a in body]
                tracks.extend([(leg + '1', PITCH, fold), (leg + '2', PITCH, [-a * 1.3 for a in fold]),
                               (leg + '3', PITCH, [a * .49 for a in fold])])
        positions = vertical(heights)
        if travel is not None:
            positions['Coord'] = advance(travel[0], travel[1])
        return clip(times, *tracks, positions=positions)

    def flight_cycle(period, diving=False):
        times, phases = cycle(period)
        return flight(times, [(-15 if diving else 0) + 8 * cos(t) for t in phases],
                      [56 * sin(t) for t in phases], [6 + 3 * cos(t) for t in phases],
                      [.15 * cos(t) for t in phases])

    def walk():
        times, phases = cycle(1.75)
        tracks = [('Torso', YAW, [3.1 * cos(t) for t in phases]), ('Head', PITCH, [4 * sin(t) for t in phases])]
        for side, sign in (('L', 1), ('R', -1)):
            for end, offset in (('Front', 1), ('Back', -1)):
                foot = f'Leg_{end}_{side}'
                stride = [cos(t) * sign * offset for t in phases]
                tracks.extend([(foot + '1', PITCH, [17 * v for v in stride]),
                               (foot + '2', PITCH, [-27 * max(0, v) for v in stride]),
                               (foot + '3', PITCH, [12 * max(0, v) for v in stride])])
        return clip(times, *tracks, positions=vertical([.14 * sin(t) ** 2 for t in phases]))

    def claw(side, times, force, turn):
        swipe = (0, -8, -34, -63, -force, -37, 13, 4, 0)
        legs = []
        for name in ('Front_L', 'Front_R', 'Back_L', 'Back_R'):
            foot = 'Leg_' + name
            sweep = swipe if name == 'Front_' + side else [v * -.14 for v in swipe]
            legs.extend([(foot + '1', PITCH, sweep), (foot + '2', PITCH, [-v * .66 for v in sweep]),
                         (foot + '3', PITCH, [v * .32 for v in sweep])])
        return clip(times, *legs, ('Torso', YAW, (0, 0, -turn, -turn, turn, turn * .65, 7, 4, 0)),
                    ('Mouth_Lower', PITCH, (3, 6, 13, 27, 43, 21, 10, 7, 3)),
                    positions=vertical((0, -.06, -.18, -.10, .14, .1, -.04, 0, 0)))

    return {
        'idle': flight([0, .63, 1.31, 2.03], (0, 3, -2, 0), (6, 9, 4, 6), (3, 8, 4, 3), (0, .065, .032, 0), braced=True),
        'walk': walk(), 'fly': flight_cycle(1.28), 'airstrike': flight_cycle(.76, diving=True),
        'death': clip([0, .55, 1.28, 2.1, 3.1], ('Root', ROLL, (0, -14, -43, -83, -89)),
                      ('Wing_L1', ROLL, (0, -24, -65, -74, -80)), ('Wing_R1', ROLL, (0, 17, 40, 29, 18)),
                      ('Mouth_Lower', PITCH, (5, 34, 49, 25, 12)), positions=vertical((0, -.12, -.48, -1.86, -2.58))),
        'ground_to_fly': flight([0, .14, .28, .48, .67, .92, 1.09, 1.31, 1.58],
                                (0, 8, 17, -18, -27, -24, -10, -5, 0), (0, 29, 65, -47, -24, 57, 41, -40, -12),
                                (4, 11, 23, 17, 5, 6, 5, 5, 5), (0, -.13, -.18, 0, .09, .06, 0, 0, 0),
                                ((0, 0, .04, .19, .59, 1.0, 1.87, 2.69, 3.15), (0, 0, 0, .12, .56, 1.12, 2.09, 2.9, 3.47))),
        'fly_to_ground': flight([0, .18, .35, .59, .83, 1.08, 1.22, 1.37, 1.64],
                                (0, 17, 24, 29, 23, 12, -9, 3, 0), (-32, 12, 56, -35, 14, 48, 21, 6, 2),
                                (5, 8, 12, 15, 20, 29, 16, 7, 3), (0, 0, .04, .09, .02, -.22, -.34, -.12, 0),
                                ((0, .25, .78, 1.3, 1.95, 2.65, 2.92, 3., 3.), (0, -.26, -.83, -1.42, -2.07, -2.8, -2.96, -3, -3)), True),
        'attack1': claw('R', [0, .25, .44, .61, .71, .86, 1.08, 1.42, 1.91], 89, 31),
        'attack2': claw('R', [0, .11, .21, .35, .51, .65, .69, .72, .79], 69, -33),
        'attack3': claw('L', [0, .13, .25, .35, .54, .63, .7, .74, .8], 75, 37),
        'attack4': flight([0, .23, .43, .62, .83, 1.04, 1.19, 1.47, 1.93], (0, 4, -7, -23, -37, -28, 25, 12, 2),
                          (12, 18, 42, 58, 68, 23, -45, -31, 8), (6, 4, 15, 31, 35, 49, 51, 19, 8),
                          (0, -.07, -.17, .02, .59, .62, -.42, -.56, -.21), braced=True),
        'attack4_recovery': flight([0, .15, .31, .51, .69, .86, 1.11], (19, 16, 12, 8, 6, 3, 0),
                                   (-32, -22, -12, 4, 22, 9, 6), (20, 14, 11, 7, 8, 6, 3), (-.51, -.54, -.48, -.28, -.16, -.06, 0), braced=True),
        'fireball': flight([0, .16, .35, .49, .66, .83, 1.04, 1.23], (0, -4, -11, -23, 10, 14, 5, 0),
                           (4, 7, 17, 25, 42, 23, 11, 4), (6, 15, 32, 58, 61, 34, 12, 6), (0, .02, .07, .13, -.22, -.17, -.04, 0), braced=True),
        'backjump_prepare': flight([0, .08, .16, .24, .32, .43], (0, 5, 13, 19, 26, 27),
                                   (6, 12, 19, 26, 40, 45), (3, 5, 9, 15, 8, 7), (0, -.08, -.23, -.37, -.54, -.58), braced=True),
        'backjump_move': flight([0, .19, .42, .69, .94, 1.13], (27, -19, -27, 8, 21, 24),
                                (45, -32, -53, 43, 67, 25), (7, 10, 14, 18, 7, 6), (-.58, -.14, 0, 0, -.07, -.16),
                                ((0, -.46, -1.54, -2.62, -3.24, -3.5), (0, .64, .98, .71, .33, 0))),
        'backjump_recovery': flight([0, .10, .17, .32, .51, .72], (24, 21, 16, 7, -1, 0),
                                    (26, 18, -8, 22, 10, 5), (6, 18, 20, 14, 6, 3), (-.16, -.43, -.58, -.31, -.13, 0), braced=True),
        'crystal_link': flight([0, .42, 1.06, 2.09, 4.07, 6.83, 7.23], (0, -8, -20, -17, -22, -12, 0),
                               (4, 21, 34, 14, 34, 18, 4), (5, 20, 46, 34, 50, 24, 4), (0, .13, .44, .46, .38, .23, 0), braced=True),
        'neutralized': flight([0, .21, .52, 1.04, 2.31, 3.46, 4.13], (0, 26, 34, 29, 26, 31, 28),
                              (9, -28, -59, -48, -39, -48, -44), (6, 41, 47, 31, 33, 27, 26), (0, -.4, -1.32, -1.49, -1.54, -1.5, -1.48), braced=True),
        'neutralized_recovery': flight([0, .19, .44, .71, 1.04, 1.34, 1.58, 1.76], (28, 31, 17, 12, -7, -9, 3, 0),
                                       (-44, -63, -47, -22, 21, 29, 15, 4), (26, 41, 37, 29, 22, 12, 6, 3),
                                       (-1.48, -1.51, -1.2, -.88, -.53, -.21, -.08, 0), braced=True),
    }


def wither_clips(clip):
    def hover(times, body, spread, lead, heights, heading=None, positions=None):
        tracks = [('Torso', PITCH, body), ('Tail', PITCH, [-a * .73 for a in body]),
                  ('Head_M', PITCH, lead), ('Head_L', YAW, [-a for a in spread]), ('Head_R', YAW, spread)]
        if heading:
            tracks.append(('Root', heading[0], heading[1]))
        offset = vertical(heights)
        if positions:
            offset['Coord'] = advance(positions)
        return clip(times, *tracks, positions=offset)

    return {
        'idle': hover([0, .51, 1.05, 1.59, 2.07], (0, -5, 3, 4, 0), (6, 14, 3, 7, 6),
                      (0, 3, -3, 2, 0), (0, .12, 0, -.11, 0)),
        'rush': hover([0, .22, .39, .51, .65, .86, 1.37, 2.11], (0, -19, 34, 44, 39, 26, 8, 0),
                      (8, 18, 12, 5, -7, -9, 15, 8), (0, -17, 31, 34, 21, 13, 5, 0),
                      (0, .12, .14, .11, .06, .03, .07, 0), positions=(0, .04, .3, 1.09, 2.39, 2.89, 3.14, 3.19)),
        'death': hover([0, .24, .58, .98, 1.52], (0, -12, 23, 39, 36), (8, 18, 41, 25, 13),
                       (0, -21, 18, 30, 27), (0, -.07, -.37, -1.05, -1.2), (ROLL, (0, 7, 39, 69, 88))),
        'neutralized': hover([0, .17, .39, .91, 1.44], (0, -41, 24, 11, 0), (8, 43, 31, -6, 8),
                             (0, -36, 27, 11, 0), (0, .07, -.44, -.35, 0), (ROLL, (0, 21, -19, 10, 0))),
        'spell_wither_armor': hover([0, .24, .52, .76, 1.18], (0, -12, -36, -19, 0), (8, 22, 55, 29, 8),
                                    (0, -15, -34, -20, 0), (0, .09, .29, .14, 0)),
        'charging_blocked': hover([0, .15, .36, .68, 1.11], (39, -17, -31, 16, 0), (5, 31, 42, 14, 8),
                                  (29, -25, -29, 13, 0), (.13, .18, -.27, -.21, 0)),
        'ghost_stand': hover([0, .41, .82, 1.22], (-6, -8, -3, -6), (17, 22, 14, 17),
                             (-8, -14, -2, -8), (0, .097, -.081, 0)),
        'swirl': hover([0, .25, .4, .51, .69, .85, 1.16, 1.65], (0, -9, 4, 12, 18, 9, 3, 0),
                       (8, 19, 32, 13, 8, 13, 17, 8), (0, -6, 11, 18, 11, 3, 2, 0),
                       (0, .15, .13, .05, -.08, -.07, .09, 0), (YAW, (0, -29, 21, 104, 198, 293, 352, 360))),
        'laser': hover([0, .24, .52, .72, .89, 1.29, 1.98, 2.32, 2.66], (0, -9, -24, -26, 13, 17, 16, 10, 0),
                       (8, 14, 37, 46, 17, 12, 16, 18, 8), (0, -13, -27, -20, 11, 18, 17, 6, 0),
                       (0, .09, .21, .19, -.03, -.11, .06, .08, 0)),
        'backflip': hover([0, .24, .43, .59, .78, .98, 1.36, 2.14], (0, -15, -28, -37, -26, 22, 7, 0),
                          (8, 18, 31, 27, 15, 6, 15, 8), (0, -11, -25, -31, -19, 18, 10, 0),
                          (0, -.08, .13, .42, .47, .38, .15, 0), (PITCH, (0, -17, -59, -121, -213, -295, -353, -360)),
                          (0, .04, -.14, -.51, -.87, -1.12, -1.34, -1.34)),
    }


def clips(frame, track):
    clip = timeline(frame, track)
    return {'dragon': dragon_clips(clip), 'wither': wither_clips(clip)}
