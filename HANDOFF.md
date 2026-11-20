# Epic Fight Fabric 1.21.11

งานชุดนี้ต่อจาก `1289d92ef673` บน `fabric-1.21.11` ใช้ `git rev-parse HEAD` ตรวจ commit และตรวจไฟล์ `.sha256` ของ JAR ใน Actions ที่มี head SHA เดียวกัน

## ทดสอบใหม่หลัง `1289d92ef673`

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
