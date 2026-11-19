import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.DoubleTag;
import net.minecraft.nbt.IntTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.nbt.TagParser;
import org.joml.Matrix4f;
import yesman.epicfight.api.client.model.transformer.MeshVertex;
import yesman.epicfight.util.TagUtils;

public final class PortDataTest {
    public static void main(String[] args) throws Exception {
        ReplacementAssetTest.run(java.nio.file.Path.of(args[0]));
        CompoundTag saved = TagParser.parseCompoundFully("{skill:\"หลบ\",joints:[2,5],speed:1.5d}");
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        NbtIo.write(saved, new DataOutputStream(bytes));
        CompoundTag loaded = NbtIo.read(new DataInputStream(new ByteArrayInputStream(bytes.toByteArray())));
        check(saved.equals(loaded), "binary NBT round trip");
        ListTag joints = TagUtils.getTypedList(loaded, "joints", Tag.TAG_INT);
        check(TagUtils.intAt(joints, 0) == 2 && TagUtils.intAt(joints, 1) == 5, "joint order");
        joints.add(IntTag.valueOf(8));
        check(loaded.getListOrEmpty("joints").size() == 3, "typed list must be live");
        check(TagUtils.getTypedList(loaded, "joints", Tag.TAG_STRING).isEmpty(), "wrong list element type");
        check(TagUtils.getTypedList(loaded, "skill", Tag.TAG_STRING).isEmpty(), "wrong container type");
        ListTag missing = TagUtils.getTypedList(loaded, "absent", Tag.TAG_COMPOUND);
        missing.add(new CompoundTag());
        check(!loaded.contains("absent"), "missing list must stay detached");
        ListTag mixed = new ListTag();
        mixed.add(IntTag.valueOf(6));
        mixed.add(StringTag.valueOf("mixed"));
        loaded.put("heterogeneous", mixed);
        check(TagUtils.getTypedList(loaded, "heterogeneous", Tag.TAG_INT).isEmpty(), "mixed list rejection");
        check(TagUtils.containsType(loaded, "speed", 99) && !TagUtils.containsType(loaded, "skill", 99), "numeric wildcard");
        check(TagUtils.containsType(loaded, "absent", Tag.TAG_END) && !TagUtils.containsType(loaded, "absent", 99), "absent type");
        check(TagUtils.intAt(joints, -1) == 0 && TagUtils.doubleAt(joints, 0) == 0, "bounds and strict numeric types");
        ListTag decimals = new ListTag();
        decimals.add(DoubleTag.valueOf(2.25));
        check(TagUtils.doubleAt(decimals, 0) == 2.25 && TagUtils.intAt(decimals, 0) == 0, "double list");
        check(TagUtils.stringAt(mixed, 0).equals("6") && TagUtils.stringAt(mixed, 1).equals("mixed")
                && TagUtils.stringAt(mixed, mixed.size()).isEmpty(), "list text fallbacks");
        check(TagUtils.stringValue(StringTag.valueOf("หลบ \"เร็ว\"")).equals("หลบ \"เร็ว\""), "unquoted editor text");

        ModelPart.Vertex source = new ModelPart.Vertex(16, -8, 4, 0.25F, 0.75F);
        MeshVertex vertex = MeshVertex.transform(source, new Matrix4f().translation(5, 2, -1).scale(2));
        check(vertex.pos.x == 37 && vertex.pos.y == -14 && vertex.pos.z == 7, "model-space units and transform order");
        check(vertex.u == 0.25F && vertex.v == 0.75F, "UV preservation");
        MeshVertex.AnimatedVertex rigid = new MeshVertex.AnimatedVertex(vertex, 4);
        check(rigid.jointId.getX() == 4 && rigid.weight.x == 1 && rigid.weight.y == 0, "rigid vertex");
        MeshVertex.AnimatedVertex skinned = new MeshVertex.AnimatedVertex(vertex, 5, 3, 8, 0.5F, 0.375F, 0.125F);
        MeshVertex.AnimatedVertex cut = new MeshVertex.AnimatedVertex(skinned, 0.125F, 0.625F, skinned.jointId, skinned.weight);
        vertex.pos.zero();
        check(cut.pos.x == 37 && cut.u == 0.125F && cut.v == 0.625F, "clipping UVs and independent position");
        check(cut.jointId.getX() == 5 && cut.jointId.getY() == 3 && cut.jointId.getZ() == 8, "joint ordering");
        check(cut.weight.x == 0.5F && cut.weight.y == 0.375F && cut.weight.z == 0.125F, "skinning weights");
        System.out.println("PASS: binary NBT, typed list and editor behavior, model-space transform, UVs, joints and weights");
    }

    private static void check(boolean result, String message) {
        if (!result) throw new AssertionError(message);
    }
}
