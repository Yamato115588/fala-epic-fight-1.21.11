package th.falasiayacraft.phone;

import net.fabricmc.api.ModInitializer;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;

public final class FalaPhone implements ModInitializer {
    public static final ResourceKey<Item> KEY = ResourceKey.create(Registries.ITEM, Identifier.fromNamespaceAndPath("fala_phone", "phone"));
    public static final Item PHONE = new Item(new Item.Properties().stacksTo(1).setId(KEY));

    @Override
    public void onInitialize() {
        Registry.register(BuiltInRegistries.ITEM, KEY, PHONE);
    }
}
