package yesman.epicfight.client.particle;

import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.ByteBufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.MeshData;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.blaze3d.vertex.VertexFormatElement;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.List;
import java.util.Map;
import net.minecraft.client.renderer.SubmitNodeStorage;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.resources.Identifier;

public final class TrailGeometryTest {
    public static void run() throws ReflectiveOperationException {
        int light = 0x00d000e0;
        TrailGeometry ribbon = new TrailGeometry(Identifier.parse("test:ribbon"), 4, light);
        for (int i = 0; i < 4; i++) {
            ribbon.add(i, -i, i * 2, i / 4.0F, 1 - i / 4.0F, 0x80204080 + i);
        }
        SubmitNodeStorage collector = new SubmitNodeStorage();
        ribbon.submit(collector, new PoseStack());
        var submissions = collector.order(0).getCustomGeometrySubmits();
        var field = submissions.getClass().getDeclaredField("customGeometrySubmits");
        field.setAccessible(true);
        @SuppressWarnings("unchecked")
        var batches = (Map<RenderType, List<SubmitNodeStorage.CustomGeometrySubmit>>)field.get(submissions);
        check(batches.size() == 1, "one particle batch");
        var batch = batches.entrySet().iterator().next();
        var type = batch.getKey();
        check(type.format() == DefaultVertexFormat.PARTICLE && type.mode() == VertexFormat.Mode.QUADS, "particle format and primitive");
        check(!type.pipeline().isWriteDepth() && !type.pipeline().isCull(), "translucent double-sided ribbon");
        check(batch.getValue().size() == 1, "one extracted strip");
        var strip = batch.getValue().getFirst();
        var format = type.format();
        try (var arena = new ByteBufferBuilder(256)) {
            var builder = new BufferBuilder(arena, type.mode(), format);
            strip.customGeometryRenderer().render(strip.pose(), builder);
            try (MeshData mesh = builder.buildOrThrow()) {
                check(mesh.drawState().vertexCount() == 4 && mesh.drawState().indexCount() == 6, "quad triangulation");
                ByteBuffer bytes = mesh.vertexBuffer().order(ByteOrder.nativeOrder());
                for (int i = 0; i < 4; i++) {
                    int base = i * format.getVertexSize();
                    int xyz = base + format.getOffset(VertexFormatElement.POSITION);
                    check(bytes.getFloat(xyz) == i && bytes.getFloat(xyz + 4) == -i && bytes.getFloat(xyz + 8) == i * 2, "position");
                    int uv = base + format.getOffset(VertexFormatElement.UV0);
                    check(bytes.getFloat(uv) == i / 4.0F && bytes.getFloat(uv + 4) == 1 - i / 4.0F, "UV");
                    int rgba = base + format.getOffset(VertexFormatElement.COLOR);
                    check(bytes.get(rgba) == 32 && bytes.get(rgba + 1) == 64 && Byte.toUnsignedInt(bytes.get(rgba + 2)) == 128 + i
                            && Byte.toUnsignedInt(bytes.get(rgba + 3)) == 128, "ordered vertex color and opacity");
                    check(bytes.getInt(base + format.getOffset(VertexFormatElement.UV2)) == light, "packed block and sky light");
                }
            }
        }
        System.out.println("PASS: weapon trail extracted into Minecraft SubmitNodeStorage, four particle vertices and six indices");
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
