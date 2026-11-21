package fala.bosstest;

import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import net.fabricmc.api.ModInitializer;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.animal.cow.Cow;
import net.minecraft.world.entity.boss.enderdragon.EndCrystal;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.boss.wither.WitherBoss;
import net.minecraft.world.level.Level;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.boss.WitherPatch;
import yesman.epicfight.world.capabilities.entitypatch.boss.enderdragon.EnderDragonPatch;
import yesman.epicfight.world.entity.WitherGhostClone;

public final class NaturalBossServer implements ModInitializer {
    private static final Map<String, String> LAST = new HashMap<>();
    private static UUID trackedDragon;
    private static boolean started;

    @Override
    public void onInitialize() {
        subscribe("net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents",
                "EndTick", "END_SERVER_TICK", value -> tick((MinecraftServer) value));
    }

    static void subscribe(String eventsName, String callbackName, String field, Consumer<Object> action) {
        try {
            Class<?> events = Class.forName(eventsName);
            Class<?> callback = Class.forName(eventsName + "$" + callbackName);
            Object listener = Proxy.newProxyInstance(callback.getClassLoader(), new Class<?>[]{callback},
                    (proxy, method, arguments) -> {
                        if (method.getDeclaringClass() == Object.class) {
                            return switch (method.getName()) {
                                case "hashCode" -> System.identityHashCode(proxy);
                                case "equals" -> proxy == arguments[0];
                                default -> eventsName;
                            };
                        }
                        action.accept(arguments[0]);
                        return null;
                    });
            Class.forName("net.fabricmc.fabric.api.event.Event").getMethod("register", Object.class)
                    .invoke(events.getField(field).get(null), listener);
        } catch (ReflectiveOperationException failure) {
            throw new IllegalStateException(failure);
        }
    }

    private static void tick(MinecraftServer server) {
        Path command = Path.of("fala-natural-command");
        try {
            if (Files.isRegularFile(command)) {
                String action = Files.readString(command).strip();
                Files.delete(command);
                act(server, action);
            }
            if (!started) {
                recordCombat(server);
                return;
            }
            var end = server.getLevel(Level.END);
            if (end == null) return;
            for (Entity entity : end.getAllEntities()) {
                if (entity instanceof EnderDragon dragon && dragon.getUUID().equals(trackedDragon)) {
                    EnderDragonPatch patch = EpicFightCapabilities.getEntityPatch(dragon, EnderDragonPatch.class);
                    record("dragon", dragon.getPhaseManager().getCurrentPhase().getPhase().toString(), server);
                    recordMotion("dragon", patch, server);
                    if (dragon.tickCount % 200 == 0) {
                        System.out.println("FALA_NATURAL server tick=" + server.getTickCount()
                                + " dragon progress pos=" + dragon.blockPosition()
                                + " health=" + dragon.getHealth() + " crystals=" + patch.getNearbyCrystals()
                                + " target=" + (dragon.getTarget() == null ? "none" : dragon.getTarget().getName().getString()));
                    }
                } else if (entity instanceof WitherBoss wither && wither.getTags().contains("fala_natural")) {
                    WitherPatch patch = EpicFightCapabilities.getEntityPatch(wither, WitherPatch.class);
                    record("wither armor", Boolean.toString(patch.isArmorActivated()), server);
                    record("wither ghost", Boolean.toString(patch.isGhost()), server);
                    recordMotion("wither", patch, server);
                    if (wither.isDeadOrDying()) record("wither death", "true", server);
                } else if (entity instanceof WitherGhostClone) {
                    record("wither clone", entity.getUUID().toString(), server);
                }
            }
        } catch (Throwable failure) {
            System.err.println("FALA_NATURAL ERROR " + failure);
            failure.printStackTrace();
            started = false;
        }
    }

