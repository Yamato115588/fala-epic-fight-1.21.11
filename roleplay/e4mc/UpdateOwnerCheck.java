import static org.objectweb.asm.Opcodes.*;
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.nio.file.*;

/** Adapts one dedicated-server level-four check to the native 1.21.11 owner check. */
public final class UpdateOwnerCheck {
    public static void main(String[] args) throws Exception {
        ClassNode cls = new ClassNode();
        ClassReader source = new ClassReader(Files.readAllBytes(Path.of(args[0])));
        source.accept(cls, 0);
        int edits = 0;
        for (MethodNode method : cls.methods) {
            if (!method.name.equals("lambda$registerCommands$0") || !method.desc.equals("(Lnet/minecraft/class_2168;)Z")) continue;
            for (AbstractInsnNode insn : method.instructions.toArray()) {
                if (!(insn instanceof MethodInsnNode call) || call.getOpcode()!=INVOKEVIRTUAL ||
                    !call.owner.equals("net/minecraft/class_2168") || !call.name.equals("method_9259") || !call.desc.equals("(I)Z")) continue;
                AbstractInsnNode level = call.getPrevious();
                if (level.getOpcode()!=ICONST_4) throw new IllegalStateException("Expected owner level four");
                method.instructions.remove(level);
                InsnList mapped = new InsnList();
                // Commands.LEVEL_OWNERS.check(source.permissions()). Keep the existing integrated-host check.
                mapped.add(new MethodInsnNode(INVOKEVIRTUAL, "net/minecraft/class_2168", "method_75037", "()Lnet/minecraft/class_12096;", false));
                mapped.add(new FieldInsnNode(GETSTATIC, "net/minecraft/class_2170", "field_31841", "Lnet/minecraft/class_12090;"));
                mapped.add(new InsnNode(SWAP));
                mapped.add(new MethodInsnNode(INVOKEINTERFACE, "net/minecraft/class_12090", "method_75022", "(Lnet/minecraft/class_12096;)Z", true));
                method.instructions.insertBefore(call,mapped);
                method.instructions.remove(call);
                edits++;
            }
        }
        if(edits!=1) throw new IllegalStateException("Unexpected e4mc source version");
        ClassWriter output=new ClassWriter(source,ClassWriter.COMPUTE_MAXS);
        cls.accept(output);
        Files.write(Path.of(args[1]),output.toByteArray());
    }
}
