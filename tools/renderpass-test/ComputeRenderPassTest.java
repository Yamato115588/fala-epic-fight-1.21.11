package yesman.epicfight.client.renderer.shader.compute;

import com.mojang.blaze3d.opengl.GlTexture;
import com.mojang.blaze3d.pipeline.RenderPipeline;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.platform.DepthTestFunction;
import com.mojang.blaze3d.shaders.ShaderType;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.client.renderer.rendertype.OutputTarget;
import net.minecraft.client.renderer.rendertype.RenderSetup;
import net.minecraft.client.renderer.rendertype.RenderType;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL;
import org.lwjgl.opengl.GL11C;
import org.lwjgl.opengl.GL15C;
import org.lwjgl.opengl.GL30C;
import org.lwjgl.opengl.GL32C;
import org.lwjgl.opengl.GL43C;
import org.lwjgl.system.Configuration;
import yesman.epicfight.client.renderer.shader.compute.backend.program.ComputeProgram;
import yesman.epicfight.client.renderer.shader.compute.backend.program.ComputeShader;

import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;

/** Isolated test of the production vertex packer and Minecraft's OpenGL command encoder. */
public final class ComputeRenderPassTest {
    private static final int SSBO = GL43C.GL_SHADER_STORAGE_BUFFER;
    private static final int WIDTH = 32;
    private static final String VERTEX = """
        #version 150
        in vec3 Position;
        in vec4 Color;
        out vec4 tint;
        void main() { gl_Position = vec4(Position, 1.0); tint = Color; }
        """;
    private static final String PIXEL = """
        #version 150
        in vec4 tint;
        out vec4 fragColor;
        void main() { fragColor = tint; }
        """;
    // Known triangle in the 48-byte vanilla skinning output layout.
    public static void main(String[] args) throws Exception {
        Configuration.OPENGL_EXPLICIT_INIT.set(true);
        if (Boolean.getBoolean("epicfight.test.osmesa")) GLFW.glfwInitHint(GLFW.GLFW_PLATFORM, GLFW.GLFW_PLATFORM_NULL);
        if (!GLFW.glfwInit()) throw new AssertionError("GLFW initialization failed");
        try {
            if (Boolean.getBoolean("epicfight.test.osmesa")) GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_CREATION_API, GLFW.GLFW_OSMESA_CONTEXT_API);
            GLFW.glfwWindowHint(GLFW.GLFW_VISIBLE, GLFW.GLFW_FALSE);
            GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 4);
            GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3);
            GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE);
            long window = GLFW.glfwCreateWindow(WIDTH, WIDTH, "Epic Fight RenderPass", 0, 0);
            if (window == 0) throw new AssertionError("OpenGL 4.3 context unavailable");
            try {
                GLFW.glfwMakeContextCurrent(window);
                GL.create(GLFW::glfwGetProcAddress);
                RenderSystem.initRenderThread();
                RenderSystem.initRenderer(window, 0, false,
                    (name, stage) -> stage == ShaderType.VERTEX ? VERTEX : PIXEL, false);
                run(Path.of(args[0]), Path.of(args[1]));
            } finally { GLFW.glfwDestroyWindow(window); }
        } finally { GLFW.glfwTerminate(); }
    }

    private static void run(Path packerPath, Path skinPath) throws Exception {
        TextureTarget target = new TextureTarget("pixel check", WIDTH, WIDTH, false);
        ComputeProgram packer = program(Files.readString(packerPath));
        ComputeProgram producer = program(Files.readString(skinPath));
        int source = GL15C.glGenBuffers();
        int sentinel = GL15C.glGenBuffers();
        int alignment = GL11C.glGetInteger(GL43C.GL_SHADER_STORAGE_BUFFER_OFFSET_ALIGNMENT);
        try (ComputeVertexBuffer vertices = new ComputeVertexBuffer(); SkinningInputs inputs = new SkinningInputs()) {
            GL15C.glBindBuffer(SSBO, source);
            GL15C.glBindBuffer(SSBO, sentinel);
            GL15C.glBufferData(SSBO, alignment + 64L, GL15C.GL_STATIC_DRAW);
            GL30C.glBindBufferRange(SSBO, 5, sentinel, alignment, 64L);
            GL15C.glBindBuffer(SSBO, source);
            var pipeline = RenderPipeline.builder().withLocation("test/compute")
                .withVertexShader("test/color").withFragmentShader("test/color")
                .withVertexFormat(DefaultVertexFormat.POSITION_COLOR, VertexFormat.Mode.TRIANGLES)
                .withDepthTestFunction(DepthTestFunction.NO_DEPTH_TEST).withDepthWrite(false).withCull(false).build();
            var setup = RenderSetup.builder(pipeline).setOutputTarget(new OutputTarget("test", () -> target)).createRenderSetup();
            RenderType type = RenderType.create("test", setup);
            for (int frame = 0; frame < 6; frame++) {
                int channel = frame % 3;
                boolean iris = frame >= 3;
                boolean hidden = frame == 4;
                if (frame == 4 || frame == 5) inputs.setHidden(hidden);
                int stride = iris ? 60 : 48;
                GL15C.glBindBuffer(SSBO,source);
                GL15C.glBufferData(SSBO,3L*stride,GL15C.GL_DYNAMIC_DRAW);
                RenderSystem.getDevice().createCommandEncoder().clearColorTexture(target.getColorTexture(), 0);
                vertices.draw(packer, type, source, stride, iris ? inputs.midUv() : 0, 3,
                    () -> inputs.dispatch(producer, source, iris, channel));
                int bound = GL30C.glGetIntegeri(GL43C.GL_SHADER_STORAGE_BUFFER_BINDING, 5);
                if (bound != sentinel || GL32C.glGetInteger64i(GL43C.GL_SHADER_STORAGE_BUFFER_START, 5) != alignment
                    || GL32C.glGetInteger64i(GL43C.GL_SHADER_STORAGE_BUFFER_SIZE, 5) != 64
                    || GL11C.glGetInteger(GL43C.GL_SHADER_STORAGE_BUFFER_BINDING) != source) {
                    throw new AssertionError("SSBO range or generic binding changed after frame " + frame);
                }
                inputs.verifyRecords(iris, hidden);
                ByteBuffer bytes = ByteBuffer.allocateDirect(WIDTH * WIDTH * 4);
                GL11C.glBindTexture(GL11C.GL_TEXTURE_2D, ((GlTexture) target.getColorTexture()).glId());
                GL11C.glGetTexImage(GL11C.GL_TEXTURE_2D, 0, GL11C.GL_RGBA, GL11C.GL_UNSIGNED_BYTE, bytes);
                int center = (WIDTH * (WIDTH / 2) + WIDTH / 2) * 4;
                for (int c = 0; c < 4; c++) {
                    int expected = !hidden && (c == channel || c == 3) ? 255 : 0;
                    if (Byte.toUnsignedInt(bytes.get(center + c)) != expected || bytes.get(c) != 0) {
                        throw new AssertionError("Unexpected pixel on frame " + frame + ", channel " + c);
                    }
                }
                if (GL11C.glGetError() != GL11C.GL_NO_ERROR) throw new AssertionError("OpenGL error on frame " + frame);
            }
            System.out.println("PASS: weighted skinning, Vanilla and Iris records, hidden triangles, six RenderPass readbacks and preserved SSBO range. " + GL11C.glGetString(GL11C.GL_RENDERER));
        } finally {
            GL15C.glDeleteBuffers(source);
            GL15C.glDeleteBuffers(sentinel);
            producer.delete();
            packer.delete();
            target.destroyBuffers();
        }
    }

    private static ComputeProgram program(String source) {
        ComputeShader shader = new ComputeShader();
        try {
            shader.setShaderSource(source);
            shader.compileShader();
            if (!shader.isCompiled()) throw new AssertionError(shader.getInfoLog());
            var program = new ComputeProgram(GL43C.GL_SHADER_STORAGE_BARRIER_BIT | GL43C.GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT);
            program.attachShader(shader);
            program.linkProgram();
            if (!program.isLinked()) throw new AssertionError(program.getInfoLog());
            return program;
        } finally { shader.delete(); }
    }
}
