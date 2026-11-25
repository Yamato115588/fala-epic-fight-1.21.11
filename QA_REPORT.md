# V3 Epic Fight verification

| Check | Result | Evidence |
| --- | --- | --- |
| Pinned official source and non-asset extraction | PASS | Both archive hashes validated by tools/audit_source_port.py. See PORT_COVERAGE.md. |
| Clean Gradle build, access widener and original unit tests | PASS locally on JDK 21 | Fourteen JUnit tests, zero failures and errors. The remapped development JAR was generated. |
| Differential pose math | PASS | 4,096 poses, SHA-256 5af6ebf22f79d6cf3291420c3b9ab53d31f2efebe2103e1fa4d189955594841c. |
| Complete data/model suite | FAIL | testPortData reached ItemModelPortTest and stopped resolving epicfight:items/skillbook.json. Strict worktree contains no generated Beta models. |
| Original licensed assets, complete V3 combat/render/boss parity, clip reproduction, device and authenticated multiplayer tests | NOT TESTED | Original asset permission, exact clip and target environments are outstanding. Earlier Beta tests apply only to their pinned artifact. |

The repository contains source changes and reference evidence. The V3 CI has no release or game-JAR upload step.
