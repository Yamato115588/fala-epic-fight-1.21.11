"""Apply class moves confirmed in Mojang's Minecraft 1.21.11 mappings."""

import re


MOVES = {
    'resources.ResourceLocation': 'resources.Identifier',
    'Util': 'util.Util',
    'client.renderer.RenderType': 'client.renderer.rendertype.RenderType',
    'client.model.PlayerModel': 'client.model.player.PlayerModel',
    'client.resources.PlayerSkin': 'world.entity.player.PlayerSkin',
    'world.item.UseAnim': 'world.item.ItemUseAnimation',
    'world.item.ArmorMaterial': 'world.item.equipment.ArmorMaterial',
    'world.item.armortrim.ArmorTrim': 'world.item.equipment.trim.ArmorTrim',
    'world.level.GameRules': 'world.level.gamerules.GameRules',
    'world.entity.MobSpawnType': 'world.entity.EntitySpawnReason',
    'world.entity.projectile.AbstractArrow': 'world.entity.projectile.arrow.AbstractArrow',
    'world.entity.projectile.ThrownTrident': 'world.entity.projectile.arrow.ThrownTrident',
    'world.entity.projectile.Arrow': 'world.entity.projectile.arrow.Arrow',
    'world.entity.projectile.SpectralArrow': 'world.entity.projectile.arrow.SpectralArrow',
    'world.entity.projectile.WitherSkull': 'world.entity.projectile.hurtingprojectile.WitherSkull',
    'world.entity.projectile.DragonFireball': 'world.entity.projectile.hurtingprojectile.DragonFireball',
    'world.entity.animal.IronGolem': 'world.entity.animal.golem.IronGolem',
    'world.entity.animal.horse.AbstractHorse': 'world.entity.animal.equine.AbstractHorse',
    'world.entity.monster.Drowned': 'world.entity.monster.zombie.Drowned',
    'world.entity.monster.ZombieVillager': 'world.entity.monster.zombie.ZombieVillager',
    'world.entity.monster.ZombifiedPiglin': 'world.entity.monster.zombie.ZombifiedPiglin',
    'world.entity.monster.AbstractSkeleton': 'world.entity.monster.skeleton.AbstractSkeleton',
    'world.entity.monster.WitherSkeleton': 'world.entity.monster.skeleton.WitherSkeleton',
    'world.entity.monster.AbstractIllager': 'world.entity.monster.illager.AbstractIllager',
    'world.entity.monster.Pillager': 'world.entity.monster.illager.Pillager',
    'world.entity.monster.SpellcasterIllager': 'world.entity.monster.illager.SpellcasterIllager',
    'world.entity.monster.Spider': 'world.entity.monster.spider.Spider',
    'world.entity.boss.EnderDragonPart': 'world.entity.boss.enderdragon.EnderDragonPart',
    'world.entity.npc.VillagerData': 'world.entity.npc.villager.VillagerData',
    'world.entity.npc.VillagerDataHolder': 'world.entity.npc.villager.VillagerDataHolder',
    'world.entity.npc.VillagerProfession': 'world.entity.npc.villager.VillagerProfession',
    'client.model.WitherBossModel': 'client.model.monster.wither.WitherBossModel',
    'client.model.IronGolemModel': 'client.model.animal.golem.IronGolemModel',
    'client.model.DrownedModel': 'client.model.monster.zombie.DrownedModel',
    'client.model.ZombieVillagerModel': 'client.model.monster.zombie.ZombieVillagerModel',
    'client.model.IllagerModel': 'client.model.monster.illager.IllagerModel',
    'client.model.WitchModel': 'client.model.monster.witch.WitchModel',
    'client.model.VexModel': 'client.model.monster.vex.VexModel',
    'client.model.CreeperModel': 'client.model.monster.creeper.CreeperModel',
    'client.model.HoglinModel': 'client.model.monster.hoglin.HoglinModel',
    'client.model.SpiderModel': 'client.model.monster.spider.SpiderModel',
    'client.model.RavagerModel': 'client.model.monster.ravager.RavagerModel',
    'client.model.EndermanModel': 'client.model.monster.enderman.EndermanModel',
}

JAVA_MOVES = [
    (
        re.compile(r'(?<![\w.])' + re.escape('net.minecraft.' + old) + r'(?![\w])'),
        'net.minecraft.' + new,
        re.compile(r'\b' + re.escape(old.rsplit('.', 1)[-1]) + r'\b'),
        old.rsplit('.', 1)[-1],
        new.rsplit('.', 1)[-1],
    )
    for old, new in MOVES.items()
]
BINARY_MOVES = [
    (
        re.compile(re.escape('net/minecraft/' + old.replace('.', '/')) + r'(?![\w/])'),
        'net/minecraft/' + new.replace('.', '/'),
    )
    for old, new in MOVES.items()
]


def relocate_java(source):
    for full_name, target, short_name, old, new in JAVA_MOVES:
        source, count = full_name.subn(target, source)
        if count and old != new:
            source = short_name.sub(new, source)
    return relocate_binary(source)


def relocate_binary(source):
    for name, target in BINARY_MOVES:
        source = name.sub(target, source)
    return source


def migrate(source_tree):
    changed = 0
    for path in sorted((source_tree / 'src').rglob('*.java')):
        before = path.read_text(encoding='utf-8')
        after = relocate_java(before)
        if before != after:
            path.write_text(after, encoding='utf-8')
            changed += 1
    widener = source_tree / 'src/main/resources/epicfight.accesswidener'
    original = widener.read_bytes().decode('utf-8')
    widener.write_bytes(relocate_binary(original).encode('utf-8'))
    return changed
