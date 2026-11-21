# Boss lifecycle test

This Linux test runs the production Epic Fight JAR with the pinned Fala Lite pack, a dedicated server bound to 127.0.0.1 and two clients. It records AI-selected dragon and Wither phases, animations, IK, dust particle creation and sound events. X11 input on the first client drives an iron sword combo and forward roll. The server verifies the three attacks and the target's loss of health.

The scenario uses a fixed world seed, retains three currently loaded End crystals, seeds the dragon RNG, applies ordinary player head damage to cross health thresholds, and calls the production stun-impact API to exercise interruption. Test players receive resistance and regeneration. The probe never selects a boss phase or starts a boss animation. These controlled inputs test lifecycle transitions and synchronization.

Authenticated multiplayer and a manual survival playthrough need their own results. The runner creates a loopback-only offline test server and requires a previously accepted EULA file.

## Compile the probe

From the prepared port workspace with JDK 21, use the source repository path.

```sh
./gradlew -I "$repo/tools/boss-test/boss.gradle" remapBossProbeJar
```

The probe is written to `build/boss-probe/natural-boss-probe.jar`. Use the production JAR produced by `clean build`.

## Run

Use a new output directory and install Xvfb, libX11 and libXtst. Minecraft, Fabric and their libraries must already be downloaded. The mod cache contains the 24 Fala Lite JARs. The runner verifies both the pack index hashes and the repository's SHA-256 manifests before launch.

```sh
python3 "$repo/tools/boss-test/run.py" \
  --jar "/absolute/path/Epic Fight-21.17.3-fala.2+mc1.21.11.jar" \
  --probe "/absolute/path/build/boss-probe/natural-boss-probe.jar" \
  --pack "/absolute/path/Fala-Lite.mrpack" \
  --mod-cache "/absolute/path/lite-jars" \
  --eula-file "/absolute/path/authorized-test-server/eula.txt" \
  --output "/absolute/path/new-natural-boss-test" \
  --game-cache "/absolute/path/minecraft-cache" \
  --game-libs "/absolute/path/minecraft-libraries" \
  --loader-libs "/absolute/path/fabric-libraries" \
  --loader-json "/absolute/path/fabric-loader-profile.json" \
  --assets "/absolute/path/minecraft-assets" \
  --java "/absolute/path/jdk-21/bin/java" \
  --xvfb "/usr/bin/Xvfb"
```

`game-cache` contains `minecraft-client.jar`, `minecraft-server.jar` and `mojang_minecraft_info.json`. `loader-json` is the Fabric Loader 0.19.3 profile with its Maven library list. `loader-libs` is a flat cache of those JARs. `game-libs` is a flat cache of the Minecraft manifest's Linux libraries and native JARs. If Xvfb needs a separate shared-library directory, pass `--xvfb-library`. Use `--xvfb-tcp` on runners where Unix sockets are unavailable. Both display modes require a per-run X11 cookie.

The logs and `result.json` are written under the output directory's `logs/`. A zero exit status requires the sword combo and roll plus all six dragon phases, dragon death, active IK, dust particle creation, Wither armor, ghost clones, three laser targets, the laser blast sound, and Wither death on both clients. Sound checks observe events through the client sound manager under a null audio driver. A failure reports the missing marker and leaves the logs for diagnosis.
