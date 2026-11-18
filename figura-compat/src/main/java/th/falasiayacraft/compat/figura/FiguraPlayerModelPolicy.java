package th.falasiayacraft.compat.figura;

import java.util.UUID;
import org.figuramc.figura.avatar.AvatarManager;
import yesman.epicfight.api.client.render.VanillaPlayerModelPolicy;

public final class FiguraPlayerModelPolicy implements VanillaPlayerModelPolicy {
    @Override
    public boolean keepVanillaModel(UUID playerId) {
        var avatar = AvatarManager.getLoadedAvatar(playerId);
        return avatar != null && avatar.loaded && avatar.renderer != null;
    }
}
