package fala.tests;

import java.util.List;
import java.util.Properties;
import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.minecraft.data.AtlasIds;
import yesman.epicfight.api.client.model.Meshes;
import yesman.epicfight.gameasset.Armatures;
import yesman.epicfight.gameasset.Animations;

public final class PortWorldTest implements FabricClientGameTest {
    @Override
    public void runTest(ClientGameTestContext context) {
        context.runOnClient(client -> {
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
        try (var world = context.worldBuilder().create()) {
            waitForTerrain(context);
            context.waitTicks(30);
            context.runOnClient(client -> {
                if (client.player == null || client.level == null || client.getSingleplayerServer() == null) {
                    throw new AssertionError("Expected a connected player in an integrated world");
                }
            });
            context.takeScreenshot("fala-singleplayer");
            System.out.println("Fala integrated world rendered with a connected player");
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

    private static void waitForTerrain(ClientGameTestContext context) {
        context.waitFor(client -> client.screen == null && client.level != null && client.player != null
                && client.level.hasChunkAt(client.player.blockPosition()) && client.levelRenderer.countRenderedSections() > 0,
                2400);
    }
}
