# Epic Fight Fabric 1.21.11

## เตรียม Beta 0.1.0 — 24 พฤศจิกายน 2569

- Target ยังคงเป็น `b7875ca3b1ed15ddec14f64d9466a040f2aba52a` ไม่แก้ runtime หรือ Fala Lite ใช้ผล runtime เดิมเพราะ JAR จาก Actions `44862928688` มี SHA-256 ตรงกับ `test-evidence/lite-lifecycle.json`: `034d5f19c96f4bdd28c06299bc7d1cf73d070a70dcc5d9186a00a8f9a36c90ff`
- ตรวจ JAR metadata, intermediary access widener, CI, checksum และรายการแอสเซตผ่าน: 322 CC0 resources + 5 port resources ไม่มีไฟล์นอก allowlist และไม่พบแอสเซตที่เหมือนต้นฉบับที่สงวนสิทธิ์ ตรวจ NightConfig core/toml 3.8.0 ตรงกับ Maven ทุก class พร้อมจัดเตรียม LGPL license/source
- Dependencies ที่ใช้ทดสอบ: Minecraft 1.21.11, Java 21, Fabric Loader 0.19.3, Fabric API 0.141.6+1.21.11 วิธีติดตั้งและขอบเขตผลทดสอบอยู่ใน `releases/beta-0.1.0/INSTALL-TH.md`
- **Authenticated multiplayer: NOT TESTED** ผลเสียงเดิมเป็น sound-manager events ด้วย null audio output บอสใช้ controlled lifecycle inputs ไม่ได้ยืนยันอาวุธ/สกิลทั้งหมดหรือ GPU จริงหลายรุ่น
- ส่งมอบ [Beta 0.1.0](https://github.com/Yamato115588/fala-epic-fight-1.21.11/releases/tag/v0.1.0-beta) เป็น prerelease แล้ว (`draft=false`, `prerelease=true`) tag ชี้ `b7875ca3b1ed` ตามเดิม [Release Actions 45346596388 ผ่าน](https://github.com/Yamato115588/fala-epic-fight-1.21.11/actions/runs/45346596388) ตรวจ digest/ขนาดของไฟล์แนบครบ 12 ไฟล์ รวม production JAR, SHA-256, corresponding source, dependencies/วิธีติดตั้ง และใบอนุญาต
- การอัปโหลดจาก Cloud ไป `uploads.github.com` เคยตอบ `401 Bad credentials` แก้โดยใช้ GitHub Actions อัปโหลดสำเร็จ ไม่ใช่ blocker ค้างแล้ว Workflow เตรียม Release ไม่บิลด์/เล่นเกมใหม่ งาน build อัตโนมัติ `45346273720` ซึ่งเริ่มจากการแก้ไฟล์ workflow ถูกยกเลิกระหว่างขั้น Gradle และข้าม runtime tests ใช้ผลผ่านของ commit เดิมเท่านั้น
- **Public distribution ยังติดข้อจำกัด**: Repository เป็น Private ผู้ไม่มีสิทธิ์ดาวน์โหลดไม่ได้ ไม่ได้เปลี่ยน visibility ของ repository
- [ดาวน์โหลด JAR](https://github.com/Yamato115588/fala-epic-fight-1.21.11/releases/download/v0.1.0-beta/epicfight-fabric-1.21.11-beta-0.1.0.jar) ต้องมีสิทธิ์เข้าถึง repository ส่วนข้อจำกัด Public distribution ข้างต้นยังคงอยู่

งานชุดนี้ต่อจาก `1289d92ef673` บน `fabric-1.21.11` ใช้ `git rev-parse HEAD` ตรวจ commit และตรวจไฟล์ `.sha256` ของ JAR ใน Actions ที่มี head SHA เดียวกัน

## รอบทดสอบ 21 พฤศจิกายน 2569

- เริ่มจาก `78deb6cc8a24` ซึ่งต่อจาก `1289d92ef673` โดยตรง [Actions รอบที่ค้าง](https://github.com/Yamato115588/fala-epic-fight-1.21.11/actions/runs/44731427191) หยุดที่ spawn 16% ด้วย `Timeout loading world` ส่วน [รอบหลังแยก NetworkSynchronizer ของ Fabric Client GameTest](https://github.com/Yamato115588/fala-epic-fight-1.21.11/actions/runs/44787185235) เปิดโลกได้ใน 7.9 วินาทีและตรวจฝุ่นกับ IK ได้ คง timeout 6 นาทีเฉพาะขั้น smoke ตัวสรุปจะถือว่าขั้นนี้ล้มเหลวถ้าขาดผลฝุ่นหรือ IK แม้ Gradle คืนสถานะสำเร็จ
- เครื่องทดสอบปัจจุบันเปิด Unix socket ของ Xvfb ไม่ได้ ตัวทดสอบใช้หมายเลขจออัตโนมัติและรองรับ TCP พร้อม cookie แยกแต่ละรอบ Gradle ในเครื่องใช้ JDK 21 ที่ตรวจพบได้และ cache ของ Loom สำหรับการบิลด์แบบออฟไลน์
- แก้คำเตือนเมื่อเข้าโหมดต่อสู้ด้วยไอคอน Sweeping Edge ขนาด 32×32 ที่สร้างใหม่ ตรวจไฟล์ใน JAR พร้อมรายการ SHA-256 ของแอสเซต CC0 ทั้ง 322 รายการ
- JAR จาก clean build รอบนี้มี SHA-256 `034d5f19c96f4bdd28c06299bc7d1cf73d070a70dcc5d9186a00a8f9a36c90ff` ตรวจ `testPortData` และ `testComputeRenderPass` ด้วย llvmpipe แล้ว [ตรวจ CI และ Artifacts ตาม commit](https://github.com/Yamato115588/fala-epic-fight-1.21.11/actions/workflows/fabric-build.yml?query=branch%3Afabric-1.21.11)
- รัน JAR ที่มี hash ข้างต้นกับ Fala Lite ใหม่ Client ทั้งสองโหลดครบ 24 ม็อด ส่วน Dedicated ติดตั้ง 20 JAR และ Fabric โหลด 13 ม็อดที่รองรับเซิร์ฟเวอร์ ตรวจ hash ของแพ็กและม็อดทั้งสองโปรไฟล์ Client สองตัวเห็นมังกรครบ 6 เฟสและตาย รวมถึงท่าฟื้นและบินขึ้น, Landing IK, ฝุ่น `dust_contractive` และเสียงลมหายใจ Wither เข้าเกราะ โคลน Ghost เลเซอร์ 3 เป้า เสียงยิง และตายครบทั้งสอง Client
- กดโจมตีและกลิ้งจริงบน Client แรก Dedicated รับคอมโบดาบเหล็ก 3 จังหวะ เป้าหมายเสีย HP จาก 10 เป็น 0 และรับท่ากลิ้งหน้า ตรวจ sound events ของการเหวี่ยงดาบ ฟัน และกลิ้ง [ผลย่อของ JAR รอบนี้](test-evidence/lite-lifecycle.json)
- วิธีทดสอบสอง Client และ Dedicated ใช้ [คู่มือตัวทดสอบบอส](tools/boss-test/README.md) โปรแกรมเปิดเซิร์ฟเวอร์เฉพาะ `127.0.0.1` และตรวจ hash ของแพ็กก่อนเปิดเกม
- Multiplayer แบบยืนยันบัญชีจริง **NOT TESTED** ไม่มีบัญชีและเซิร์ฟเวอร์ทดสอบที่ได้รับอนุญาต

## ผลย้อนหลังของ `78deb6cc8a24`

- เครื่องทดสอบเจอ Xvfb แจ้งว่า display หมายเลขเดิมกำลังใช้งาน ส่งผลให้ GLFW เปิดไม่ได้ ใช้การเลือก display อัตโนมัติและตรวจว่า Xvfb พร้อมก่อนเปิดเกม
- [Actions รอบเดิม](https://github.com/Yamato115588/fala-epic-fight-1.21.11/actions/runs/44731427191) และการรันซ้ำในเครื่องหยุดที่ spawn 16% แล้ว Fabric Client GameTest แจ้ง `Timeout loading world` การปิด NetworkSynchronizer เฉพาะ smoke test ทำให้โลก Flat โหลดได้ใน 8.5–9.6 วินาทีในการตรวจสาเหตุ ใช้ timeout เดิมของการโหลดโลก ตัวรัน CI เก็บเฉพาะสถานะ spawn ที่เปลี่ยน ผลตรวจ และท้าย error
- คงการส่ง JAR และ SHA-256 ก่อนรัน smoke test และอัปโหลด log ย่อแยกกันเมื่อ smoke test ทำงาน
- ทดสอบ JAR จาก `clean build` ใหม่ SHA-256 `6215c6484680a8051fe0b0ee58d5d2ef4d3047cf822c3b901639105c53e2b00b` ใช้แพ็ก Lite SHA-256 `2676674d1ce000613129d948cd77344e71393994c0704b4e7f597ea91af04415` ดาวน์โหลด JAR ใหม่และตรวจทุกไฟล์ตาม manifest ทั้งสอง Client มี 24 JAR จากแพ็ก Dedicated ใช้รายการ Server 20 JAR ที่ตรวจ SHA-256 ใหม่
- ทดสอบ Singleplayer และ Dedicated ที่ `127.0.0.1` ด้วย Client สองตัว ทั้งสองได้รับ Flying, Landing, Ground Battle, Airstrike, Crystal Link และ Neutralized จากการกำหนดเฟสบน Server ตรวจ pose ระหว่าง Landing IK และวาด `dust_contractive` ในเกมได้
- Wither เข้าชุดเกราะจากสุขภาพ 45% ทั้งสอง Client ได้เป้าเลเซอร์สามหัว, Ghost, การตาย และ sound events จากบอส การต่อสู้บอสแบบเดินครบเฟสเอง **NOT TESTED**
- การกดโจมตีจริงในโหมด Epic Fight ส่งคอมโบดาบเหล็กทั้ง 3 จังหวะให้ Dedicated เป้าหมายเสีย HP จาก 10 เป็น 0 และ Server รับแอนิเมชันกลิ้งหน้า [Runtime Log รอบใหม่](test-evidence/lite-retest.log)
- `testPortData` ตรวจ 321 CC0 resources และ `testComputeRenderPass` ผ่านด้วย llvmpipe
- Multiplayer แบบยืนยันบัญชีจริง **NOT TESTED** ไม่มีบัญชีทดสอบและเซิร์ฟเวอร์ที่ยืนยันสิทธิ์ได้

## การทดสอบบอสจาก `8aa3e017d408`

- ทดสอบ Fala Lite ด้วย Client สองตัวที่ตรวจ SHA-256 ตรงกับ JAR ทั้ง 24 ไฟล์ และ Dedicated แบบ loopback ที่ใช้โปรไฟล์ Server 20 JAR โดยเก็บ Figura Extra Bone ฝั่ง Client
- บน Artifact ของ `8aa3e017d408` สถานะ Flying, Landing และ Ground Battle ของ Ender Dragon มาถึงทั้งสอง Client พร้อมคลิปลงจอด จากนั้นทั้งสอง Client แครชที่ IK ของมังกรซึ่งอ้างเฟรม 9 จาก 9 คีย์เฟรม
- Wither แสดงท่าเลเซอร์ เป้าเลเซอร์สามหัว การถูกบล็อก Ghost และการตายตรงกันบน Dedicated และทั้งสอง Client พบ Ghost Clone และเสียง Wither ambient, break block และ death ในเกมจริง
- บิลด์ทดสอบหลังแก้ IK พบ Client แครชเมื่อชุดเกราะ Wither สร้าง `dust_contractive` โดย SpriteSet ไม่มีรายการภาพ จึงเพิ่ม particle descriptions สำหรับ SpriteSet ทั้ง 13 รายการ โดยอ้างภาพ Minecraft ที่ติดตั้งไว้และใช้ภาพขนนก CC0 ที่สร้างใหม่
- แก้ IK ให้ใช้เวลาจากเฟรมที่มีจริงบนปลายขา แล้วคำนวณ pose ของแต่ละข้อต่อตามเวลานั้น เพิ่ม smoke test สำหรับ dust sprite และท่าลงจอดใน Minecraft บน GitHub Actions

| งาน | สถานะ |
| --- | --- |
| Fala Lite สอง Client แบบ loopback บน `8aa3e017d408` | ทดสอบจริงตามขอบเขตด้านบน |
| Fala Lite หลังแก้สองจุด และการเดินครบทุกเฟสตามธรรมชาติ | **NOT TESTED** หลังพบแครช เพราะเครื่องรันเกมเดิมกู้คืนไม่สำเร็จ |
| Multiplayer แบบยืนยันบัญชีจริง | **NOT TESTED** ไม่มีบัญชีทดสอบและปลายทางที่ยืนยันสิทธิ์เข้าถึง |

รอบเดิมที่ `cf262f0334bd` บิลด์ ตรวจแอสเซต และ Minecraft RenderPass ผ่าน ส่วน smoke test หยุดที่ `Timeout loading world` ก่อนถึง dust sprite และ IK ดูผลทดสอบใหม่ในหัวข้อด้านบน [Actions รอบเดิม](https://github.com/Yamato115588/fala-epic-fight-1.21.11/actions/runs/44731427191)

## แอนิเมชัน เสียง และการเรนเดอร์

- เพิ่มคลิปออกแบบใหม่ 109 คลิปสำหรับม็อบและท่าร่วมของม็อบมนุษย์ พร้อมเมช 5 แบบสำหรับ Zombie, Drowned, Zombie Villager, Illager และ Witch แอนิเมชัน Enderman และกลไกผู้เล่นจากฐานเดิมอยู่ในชุดแอสเซตด้วย
- โหลด Coord ของท่าโจมตีใน Dedicated Server และคลิป IK มังกร ระหว่างเปลี่ยนท่าใช้การเคลื่อนที่เดิมเมื่อคลิปมี Root รองรับท่าที่ขยับเฉพาะแขนหรือส่วนอื่นโดยไม่มี Root
- แก้แคช RenderType ที่คำนวณ outline ซ้อนใน `computeIfAbsent` ซึ่งทำให้ Client ของ Lite หยุดด้วย `Recursive update`
- เสียง 42 รายการอ้างถึง sound event ของ Minecraft 1.21.11 ที่เกมติดตั้งไว้ ไฟล์ Vorbis เงียบของ `sfx.no_sound` สร้างใหม่ ชุดแอสเซตบันทึก SHA-256 ใน JAR ภายใต้ CC0 แล้วตามขั้นตอนตรวจสิทธิ์ของ `LICENSE-ASSETS`

## แพ็กที่ใช้ทดสอบ

| แพ็ก | Client ก่อนเพิ่ม Epic Fight | การติดตั้ง Dedicated |
| --- | --- | --- |
| Fala SiayaCraft Lite 1.21.11 | 24 JAR จาก `.mrpack` เดิม | 20 JAR ในโฟลเดอร์ทดสอบ หลังแบ่งตามสภาพแวดล้อมและเก็บ Figura Extra Bone ไว้ฝั่ง Client |
| Fala Siaya Craft 1.0.0 | 93 JAR | 36 JAR ตาม manifest |

SHA-256 ของไฟล์ Lite `2676674d1ce000613129d948cd77344e71393994c0704b4e7f597ea91af04415` ตรวจไฟล์ที่ดาวน์โหลดตาม SHA-1 และ SHA-512 ใน manifest พร้อม SHA-256 ของ [Client 24 JAR](test-evidence/lite-client.sha256) และ [Dedicated 20 JAR](test-evidence/lite-server.sha256) [แพ็ก Lite ต้นฉบับ](https://drive.google.com/file/d/1b_wxtGDoeoMQiRtkK7zyt4eVJWNkDI7p/view)

การทดสอบ Dedicated ครั้งแรกของ Lite หยุดที่ `figuraextrabone 0.0.42-fabric-hotfix` เพราะมันประกาศการพึ่งพา Figura ซึ่งโหลดเฉพาะ Client โปรไฟล์ Dedicated ทดสอบจึงติดตั้งเฉพาะ JAR ที่ใช้งานได้ฝั่ง Server และเก็บทั้ง 24 JAR ของแพ็กฝั่ง Client

## ทำซ้ำ

ใช้ Java 21 และ Fabric Loader 0.19.3 บน Minecraft 1.21.11

```bash
git switch fabric-1.21.11
git rev-parse HEAD
repo="$PWD"
python3 tools/prepare_fabric_port.py ../epicfight-fabric-work
cd ../epicfight-fabric-work
./gradlew compileJava
./gradlew clean build
jar=$(python3 "$repo/tools/check_fabric_jar.py" build/libs)
sha256sum "$jar"
./gradlew -I "$repo/tools/data-test/data.gradle" testPortData
xvfb-run -a ./gradlew -I "$repo/tools/renderpass-test/renderpass.gradle" testComputeRenderPass
LIBGL_ALWAYS_SOFTWARE=1 ALSOFT_DRIVERS=null LP_NUM_THREADS=2 \
  bash "$repo/tools/world-test/run_ci_smoke.sh" "$PWD/boss-smoke.log"
./gradlew -I "$repo/tools/world-test/world.gradle" -PtestDedicated runClient
```

การทดสอบ Dedicated ต้องตั้ง `run/eula.txt` เป็น `eula=true` หลังผู้มีสิทธิ์ยอมรับ EULA ในโปรไฟล์เฉพาะการทดสอบ ใช้ loopback และผู้เล่นทดสอบ การวัดการเล่นแอนิเมชันใช้ม็อดวัดผลแยกจาก JAR ที่ส่งมอบ

## ผลทดสอบ

- `compileJava`, `clean build` และ `testPortData` ผ่าน ตรวจ Fabric JAR และทรัพยากรทดแทน 307 รายการ SHA-256 ของ JAR ทดสอบ `e481c818277b8599226444fbd8da538135a90476c0b063c80e71be8aa21ea0a6`
- Lite เปิด Client เข้า Singleplayer และต่อ Dedicated แบบ loopback ได้ ทั้งสองฝั่งโหลด 114 คลิปม็อบ มี 9 คลิปที่อ่าน Coord และ 14 คลิปที่คำนวณ IK
- การกดปุ่มใน Client ทดสอบยืนยันคอมโบดาบเหล็ก 3 จังหวะ ทำความเสียหายจริง และกลิ้งหน้า–หลัง Dedicated ส่งท่า Zombie, Creeper, Spider, Vindicator และ Iron Golem ให้ Client เล่นและเรนเดอร์ได้
- ทดสอบเล่นเสียงดาบฟัน เสียงเหวี่ยงดาบ และเสียงกลิ้งผ่าน OpenAL ใน Runtime ตรวจ 43 sound events และไม่พบข้อความแจ้งเสียง Epic Fight ที่ขาดในรอบทดสอบ
- [Build Log](test-evidence/build.log) และ [Runtime Log](test-evidence/runtime.log)

## สิ่งที่ยังต้องยืนยัน

- เล่นการต่อสู้กับบอสครบทุกช่วงและทดสอบอาวุธกับสกิลของผู้เล่นที่อยู่นอกชุดทดสอบปัจจุบัน
- ทดสอบเซิร์ฟเวอร์ที่ยืนยันบัญชีจริงและเรนเดอร์ด้วย GPU จริงหลายรุ่น

## V3 native Fabric checkpoint

Use the v3/upstream-parity branch for original implementation work. The recipe defaults to upstream source with the 1.21.11 API port, no Beta asset generation. The development version is 21.17.3-fala.3-dev+mc1.21.11. The public-distribution and gameplay gates are held. Beta tag, JAR and existing QA packs are preserved. See PORT_COVERAGE.md and QA_REPORT.md for current scope. Continue from the verified source and matrix comparison. Required inputs include written asset rights, the referenced video, an authorized online test account and target devices.

### Native roleplay integration

The repository now preserves the tested Fala Phone source, the e4mc owner-check fix, the Saros sign-field adapter, original furnished prefabs and the exact 102-client/53-server QA inventory. Recreate the isolated mod directories with roleplay/stage_mods.py; use the private test builds in test-evidence/roleplay/local-builds. QA_REPORT.md records actual loopback, restart and transfer results. The live server still requires a verified backup before migration. Authenticated multiplayer, target hardware, upstream asset permission and the full V3 release remain open.

### Epic Fight · keyframe and pose comparison complete

2,112 keyframe and two-joint blending samples matched the pinned official Fabric implementation on the same 1.21.11 runtime. The incremental classes task and the targeted comparison passed. No production implementation changed. Evidence and invocation are in QA_REPORT.md. Next small upstream task: compare collider transforms and hit/miss decisions at weapon-range boundaries using fixed inputs. Authored clip comparisons still require upstream asset permission.
