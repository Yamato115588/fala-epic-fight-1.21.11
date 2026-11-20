package fala.tests;

import java.util.List;
import java.util.Locale;
import java.util.Properties;
import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.minecraft.data.AtlasIds;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import yesman.epicfight.api.client.model.Meshes;
import yesman.epicfight.gameasset.Armatures;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.registry.entries.EpicFightParticles;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.boss.enderdragon.EnderDragonPatch;
import yesman.epicfight.world.capabilities.entitypatch.boss.enderdragon.PatchedPhases;

public final class PortWorldTest implements FabricClientGameTest {
    @Override
    public void runTest(ClientGameTestContext context) {
        context.runOnClient(client -> {
            if (Boolean.getBoolean("fala.test.bossRegressions")) {
                client.options.renderDistance().set(3);
                client.options.simulationDistance().set(5);
            }
            client.getAtlasManager().getAtlasOrThrow(AtlasIds.ARMOR_TRIMS);
            if (Armatures.ENDERMAN.get().headTop == null || Meshes.ENDERMAN.get().headTop == null) {
                throw new AssertionError("Enderman upper head did not load");
            }
            for (var animation : List.of(Animations.SWORD_AUTO1, Animations.SWORD_AUTO2,
                    Animations.SWORD_AUTO3, Animations.BIPED_ROLL_FORWARD, Animations.BIPED_ROLL_BACKWARD)) {
                var clip = animation.get().getAnimationClip();
                if (clip.getClipTime() <= 0 || clip.getJointTransforms().isEmpty()) {
                    throw new AssertionError("Empty combat clip " + animation);
                }
                clip.getPoseInTime(clip.getClipTime() / 2);
            }
            System.out.println("Loaded and sampled three sword combo clips and both dodge clips");
        });
        long worldStart = System.nanoTime();
        System.out.println("FALA_WORLD_SMOKE creating flat integrated world");
        try (var world = context.worldBuilder().create()) {
            System.out.printf(Locale.ROOT, "FALA_WORLD_SMOKE world loaded in %.1f s%n",
                    (System.nanoTime() - worldStart) / 1_000_000_000.0);
            waitForTerrain(context);
            context.waitTicks(30);
            context.runOnClient(client -> {
                if (client.player == null || client.level == null || client.getSingleplayerServer() == null) {
                    throw new AssertionError("Expected a connected player in an integrated world");
                }
            });
            context.takeScreenshot("fala-singleplayer");
            System.out.println("Fala integrated world rendered with a connected player");
            if (Boolean.getBoolean("fala.test.bossRegressions")) {
                testBossRendering(context, world.getServer());
            }
        }
        if (Boolean.getBoolean("fala.test.dedicated")) {
            var properties = new Properties();
            properties.setProperty("server-ip", "127.0.0.1");
            try (var server = context.worldBuilder().createServer(properties); var connection = server.connect()) {
                waitForTerrain(context);
                context.waitTicks(30);
                context.runOnClient(client -> {
                    if (client.player == null || client.level == null || client.getSingleplayerServer() != null) {
                        throw new AssertionError("Expected a remote world connection");
                    }
                });
                context.takeScreenshot("fala-multiplayer");
                System.out.println("Fala dedicated world rendered with a connected client");
            }
        }
    }

    private static void testBossRendering(ClientGameTestContext context, TestServerContext server) {
        context.runOnClient(client -> {
            var player = client.player;
            client.level.addParticle(EpicFightParticles.DUST_CONTRACTIVE.get(),
                    player.getX() + 1, player.getY() + 1, player.getZ(), -.02, 0, 0);
        });
        context.waitTicks(8);
        System.out.println("FALA_BOSS_SMOKE dust_sprite PASS");

        server.runCommand("gamemode creative @a");
        server.runCommand("execute in minecraft:the_end run tp @a 0.5 76 13.5 180 0");
        context.waitFor(client -> client.level != null && client.level.dimension().equals(Level.END)
                && client.player != null && client.screen == null, 1600);
        server.runCommand("execute in minecraft:the_end run summon minecraft:ender_dragon 0.5 82 0.5 "
                + "{NoAI:1b,Tags:[\"fala_ik_probe\"]}");

        var landing = server.computeOnServer(instance -> {
            var end = instance.getLevel(Level.END);
            for (var entity : end.getAllEntities()) {
                if (entity instanceof EnderDragon dragon && entity.getTags().contains("fala_ik_probe")) {
                    dragon.getPhaseManager().setPhase(PatchedPhases.LANDING);
                    var target = dragon.getPhaseManager().getPhase(PatchedPhases.LANDING).getLandingPosition();
                    dragon.setPos(target.x, target.y + 1, target.z);
                    return new DragonLanding(dragon.getId(), target);
                }
            }
            throw new AssertionError("Expected a dragon for the landing regression");
        });
        server.runCommand(String.format(Locale.ROOT,
                "execute in minecraft:the_end run tp @a %.4f %.4f %.4f 180 0",
                landing.target().x, landing.target().y + 4, landing.target().z + 12));
        context.waitFor(client -> client.level != null && client.screen == null
                && client.level.getEntity(landing.entityId()) instanceof EnderDragon dragon
                && dragon.getPhaseManager().getCurrentPhase().getPhase() == PatchedPhases.LANDING
                && EpicFightCapabilities.getEntityPatch(dragon, EnderDragonPatch.class) != null, 400);
        System.out.println("FALA_BOSS_SMOKE landing entity and phase synchronized");
        context.runOnClient(client -> {
            var dragon = client.level.getEntity(landing.entityId());
            var patch = EpicFightCapabilities.getEntityPatch(dragon, EnderDragonPatch.class);
            var animator = patch.getClientAnimator();
            animator.playAnimationInstantly(Animations.DRAGON_FLY_TO_GROUND);
            // The simulator registers jobs during playback and activates them on its next tick.
            patch.getIKSimulator().tick(null);
            if (!patch.getIKSimulator().isRunning(Armatures.DRAGON.get().legFrontL3)) {
                throw new AssertionError("Landing clip did not activate front-left IK");
            }
            animator.getPose(0.5F);
        });
        context.waitTicks(10);
        System.out.println("FALA_BOSS_SMOKE dragon_landing_ik PASS");
    }

    private record DragonLanding(int entityId, Vec3 target) {}

    private static void waitForTerrain(ClientGameTestContext context) {
        context.waitFor(client -> client.screen == null && client.level != null && client.player != null
                && client.level.hasChunkAt(client.player.blockPosition()) && client.levelRenderer.countRenderedSections() > 0,
                2400);
    }
}
