package th.falasiayacraft.phone;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.client.Minecraft;
import net.minecraft.world.InteractionResult;

public final class PhoneClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        UseItemCallback.EVENT.register((player, level, hand) -> {
            if (!level.isClientSide() || !player.getItemInHand(hand).is(FalaPhone.PHONE)) return InteractionResult.PASS;
            Minecraft client = Minecraft.getInstance();
            client.setScreen(new PhoneScreen());
            return InteractionResult.SUCCESS;
        });
    }
}
