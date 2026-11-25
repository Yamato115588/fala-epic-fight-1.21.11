import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Random;
import yesman.epicfight.api.utils.math.OpenMatrix4f;
import yesman.epicfight.api.utils.math.Vec3f;

/** Identical motion inputs run once against the official reference and once against target bytecode. */
public class MatrixScenario {
    public static void main(String[] args) throws Exception {
        Random input = new Random(73151411L);
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        ByteBuffer bytes = ByteBuffer.allocate(12);
        for (int i = 0; i < 4096; i++) {
            OpenMatrix4f pose = new OpenMatrix4f();
            pose.translate(input.nextFloat() * 8 - 4, input.nextFloat(), input.nextFloat() * 8 - 4);
            pose.rotate(input.nextFloat() * 6 - 3, Vec3f.Y_AXIS);
            pose.rotate(input.nextFloat() * 2 - 1, Vec3f.X_AXIS);
            pose.scale(0.5F + input.nextFloat(), 0.5F + input.nextFloat(), 0.5F + input.nextFloat());
            Vec3f point = new Vec3f(input.nextFloat(), input.nextFloat(), input.nextFloat());
            Vec3f transformed = OpenMatrix4f.transform3v(pose, point, null);
            Vec3f recovered = OpenMatrix4f.transform3v(OpenMatrix4f.invert(pose, null), transformed, null);
            if (!(Math.abs(recovered.x - point.x) < 0.00002F && Math.abs(recovered.y - point.y) < 0.00002F
                    && Math.abs(recovered.z - point.z) < 0.00002F)) throw new AssertionError("inverse mismatch " + i);
            bytes.clear();
            bytes.putFloat(transformed.x).putFloat(transformed.y).putFloat(transformed.z);
            digest.update(bytes.array());
        }
        System.out.println("4096 poses " + HexFormat.of().formatHex(digest.digest()));
    }
}
