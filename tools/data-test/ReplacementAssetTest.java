import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.PackLocationInfo;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.PathPackResources;
import net.minecraft.server.packs.repository.PackSource;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceProvider;
import yesman.epicfight.api.asset.AssetResourceSource;

final class ReplacementAssetTest {
    static void run(Path directory) throws Exception {
        String base = "animmodels/";
        var model = Identifier.fromNamespaceAndPath("epicfight", base + "entity/biped.json");
        var manifest = object(ReplacementAssetTest.class.getResourceAsStream("/META-INF/fala-replacement-assets/manifest.json").readAllBytes());
        check(manifest.get("license").getAsString().equals("CC0-1.0"), "asset license");
        var hashes = manifest.getAsJsonObject("sha256");
        var packInfo = new PackLocationInfo("fala-assets", Component.literal("Fala"), PackSource.DEFAULT, Optional.empty());
        try (var pack = new PathPackResources(packInfo, directory)) {
            for (var item : hashes.entrySet()) {
                String[] parts = item.getKey().split("/",3);
                Identifier id = Identifier.fromNamespaceAndPath(parts[1], parts[2]);
                var input = pack.getResource(PackType.CLIENT_RESOURCES,id);
                check(input != null, "missing pack entry " + id);
                ResourceProvider provider = ResourceProvider.fromMap(Map.of(id,new Resource(pack,input)));
                try (var bundled = AssetResourceSource.open(null,id); var packed = AssetResourceSource.open(provider,id)) {
                    byte[] bytes = bundled.readAllBytes();
                    check(Arrays.equals(bytes,packed.readAllBytes()), "pack/classpath bytes " + id);
                    check(HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes))
                            .equals(item.getValue().getAsString()), "digest " + id);
                }
            }
            var other = Identifier.fromNamespaceAndPath("epicfight", base+"entity/biped_slim_arm.json");
            var replacement = new Resource(pack,pack.getResource(PackType.CLIENT_RESOURCES,other));
            try (var overridden = AssetResourceSource.open(ResourceProvider.fromMap(Map.of(model,replacement)),model);
                 var slim = AssetResourceSource.open(null,other); var regular = AssetResourceSource.open(null,model)) {
                byte[] bytes = overridden.readAllBytes();
                check(Arrays.equals(bytes,slim.readAllBytes()) && !Arrays.equals(bytes,regular.readAllBytes()), "pack override order");
            }
        }
        try {
            AssetResourceSource.open(null,Identifier.fromNamespaceAndPath("fala_epicfight","absent.json"));
            throw new AssertionError("missing asset");
        } catch (FileNotFoundException expected) { }
        JsonObject player = read("entity/biped");
        JsonArray joints = player.getAsJsonObject("armature").getAsJsonArray("joints");
        String[] armorOrder = {"Root","Thigh_R","Leg_R","Knee_R","Thigh_L","Leg_L","Knee_L","Torso","Chest","Head",
                "Shoulder_R","Arm_R","Hand_R","Tool_R","Elbow_R","Shoulder_L","Arm_L","Hand_L","Tool_L","Elbow_L"};
        for (int i=0; i<armorOrder.length; i++) check(joints.get(i).getAsString().equals(armorOrder[i]),"armor joint " + i);
        Set<String> names = new HashSet<>();
        gather(player.getAsJsonObject("armature").getAsJsonArray("hierarchy").get(0).getAsJsonObject(),names);
        check(names.size()==joints.size() && names.containsAll(Set.of("Root","Tool_R","Tool_L","Head")), "skeleton hierarchy");
        var vertices=player.getAsJsonObject("vertices");
        int count=array(vertices,"positions").size()/3;
        check(array(vertices,"vcounts").size()==count && array(vertices,"vindices").size()==2*count,"joint influences");
        int uvCount=array(vertices,"uvs").size()/2, normalCount=array(vertices,"normals").size()/3;
        for (int i=0; i<count; ++i) {
            int joint=array(vertices,"vindices").get(2*i).getAsInt();
            check(joint>=0 && joint<joints.size() && array(vertices,"vcounts").get(i).getAsInt()==1,"weighted vertex");
        }
        var parts=vertices.getAsJsonObject("parts");
        check(parts.size()==12,"base and skin layers");
        for (String name:parts.keySet()) {
            var indices=array(parts,name);
            check(indices.size()>0 && indices.size()%9==0,"triangle topology");
            for (int i=0;i<indices.size();i+=3) {
                check(indices.get(i).getAsInt()<count && indices.get(i+1).getAsInt()<uvCount
                      && indices.get(i+2).getAsInt()<normalCount,"position, UV and normal indices");
            }
        }
        for (String clip : new String[]{"living/idle","combat/sword_auto1","combat/sword_auto2","combat/sword_auto3","skill/roll_forward","skill/roll_backward"}) {
            JsonArray tracks=read("animations/biped/"+clip).getAsJsonArray("animation");
            boolean hasMovement=false;
            for (var element:tracks) {
                var t=element.getAsJsonObject(); String name=t.get("name").getAsString();
                check(names.contains(name) || name.equals("Coord"),"clip joint "+name);
                var times=t.getAsJsonArray("time"); var frames=t.getAsJsonArray("transform");
                check(times.size()==frames.size() && times.size()>1,"keyframe count");
                double previous=-1;
                for (int i=0;i<times.size();i++) {
                    double time=times.get(i).getAsDouble();
                    check(time>previous,"timestamp order"); previous=time;
                    var q=frames.get(i).getAsJsonObject().getAsJsonArray("rot");
                    double norm=0; for (var axis:q) norm+=Math.pow(axis.getAsDouble(),2);
                    check(Math.abs(norm-1)<.00001,"unit rotation");
                    if (!frames.get(i).equals(frames.get(0))) hasMovement=true;
                }
                if (name.equals("Coord")) {
                    double z=frames.get(frames.size()-1).getAsJsonObject().getAsJsonArray("loc").get(2).getAsDouble();
                    check(clip.endsWith("forward") ? z>1 : z< -1,"directional dodge displacement");
                }
            }
            check(hasMovement,"animated joints for "+clip);
        }
        System.out.println("PASS: nine licensed resources, pack override and bundled lookup, skeleton, skin layers and six original motion clips");
    }
    private static JsonArray array(JsonObject object,String name) {
        return object.getAsJsonObject(name).getAsJsonArray("array");
    }
    private static void gather(JsonObject node,Set<String> seen) {
        check(seen.add(node.get("name").getAsString()),"duplicate joint");
        check(node.getAsJsonArray("transform").size()==16,"rest transform");
        for (var child:node.getAsJsonArray("children")) gather(child.getAsJsonObject(),seen);
    }
    private static JsonObject read(String asset) throws Exception {
        try (InputStream input=AssetResourceSource.open(null,Identifier.fromNamespaceAndPath("epicfight","animmodels/"+asset+".json"))) {
            return object(input.readAllBytes());
        }
    }
    private static JsonObject object(byte[] bytes) {
        return JsonParser.parseString(new String(bytes,StandardCharsets.UTF_8)).getAsJsonObject();
    }
    private static void check(boolean ok,String message) {
        if (!ok) throw new AssertionError(message);
    }
}
