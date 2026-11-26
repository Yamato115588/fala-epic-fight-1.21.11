import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Random;
import org.joml.Quaternionf;
import yesman.epicfight.api.animation.JointTransform;
import yesman.epicfight.api.animation.Keyframe;
import yesman.epicfight.api.animation.Pose;
import yesman.epicfight.api.animation.TransformSheet;
import yesman.epicfight.api.utils.math.Vec3f;

/** Exercise production keyframe sampling and two-joint pose blending with synthetic motion inputs. */
public final class AnimationScenario {
    private static final String[] JOINTS = {"Root", "Upper_Arm_R"};
    private static final float[] TIMES = {0.0F, 0.125F, 0.375F, 0.875F, 1.0F};
    private final MessageDigest digest = MessageDigest.getInstance("SHA-256");
    private final ByteBuffer buffer = ByteBuffer.allocate(Float.BYTES);

    private AnimationScenario() throws Exception { }

    private void add(float value) {
        if (!Float.isFinite(value)) throw new AssertionError("non-finite animation output");
        buffer.clear();
        buffer.putFloat(value);
        digest.update(buffer.array());
    }

    private void record(JointTransform transform) {
        Vec3f translation = transform.translation();
        Quaternionf rotation = transform.rotation();
        Vec3f scale = transform.scale();
        add(translation.x); add(translation.y); add(translation.z);
        add(rotation.x); add(rotation.y); add(rotation.z); add(rotation.w);
        add(scale.x); add(scale.y); add(scale.z);
    }

    private static TransformSheet makeSheet(Random input) {
        Keyframe[] frames = new Keyframe[TIMES.length];
        for (int i = 0; i < frames.length; i++) {
            Vec3f position = new Vec3f(input.nextFloat() - 0.5F, input.nextFloat(), input.nextFloat() * 4 - 2);
            Quaternionf rotation = new Quaternionf().rotationXYZ(input.nextFloat() * 5 - 2.5F,
                    input.nextFloat() * 4 - 2, input.nextFloat() * 6 - 3);
            Vec3f scale = new Vec3f(0.75F + input.nextFloat(), 0.75F + input.nextFloat(), 0.75F + input.nextFloat());
            frames[i] = new Keyframe(TIMES[i], new JointTransform(position, rotation, scale));
        }
        return new TransformSheet(frames);
    }

    private static Pose sample(TransformSheet root, TransformSheet arm, float time) {
        Pose pose = new Pose();
        pose.putJointData("Root", root.getInterpolatedTransform(time));
        pose.putJointData("Upper_Arm_R", arm.getInterpolatedTransform(time));
        return pose;
    }

    private void run() {
        Random input = new Random(12111016L);
        for (int clip = 0; clip < 64; clip++) {
            TransformSheet a = makeSheet(input), b = makeSheet(input);
            for (int frame = 0; frame <= 32; frame++) {
                float t = frame / 32F;
                Pose sampled = sample(a, b, t);
                Pose blended = Pose.interpolatePose(sampled, sample(b, a, 1 - t), (clip % 9) / 8F);
                for (String joint : JOINTS) {
                    if (!blended.hasTransform(joint)) throw new AssertionError("dropped " + joint);
                    record(sampled.get(joint));
                    record(blended.get(joint));
                }
            }
        }
        System.out.println("2112 animation samples " + HexFormat.of().formatHex(digest.digest()));
    }

    public static void main(String[] args) throws Exception {
        Path official = Path.of(args[0]);
        boolean expectOfficial = Boolean.parseBoolean(args[1]);
        for (Class<?> type : new Class<?>[]{JointTransform.class, Keyframe.class, TransformSheet.class, Pose.class}) {
            Path loadedFrom = Path.of(type.getProtectionDomain().getCodeSource().getLocation().toURI());
            if (Files.isSameFile(loadedFrom, official) != expectOfficial) {
                throw new AssertionError(type.getName() + " loaded from " + loadedFrom);
            }
        }
        new AnimationScenario().run();
    }
}
