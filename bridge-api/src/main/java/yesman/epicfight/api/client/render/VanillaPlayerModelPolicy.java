package yesman.epicfight.api.client.render;

import java.util.UUID;

/** A client mod can keep Minecraft's player renderer for selected players. */
@FunctionalInterface
public interface VanillaPlayerModelPolicy {
    String ENTRYPOINT = "epicfight:fala_vanilla_player_model";

    boolean keepVanillaModel(UUID playerId);
}
