# SPDX-License-Identifier: CC0-1.0
"""Event aliases resolve against Minecraft's installed sound library."""

VANILLA_EVENTS = {
    'entity.hit.blade': ('entity.player.attack.crit', .94, 1.08),
    'entity.hit.blunt': ('entity.player.attack.strong', .92, .96),
    'entity.hit.blunt_hard': ('entity.iron_golem.attack', .9, .84),
    'entity.hit.clash': ('item.shield.block', .9, 1.18),
    'entity.hit.eviscerate': ('entity.player.attack.crit', 1., .76),
    'entity.hit.blade_rush_last': ('item.trident.hit', .86, .82),
    'entity.hit.old_fall': ('entity.player.big_fall', .88, .94),
    'entity.weapon.sword_in': ('item.armor.equip_chain', .63, 1.23),
    'entity.weapon.whoosh': ('entity.player.attack.sweep', .86, .99),
    'entity.weapon.whoosh_hard': ('entity.player.attack.sweep', .96, .71),
    'entity.weapon.whoosh_small': ('entity.player.attack.weak', .55, 1.25),
    'entity.weapon.whoosh_sharp': ('entity.player.attack.sweep', .78, 1.32),
    'entity.weapon.whoosh_rod': ('entity.player.attack.nodamage', .77, .86),
    'entity.enderdragon.dragon_breath': ('entity.ender_dragon.shoot', .85, .8),
    'entity.enderdragon.dragon_breath_finale': ('entity.ender_dragon.growl', .88, .73),
    'entity.enderdragon.dragon_crystal_link': ('block.beacon.activate', .8, .79),
    'entity.wither.wither_spell_armor': ('entity.wither.spawn', .75, 1.16),
    'sfx.buzz': ('block.conduit.ambient', .65, .84),
    'sfx.laser_blast': ('entity.warden.sonic_boom', .81, 1.05),
    'sfx.slam_light': ('entity.iron_golem.step', .86, .84),
    'sfx.slam_heavy': ('block.anvil.land', .66, .73),
    'sfx.neutralize_bosses': ('block.bell.resonate', .9, .68),
    'sfx.neutralize_mobs': ('item.shield.block', .84, .86),
    'sfx.nether_star_glitter': ('block.amethyst_block.chime', .8, 1.17),
    'sfx.entity_move': ('entity.player.attack.nodamage', .54, 1.03),
    'sfx.big_entity_move': ('entity.ender_dragon.flap', .73, .83),
    'skill.adaptive_skin_increase': ('block.amethyst_block.chime', .76, 1.37),
    'skill.adaptive_skin_decrease': ('block.amethyst_block.hit', .72, .77),
    'skill.adrenaline': ('entity.warden.heartbeat', .77, 1.39),
    'skill.catharsis': ('block.beacon.power_select', .86, .93),
    'skill.endurance': ('item.shield.block', .7, .79),
    'skill.emergency_escape': ('item.trident.riptide_1', .56, 1.29),
    'skill.forbidden_strength': ('block.respawn_anchor.charge', .78, .73),
    'skill.hypervitality': ('block.conduit.activate', .81, 1.18),
    'skill.rocket_jump': ('entity.blaze.shoot', .87, 1.35),
    'skill.roll': ('entity.player.attack.nodamage', .68, .75),
    'skill.stamina_pillager_death': ('block.note_block.chime', .64, 1.09),
    'skill.swordmaster': ('entity.player.attack.sweep', .8, 1.44),
    'skill.technician': ('item.crossbow.loading_end', .7, 1.17),
    'skill.tumble': ('entity.player.small_fall', .7, 1.42),
    'skill.vengeance': ('entity.evoker.prepare_attack', .75, .87),
    'ui.hover': ('ui.button.click', .42, 1.37),
}


def definitions():
    events = {
        event: {'sounds': [{'name': f'minecraft:{vanilla}', 'type': 'event', 'volume': volume, 'pitch': pitch}]}
        for event, (vanilla, volume, pitch) in VANILLA_EVENTS.items()
    }
    events['sfx.no_sound'] = {'sounds': ['epicfight:compat/silence']}
    return events
