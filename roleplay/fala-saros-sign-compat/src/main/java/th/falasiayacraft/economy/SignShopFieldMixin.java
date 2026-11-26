package th.falasiayacraft.economy;

import net.fabricmc.loader.api.FabricLoader;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;

/** Keep Saros' own sign creation and trade logic, resolving its field in the active namespace. */
@Mixin(targets = "de.sarocesch.sarosmoneymod.listener.SignShopListenerFabric", remap = false)
abstract class SignShopFieldMixin {
    @ModifyConstant(method = "initSignField", constant = @Constant(stringValue = "blockEntity"), require = 1)
    private static String fala$mapSignField(String original) {
        return FabricLoader.getInstance().getMappingResolver().mapFieldName(
            "intermediary", "net.minecraft.class_7743", "field_40424", "Lnet/minecraft/class_2625;");
    }
}
