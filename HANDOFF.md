# Epic Fight Fabric 1.21.11

งานชุดนี้ต่อจาก `eceda04e38d2` บน `fabric-1.21.11` ตรวจ SHA ของโค้ดฉบับปัจจุบันด้วย `git rev-parse HEAD` และดาวน์โหลด JAR กับไฟล์ `.sha256` จาก GitHub Actions ของ commit เดียวกัน

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
- ทดสอบหลาย Client พร้อมกันและการเข้าเซิร์ฟเวอร์ด้วยบัญชีที่ยืนยันตัวตน รวมถึง GPU จริงหลายรุ่น
