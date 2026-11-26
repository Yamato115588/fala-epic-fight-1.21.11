# Native Fabric roleplay QA profile

Minecraft Java 1.21.11, Fabric Loader 0.19.3 and Java 21. This profile exercises the Full RC3 roleplay baseline, Macaw building mods, WorldEdit, Easy NPC, Saros Money, Plasmo Voice and Fala Phone. The inventory records the exact side, version and digest for each mod. The first-party test builds are stored privately with the runtime evidence.

From the repository root, use a new output directory and the original Full RC3 mrpack. Supply ASM 9.10.1 and asm-tree 9.10.1 on the classpath for the e4mc adaptation. The source pack and lock fix the downloads. A populated SHA-512 cache also supports offline staging.

```sh
python roleplay/stage_mods.py path/to/full-rc3.mrpack work/profile \
    --local-builds test-evidence/roleplay/local-builds \
    --java-home "$JAVA_HOME" --asm-classpath "$ASM_CLASSPATH"
```

The output contains client/mods and server/mods. The original pack remains the source of its configurations and other resources. The first-party prefab datapack can be installed in a private test world's datapacks directory. The WorldEdit schematics belong in the server's WorldEdit schematics directory. Restrict structure placement, schematic loading and editing to the builder/admin roles configured on that server.

The Fala Phone QA build supports coordinates, local weather, the in-game day, the official project website through Minecraft's link confirmation and a transfer screen when the server exposes /pay. The server validates and settles payments through Saros Money. For testing, an operator can give the item with `/give @s fala_phone:phone`. See QA_REPORT.md for runtime coverage and release gates.