    private static void recordCombat(MinecraftServer server) {
        var players = server.getPlayerList().getPlayers();
        if (players.isEmpty()) return;
        var patch = EpicFightCapabilities.getServerPlayerPatch(players.getFirst());
        if (patch != null) {
            var motion = patch.getAnimator().getPlayerFor(null).getRealAnimation().registryName();
            if (motion != null && (motion.getPath().contains("sword_auto") || motion.getPath().contains("roll_"))) {
                record("combat animation", motion.toString(), server);
            }
        }
        for (Entity entity : server.overworld().getAllEntities()) {
            if (entity instanceof Cow cow && cow.getTags().contains("fala_combat_target")) {
                record("combat target health", Float.toString(cow.getHealth()), server);
            }
        }
    }

    private static void recordMotion(String name,
            yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch<?> patch, MinecraftServer server) {
        if (patch == null) return;
        var id = patch.getAnimator().getPlayerFor(null).getRealAnimation().registryName();
        if (id != null) record(name + " animation", id.toString(), server);
    }

    private static void record(String key, String value, MinecraftServer server) {
        if (!value.equals(LAST.put(key, value))) {
            System.out.println("FALA_NATURAL server tick=" + server.getTickCount() + " " + key + " " + value);
        }
    }

    private static EnderDragon dragon(ServerLevel end) {
        if (trackedDragon != null && end.getEntity(trackedDragon) instanceof EnderDragon dragon) return dragon;
        UUID id = end.getDragonFight() == null ? null : end.getDragonFight().getDragonUUID();
        if (id != null && end.getEntity(id) instanceof EnderDragon dragon) return dragon;
        for (Entity entity : end.getAllEntities()) if (entity instanceof EnderDragon dragon) return dragon;
        throw new IllegalStateException("Waiting for the End fight dragon");
    }

    private static void act(MinecraftServer server, String action) {
        ServerLevel end = server.getLevel(Level.END);
        if (end == null) throw new IllegalStateException("The End is not available");
        ServerPlayer player = server.getPlayerList().getPlayers().getFirst();
        if (action.equals("start")) {
            EnderDragon dragon = dragon(end);
            trackedDragon = dragon.getUUID();
            dragon.getRandom().setSeed(20261121L);
            int kept = 0;
            for (Entity entity : end.getAllEntities()) {
                if (entity instanceof EndCrystal && kept++ >= 3) entity.discard();
            }
            started = true;
            System.out.println("FALA_NATURAL setup seed=20261121 crystalsKept=3 dragon=" + trackedDragon);
        } else if (action.equals("wound")) {
            EnderDragon dragon = dragon(end);
            float old = dragon.getHealth();
            boolean hurt = dragon.hurt(end, dragon.head, dragon.damageSources().playerAttack(player),
                    Math.max(1F, old - dragon.getMaxHealth() * .24F));
            System.out.println("FALA_NATURAL input dragon head damage accepted=" + hurt
                    + " health=" + old + "->" + dragon.getHealth());
        } else if (action.equals("interrupt")) {
            EnderDragon dragon = dragon(end);
            EnderDragonPatch patch = EpicFightCapabilities.getEntityPatch(dragon, EnderDragonPatch.class);
            float shield = patch.getStunShield();
            patch.damageStunShield(0, shield + 1);
            System.out.println("FALA_NATURAL input dragon stun impact=" + (shield + 1));
        } else if (action.equals("dragon-death")) {
            EnderDragon dragon = dragon(end);
            boolean hurt = dragon.hurt(end, dragon.head, dragon.damageSources().playerAttack(player), 10000F);
            System.out.println("FALA_NATURAL input lethal dragon head damage accepted=" + hurt);
        } else if (action.equals("wither-wound") || action.equals("wither-death")) {
            for (Entity entity : end.getAllEntities()) {
                if (!(entity instanceof WitherBoss wither) || !wither.getTags().contains("fala_natural")) continue;
                boolean hurt = wither.hurtServer(end, wither.damageSources().playerAttack(player),
                        action.equals("wither-death") ? 10000F : wither.getMaxHealth() * .56F);
                System.out.println("FALA_NATURAL input " + action + " accepted=" + hurt + " health=" + wither.getHealth());
            }
        } else {
            throw new IllegalArgumentException(action);
        }
        System.out.println("FALA_NATURAL command " + action + " complete");
    }
}
