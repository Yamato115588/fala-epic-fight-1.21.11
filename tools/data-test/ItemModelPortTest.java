package yesman.epicfight.client.model;

import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.client.renderer.block.model.BlockModel;
import net.minecraft.client.renderer.item.BlockModelWrapper;
import net.minecraft.client.renderer.item.ClientItem;
import net.minecraft.client.renderer.item.ItemModel;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.resources.model.UnbakedModel;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import yesman.epicfight.api.asset.AssetResourceSource;

public final class ItemModelPortTest {
    public static void run() throws Exception {
        net.minecraft.SharedConstants.tryDetectVersion();
        net.minecraft.server.Bootstrap.bootStrap();
        net.minecraft.client.renderer.item.ItemModels.bootstrap();
        var definition = separateModel();
        var base = definition.base();
        check(base.parent().equals(Identifier.withDefaultNamespace("item/generated")), "legacy parent");
        check(base.guiLight() == UnbakedModel.GuiLight.FRONT, "base inherited light");
        var gui = definition.perspectives().get(ItemDisplayContext.GUI);
        check(gui.guiLight() == UnbakedModel.GuiLight.SIDE && gui.transforms().getTransform(ItemDisplayContext.GUI).scale().x() == 2, "perspective properties");
        List<Identifier> parents = new ArrayList<>();
        definition.resolveDependencies(parents::add);
        check(parents.equals(List.of(Identifier.parse("minecraft:item/generated"), Identifier.parse("minecraft:item/handheld"))), "both perspectives discovered");
        List<String> selected = new ArrayList<>();
        ItemModel fallback = (state, stack, resolver, context, level, owner, seed) -> selected.add("base " + seed);
        ItemModel inventory = (state, stack, resolver, context, level, owner, seed) -> selected.add("gui " + seed);
        var baked = new SeparateTransformsBakedModel(fallback, Map.of(ItemDisplayContext.GUI, inventory));
        baked.update(new ItemStackRenderState(), ItemStack.EMPTY, null, ItemDisplayContext.GUI, null, null, 8);
        baked.update(new ItemStackRenderState(), ItemStack.EMPTY, null, ItemDisplayContext.FIRST_PERSON_RIGHT_HAND, null, null, 16);
        check(selected.equals(List.of("gui 8", "base 16")), "display context preserves render invocation");
        for (String icon : List.of("skillbook", "skillbook_dodge", "skillbook_passive", "skillbook_guard", "skillbook_mover", "skillbook_identity")) {
            try (var definitionReader = new InputStreamReader(AssetResourceSource.open(null, Identifier.parse("epicfight:items/" + icon + ".json")), StandardCharsets.UTF_8);
                 var modelReader = new InputStreamReader(AssetResourceSource.open(null, Identifier.parse("epicfight:models/item/" + icon + ".json")), StandardCharsets.UTF_8)) {
                var book = ClientItem.CODEC.parse(JsonOps.INSTANCE, JsonParser.parseReader(definitionReader)).getOrThrow();
                check(book.model() instanceof BlockModelWrapper.Unbaked wrapper && wrapper.model().equals(Identifier.parse("epicfight:item/" + icon)), "book model binding " + icon);
                check(BlockModel.fromStream(modelReader).parent().equals(Identifier.parse("minecraft:item/generated")), "book geometry " + icon);
            }
        }
        System.out.println("PASS: Minecraft item models decode six original skill books and preserve legacy display-context dispatch");
    }

    private static SeparateTransformsUnbakedModel separateModel() {
        var sample = JsonParser.parseString("""
            {"loader":"neoforge:separate_transforms","gui_light":"front",
              "base":{"parent":"minecraft:item/generated"},
              "perspectives":{"gui":{"gui_light":"side","parent":"minecraft:item/handheld",
                "display":{"gui":{"scale":[2,2,2]}}}}}
            """).getAsJsonObject();
        return SeparateTransformsUnbakedModel.parse(Identifier.parse("epicfight:test_item"), sample);
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
