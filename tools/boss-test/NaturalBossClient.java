package fala.bosstest;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import net.fabricmc.api.ClientModInitializer;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.boss.wither.WitherBoss;
import yesman.epicfight.gameasset.Armatures;
import yesman.epicfight.registry.entries.EpicFightParticles;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.boss.WitherPatch;
import yesman.epicfight.world.capabilities.entitypatch.boss.enderdragon.EnderDragonPatch;
import yesman.epicfight.world.entity.WitherGhostClone;

public final class NaturalBossClient implements ClientModInitializer {
    private final Map<String, String> last = new HashMap<>();
    private final Set<String> sounds = new HashSet<>();
    private boolean listening;
    private int ticks;

    @Override
    public void onInitializeClient() {
        NaturalBossServer.subscribe("net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents",
                "EndTick", "END_CLIENT_TICK", value -> tick((Minecraft) value));
    }

    private void tick(Minecraft mc) {
        if (mc.level == null || mc.player == null) return;
        ticks++;
        if (!listening) {
            listening = true;
            mc.getSoundManager().addListener((sound, events, distance) -> {
                String id = sound.getIdentifier().toString();
                if ((id.startsWith("epicfight:") || id.contains("wither") || id.contains("ender_dragon"))
                        && sounds.add(id)) System.out.println("FALA_NATURAL client sound " + id);
            });
        }
        if (ticks == 30) {
            var player = mc.player;
            var dust = mc.particleEngine.createParticle(EpicFightParticles.DUST_CONTRACTIVE.get(),
                    player.getX() + 1, player.getY() + 1, player.getZ(), -.02, 0, 0);
            if (dust == null) throw new IllegalStateException("Dust particle provider returned no particle");
            record("particle", "dust_contractive created");
            record("ready", player.getName().getString());
        }
        for (var entity : mc.level.entitiesForRendering()) {
            if (entity instanceof EnderDragon dragon) {
                var patch = EpicFightCapabilities.getEntityPatch(dragon, EnderDragonPatch.class);
                if (patch == null) continue;
                record("dragon", dragon.getPhaseManager().getCurrentPhase().getPhase().toString());
                var motion = patch.getAnimator().getPlayerFor(null).getRealAnimation().registryName();
                if (motion != null) record("dragon animation", motion.toString());
                if (patch.getIKSimulator().isRunning(Armatures.DRAGON.get().legFrontL3)) {
                    patch.getClientAnimator().getPose(.5F);
                    record("dragon IK", "active");
                }
                if (dragon.isDeadOrDying()) record("dragon death", "true");
            } else if (entity instanceof WitherBoss wither) {
                var patch = EpicFightCapabilities.getEntityPatch(wither, WitherPatch.class);
                if (patch == null) continue;
                record("wither armor", Boolean.toString(patch.isArmorActivated()));
                record("wither ghost", Boolean.toString(patch.isGhost()));
                var motion = patch.getAnimator().getPlayerFor(null).getRealAnimation().registryName();
                if (motion != null) record("wither animation", motion.toString());
                if (patch.getLaserTargetEntity(0) != null && patch.getLaserTargetEntity(1) != null
                        && patch.getLaserTargetEntity(2) != null) record("wither lasers", "3");
                if (wither.isDeadOrDying()) record("wither death", "true");
            } else if (entity instanceof WitherGhostClone) {
                record("wither clone", entity.getUUID().toString());
            }
        }
    }

    private void record(String key, String value) {
        if (!value.equals(last.put(key, value))) {
            System.out.println("FALA_NATURAL client tick=" + ticks + " " + key + " " + value);
        }
    }
}
