package yesman.epicfight.client.renderer.shader.compute;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL15C;
import org.lwjgl.opengl.GL30C;
import org.lwjgl.opengl.GL43C;
import yesman.epicfight.client.renderer.shader.compute.backend.program.ComputeProgram;

/** Two joints, a transformed mesh part and two influences per vertex in production buffer order. */
final class SkinningInputs implements AutoCloseable {
    private static final int SSBO = GL43C.GL_SHADER_STORAGE_BUFFER;
    private static final int[] TEX_LIGHT = {0x12345678, 0x00400070};
    private final int[] buffers = new int[5];
    private final int midUv;
    private int output;

    SkinningInputs() {
        GL15C.glGenBuffers(buffers);
        // Part translation of -.25 combined with the .25 weighted joint translation cancels exactly.
        ByteBuffer poses = bytes(3 * 64);
        for (float x : new float[] {0, 1, -.25F}) {
            for (float component : new Matrix4f().translation(x, 0, 0).get(new float[16])) poses.putFloat(component);
        }
        upload(0, poses);
        ByteBuffer indices = bytes(3 * 8);
        ByteBuffer data = bytes(3 * 40);
        for (int i=0; i<3; i++) {
            indices.putInt(i).putInt(0);
            float x = new float[] {-.8F,.8F,0}[i], y = i==2 ? .8F : -.8F;
            data.putFloat(x).putFloat(y).putFloat(0).putFloat(0).putFloat(0).putFloat(1);
            data.putFloat(i==1 ? 1 : 0).putFloat(i==2 ? 1 : 0).putInt(0).putInt(2);
        }
        upload(1, indices);
        upload(2, data);
        upload(3, bytes(16).putInt(0).putFloat(.75F).putInt(1).putFloat(.25F));
        setHidden(false);
        midUv = GL15C.glGenBuffers();
        GL15C.glBindBuffer(SSBO, midUv);
        GL15C.glBufferData(SSBO, new float[] {1F/3,1F/3,1F/3,1F/3,1F/3,1F/3}, GL15C.GL_STATIC_DRAW);
    }

    int midUv() { return midUv; }

    void setHidden(boolean hidden) { upload(4, bytes(4).putInt(hidden ? 1 : 0)); }

    void dispatch(ComputeProgram program, int target, boolean iris, int channel) {
        output=target;
        for (int i=0; i<buffers.length; ++i) GL30C.glBindBufferBase(SSBO,i,buffers[i]);
        GL30C.glBindBufferBase(SSBO,5,target);
        program.useProgram();
        program.getUniform("model_view_matrix").uploadMatrix4f(new Matrix4f());
        program.getUniform("normal_matrix").uploadMatrix3f(new Matrix3f());
        program.getUniform("colorIn").uploadVec4(channel==0?1:0,channel==1?1:0,channel==2?1:0,1);
        program.getUniform("part_offset").uploadUnsignedInt(2);
        program.getUniform("uv1In").uploadUnsignedInt(TEX_LIGHT[0]);
        program.getUniform("uv2In").uploadUnsignedInt(TEX_LIGHT[1]);
        program.getUniform("falaIris").uploadUnsignedInt(iris?1:0);
        program.getUniform("entity_id_0").uploadUnsignedInt(0xabcd1234);
        program.getUniform("entity_id_1").uploadUnsignedInt(0x56780000);
        program.dispatch(1,1,1);
        program.memBarriers();
    }

    void verifyRecords(boolean iris, boolean hidden) {
        int stride=iris ? 60 : 48;
        ByteBuffer raw=bytes(3*stride);
        GL43C.glMemoryBarrier(GL43C.GL_BUFFER_UPDATE_BARRIER_BIT);
        GL15C.glBindBuffer(SSBO,output);
        GL15C.glGetBufferSubData(SSBO,0,raw);
        for (int i=0; i<3; ++i) {
            int p=i*stride;
            float expectedX=hidden?0:new float[] {-.8F,.8F,0}[i];
            float expectedY=hidden?0:(i==2?.8F:-.8F);
            if (Math.abs(raw.getFloat(p)-expectedX) > .00001F || Math.abs(raw.getFloat(p+4)-expectedY) > .00001F
                    || raw.getFloat(p+28)!=(i==1?1:0) || raw.getFloat(p+32)!=(i==2?1:0)
                    || raw.getInt(p+36)!=(hidden?0:0x007f0000)
                    || raw.getInt(p+40)!=TEX_LIGHT[0] || raw.getInt(p+44)!=TEX_LIGHT[1]) {
                throw new AssertionError("Skin, normal, UV, overlay or light record mismatch at " + i);
            }
            if (iris && (raw.getInt(p+48)!=0x1234abcd || raw.getInt(p+52)!=0x5678
                    || (!hidden && raw.getInt(p+56)!=0x7f00007f))) {
                throw new AssertionError("Iris ID or tangent record mismatch");
            }
        }
    }

    private static ByteBuffer bytes(int length) {
        return ByteBuffer.allocateDirect(length).order(ByteOrder.nativeOrder());
    }

    private void upload(int i, ByteBuffer data) {
        GL15C.glBindBuffer(SSBO,buffers[i]);
        GL15C.glBufferData(SSBO,data.flip(),GL15C.GL_STATIC_DRAW);
    }

    @Override public void close() {
        GL15C.glDeleteBuffers(buffers);
        GL15C.glDeleteBuffers(midUv);
    }
}
