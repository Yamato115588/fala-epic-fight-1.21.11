# V3 Epic Fight verification

| Check | Result | Evidence |
| --- | --- | --- |
| Pinned official source and non-asset extraction | PASS | Both archive hashes validated by tools/audit_source_port.py. See PORT_COVERAGE.md. |
| Clean Gradle build, access widener and original unit tests | PASS locally on JDK 21 | Fourteen JUnit tests, zero failures and errors. The remapped development JAR was generated. |
| Differential pose math | PASS | 4,096 poses, SHA-256 5af6ebf22f79d6cf3291420c3b9ab53d31f2efebe2103e1fa4d189955594841c. |
| Complete data/model suite | FAIL | testPortData reached ItemModelPortTest and stopped resolving epicfight:items/skillbook.json. Strict worktree contains no generated Beta models. |
| Original licensed assets, complete V3 combat/render/boss parity, clip reproduction, device and authenticated multiplayer tests | NOT TESTED | Original asset permission, exact clip and target environments are outstanding. Earlier Beta tests apply only to their pinned artifact. |

The repository contains source changes and reference evidence. The V3 CI has no release or game-JAR upload step.

## 26 November 2026 · native Fabric roleplay profile

| Check | Result | Observation |
| --- | --- | --- |
| Mod inventory | PASS | Restaged offline from the SHA-256-pinned Full RC3 archive, an existing SHA-512 download cache, and two local test builds. Verified IDs, versions and SHA-256 for 102 client and 53 server files. The target is Minecraft 1.21.11, Fabric Loader 0.19.3 and Java 21. |
| Dedicated server login and reconnect | PASS | e4mc 6.2.1 failed in the command permission predicate. After mapping the same owner-level check to 1.21.11, a full Fabric client joined and rejoined over loopback. |
| Save and restart | PASS | After restarting the dedicated server, the test found the chair, bridge, ATM, clinic fixture and NPC in the saved world. The sender retained a balance of 70. |
| Fala Phone | PASS for item, home, coordinates and transfer | The client opened the held phone and displayed world coordinates. A transfer of 12 through its confirmation screen appeared in chat. The server reported 58 for the sender and 42 for the Carpet test recipient. |
| Saros sign regression | PASS for sign editing | The original client logged NoSuchFieldException for blockEntity. With the client-only adapter, registration succeeded, the player placed and edited a sign and the dedicated server returned its four lines, including “Fala sign QA”. Shop purchases and stock settlement remain untested. |
| Plasmo Voice | PASS for loopback UDP connection; physical capture NOT TESTED | Client and server recorded the connection. The test desktop has no capture device. The running game reported both input backends unavailable. |
| Release gates | NOT TESTED | Authenticated remote play, two human callers, Epic Fight upstream visual parity, shop purchases, cross-platform launcher flows, physical GPU/mic and same-hardware Horizon comparison. |

The Full RC3 fixture is separate from the historical 24-mod Lite/Beta. The V3 Epic Fight development JAR is excluded from this roleplay run. The ZIP and schematics under roleplay/prefabs contain five original CC0 structures. The snapshot covers only the test world. [Filtered runtime logs](test-evidence/roleplay/loopback.log) · [Phone home](test-evidence/roleplay/phone-home.png) · [GPS](test-evidence/roleplay/phone-gps.png) · [Transfer confirmation](test-evidence/roleplay/phone-bank-confirm.png) · [Sign editor](test-evidence/roleplay/sign-edit.png)
