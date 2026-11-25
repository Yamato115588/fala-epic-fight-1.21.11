# Epic Fight source parity on Fabric 1.21.11

The official project ported its NeoForge tree to Fabric for Minecraft 1.21.1 in commit 866a2a1. V3 applies the existing Fala 1.21.11 migration to that upstream Java implementation. Beta 0.1.0 remains pinned at b7875ca3b1ed. [Official Fabric change](https://github.com/Antikythera-Studios/epicfight/commit/866a2a1e4268d0d7897c6a5be4ef1e58e47d7443)

| Main Java paths | Source files | Identical to preceding tree | Changed at same path | Added | Absent at old path |
| --- | ---: | ---: | ---: | ---: | ---: |
| Official NeoForge parent a78aa24 | 938 | — | — | — | — |
| Official Fabric 866a2a1 | 1,000 | 600 | 314 | 86 | 24 |
| Fala 1.21.11 V3 development | 1,023 | 484 | 505 | 34 | 11 |

Counts compare Java source after CRLF normalization. The inventory indexes each of the three trees by path and records its SHA-256. Separate counts per package and all eleven missing paths are in the evidence. A moved or adapted entry still needs behavioral verification. Source presence alone cannot establish feature coverage. [Per-file comparison](test-evidence/v3/source-diff.tsv) · [Per-package counts](test-evidence/v3/source-summary.json)

| Feature | Verified on V3 | Open |
| --- | --- | --- |
| Skeleton transforms and matrix math | 4,096 deterministic poses run through the separately compiled official Fabric and target implementations, including inversion round trips. Output float bits matched. | Authored skeletons, animation blending and model alignment in the same scene |
| Combat, colliders, movement, skills, AI, camera, networking, equipment and particles | Main sources compiled against target mappings and validated access widener. Wooden sword data now targets the registered particle and sound. | Same-input in-game comparison with an official installation, including multiplayer timing and authenticated sessions |
| Model and shader rendering | Five port-specific resources are present. The historical Beta generator is opt-in for reference builds. | Data test stops resolving epicfight:items/skillbook.json. The unlicensed original animations, models, textures and sounds cannot be supplied. Real build is development-only. |
| Optional integrations | The official NeoForge-to-Fabric step itself removed or moved 24 paths, including optional mod integrations. | Reconcile each integration with its present Fabric providers before declaring upstream parity. |

The upstream archive contains 991 asset paths. Original media require prior written permission under the pinned asset license. The private code-only branch keeps them out of the build. The historical QA4 resource companion and boss/loopback observations belong to the old Beta. Clip 100268.mp4 did not appear among the accessible files. [Upstream asset license](https://github.com/Antikythera-Studios/epicfight/blob/866a2a1e4268d0d7897c6a5be4ef1e58e47d7443/LICENSE-ASSETS)
