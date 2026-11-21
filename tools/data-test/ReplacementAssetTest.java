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
import java.util.List;
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
        check(hashes.size() == 322, "expected independent asset inventory");
        var sweepingEdge = "textures/gui/skills/weapon_innate/sweeping_edge.png";
        check(hashes.has("assets/epicfight/" + sweepingEdge), "Sweeping Edge HUD icon inventory");
        try (var stream = AssetResourceSource.open(null, Identifier.fromNamespaceAndPath("epicfight", sweepingEdge))) {
            var icon = javax.imageio.ImageIO.read(stream);
            check(icon != null && icon.getWidth() == 32 && icon.getHeight() == 32, "Sweeping Edge HUD icon size");
        }
        checkMobMotions(hashes);
        checkSounds();
        checkParticleAtlases();
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
        for (String mob : List.of("enderman", "creeper", "skeleton", "spider", "iron_golem", "ravager",
                "vex", "piglin", "hoglin", "dragon", "wither", "biped_old_texture", "biped_outlayer",
                "zombie_villager", "illager", "witch")) {
            var modelData = read("entity/" + mob);
            var armature = modelData.getAsJsonObject("armature");
            Set<String> hierarchy = new HashSet<>();
            gather(armature.getAsJsonArray("hierarchy").get(0).getAsJsonObject(), hierarchy);
            var jointNames = armature.getAsJsonArray("joints");
            check(hierarchy.size() == jointNames.size(), mob + " joint count");
            for (var joint : jointNames) check(hierarchy.contains(joint.getAsString()), mob + " joint");
            var geometry = modelData.getAsJsonObject("vertices");
            check(array(geometry, "vindices").size() == array(geometry, "positions").size()/3*2, mob + " weights");
            for (var uv : array(geometry, "uvs")) {
                check(uv.getAsDouble() >= 0 && uv.getAsDouble() <= 1, mob + " UV range");
            }
            if (mob.equals("enderman")) {
                check(hierarchy.contains("Head_Top"), "Enderman jaw joint");
                check(geometry.getAsJsonObject("parts").keySet().equals(Set.of("headTop","headBottom",
                        "torso","leftArm","rightArm","leftLeg","rightLeg")), "Enderman mesh parts");
                for (String motion : List.of("idle", "walk", "rage_idle", "rage_walk", "hit_short", "hit_long",
                        "neutralized", "convert_rage", "tp_kick1", "tp_kick2", "rush_kick", "jump_kick",
                        "knee", "kick_twice", "grasp", "teleport", "death")) {
                    var tracks = read("animations/enderman/" + motion).getAsJsonArray("animation");
                    check(!tracks.isEmpty(), "Enderman tracks: " + motion);
                    for (var element : tracks) {
                        var channel = element.getAsJsonObject();
                        check(hierarchy.contains(channel.get("name").getAsString()), "Enderman joint: " + motion);
                        var times = channel.getAsJsonArray("time");
                        check(times.size() > 1 && times.size() == channel.getAsJsonArray("transform").size(),
                                "Enderman keyframes: " + motion);
                        for (int i = 1; i < times.size(); i++) {
                            check(times.get(i).getAsDouble() > times.get(i - 1).getAsDouble(), "Enderman timing: " + motion);
                        }
                    }
                }
            }
        }
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
        for (String clip : new String[]{"living/equip_item","living/fall","living/idle","living/walk","living/run","skill/guard_sword","skill/step_forward","skill/step_backward","skill/step_left","skill/step_right","combat/sword_auto1","combat/sword_auto2","combat/sword_auto3","skill/roll_forward","skill/roll_backward"}) {
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
                    var origin=frames.get(0).getAsJsonObject().getAsJsonArray("loc");
                    var loc=frames.get(frames.size()-1).getAsJsonObject().getAsJsonArray("loc");
                    boolean lateral = clip.endsWith("left") || clip.endsWith("right");
                    int axis = lateral ? 0 : 2;
                    double along = origin.get(axis).getAsDouble() - loc.get(axis).getAsDouble();
                    check(loc.get(lateral ? 2 : 0).getAsDouble() == 0 &&
                          ((clip.endsWith("forward") || clip.endsWith("left")) ? along > 1 : along < -1), "directional dodge " + clip);
                }
            }
            check(hasMovement,"animated joints for "+clip);
        }
        try (var stream = AssetResourceSource.open(null, Identifier.parse("epicfight:textures/particle/swing_trail.png"))) {
            var mask = javax.imageio.ImageIO.read(stream);
            check(mask.getWidth() == 64 && mask.getHeight() == 32, "ribbon mask dimensions");
            check((mask.getRGB(40, 0) >>> 24) == 0 && (mask.getRGB(0, 16) >>> 24) == 0
                   && (mask.getRGB(63, 16) >>> 24) > 240, "ribbon edge and sweep direction");
        }
        for (String effect : List.of("air_burst", "force_field", "laser")) {
            var mesh = read("particle/" + effect).getAsJsonObject("vertices");
            int size = array(mesh, "positions").size() / 3;
            var indices = array(mesh, "indices");
            check(size >= 24 && size == array(mesh, "normals").size() / 3 && size == array(mesh, "uvs").size() / 2,
                   "surface and basis " + effect);
            check(indices.size() > 0 && indices.size() % 9 == 0, "triangulated particle " + effect);
            for (var index : indices) check(index.getAsInt() >= 0 && index.getAsInt() < size, "particle index " + effect);
        }
        System.out.println("PASS: " + hashes.size() + " CC0 resources, pack override and bundled lookup, player rigs, 15 motions and ribbon texture");
    }
    private static void checkMobMotions(JsonObject hashes) throws Exception {
        Map<String, String> rigs = Map.ofEntries(Map.entry("zombie", "biped"), Map.entry("wither_skeleton", "skeleton"),
                Map.entry("illager", "biped"), Map.entry("witch", "biped"), Map.entry("piglin", "piglin"),
                Map.entry("hoglin", "hoglin"), Map.entry("ravager", "ravager"), Map.entry("spider", "spider"),
                Map.entry("iron_golem", "iron_golem"), Map.entry("creeper", "creeper"), Map.entry("vex", "vex"),
                Map.entry("wither", "wither"), Map.entry("dragon", "dragon"), Map.entry("enderman", "enderman"));
        int checked = 0;
        for (var rig : rigs.entrySet()) {
            var joints = read("entity/" + rig.getValue()).getAsJsonObject("armature").getAsJsonArray("joints");
            Set<String> names = new HashSet<>(Set.of("Coord"));
            for (var joint : joints) names.add(joint.getAsString());
            String prefix = "assets/epicfight/animmodels/animations/" + rig.getKey() + "/";
            for (String path : hashes.keySet()) {
                if (!path.startsWith(prefix)) continue;
                String name = path.substring("assets/epicfight/animmodels/".length(), path.length() - ".json".length());
                var channels = read(name).getAsJsonArray("animation");
                check(!channels.isEmpty(), "empty animation " + name);
                Set<String> seen = new HashSet<>();
                boolean moving = false;
                for (var element : channels) {
                    var channel = element.getAsJsonObject();
                    String joint = channel.get("name").getAsString();
                    check(names.contains(joint) && seen.add(joint), "invalid joint " + joint + " in " + name);
                    var times = channel.getAsJsonArray("time");
                    var keys = channel.getAsJsonArray("transform");
                    check(times.size() == keys.size() && times.size() >= 2 && times.get(0).getAsDouble() == 0, "timeline " + name);
                    for (int i = 1; i < keys.size(); i++) {
                        check(times.get(i).getAsDouble() > times.get(i - 1).getAsDouble(), "timestamp order " + name);
                        moving |= !keys.get(i).equals(keys.get(0));
                    }
                }
                check(moving, "unanimated mob motion " + name);
                checked++;
            }
        }
        check(checked == 114, "registered mob motion coverage");
    }

    private static void checkParticleAtlases() throws Exception {
        for (String particle : List.of("enderman_death_emit", "hit_blunt", "cut", "dust_normal",
                "dust_expansive", "dust_contractive", "blood", "blade_rush", "breath_flame",
                "tsunami_splash", "feather", "ash_directional", "catharsis")) {
            var id = Identifier.parse("epicfight:particles/" + particle + ".json");
            try (var input = AssetResourceSource.open(null, id)) {
                var textures = object(input.readAllBytes()).getAsJsonArray("textures");
                check(!textures.isEmpty(), "SpriteSet manifest " + particle);
                for (var name : textures) Identifier.parse(name.getAsString());
            }
        }
    }

    private static void checkSounds() throws Exception {
        try (var input = AssetResourceSource.open(null, Identifier.parse("epicfight:sounds.json"))) {
            var events = object(input.readAllBytes());
            check(events.size() == 43, "registered sound event coverage");
            for (var event : events.entrySet()) {
                var sounds = event.getValue().getAsJsonObject().getAsJsonArray("sounds");
                check(sounds.size() == 1, "sound alias " + event.getKey());
                if (event.getKey().equals("sfx.no_sound")) {
                    check(sounds.get(0).getAsString().equals("epicfight:compat/silence"), "silent event");
                    continue;
                }
                var alias = sounds.get(0).getAsJsonObject();
                check(alias.get("name").getAsString().startsWith("minecraft:")
                        && alias.get("type").getAsString().equals("event")
                        && alias.get("volume").getAsDouble() > 0 && alias.get("pitch").getAsDouble() > 0,
                        "in-game audio reference " + event.getKey());
            }
        }
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
