# Epic Fight Fabric 1.21.11

เริ่มจาก `c1adf84f57a9` บน `fabric-1.21.11` โดยมี checkpoint `328166bf9de8` ที่เข้าโลก Singleplayer และต่อ Dedicated Server ใน Fabric Client GameTest ได้ ตรวจ commit ของชุดแก้ล่าสุดด้วย `git rev-parse HEAD` และเทียบ JAR กับไฟล์ `.sha256` ใน GitHub Actions Artifact ของ commit นั้น

## การแก้ไข

- ใช้ `AtlasIds.ARMOR_TRIMS` ตาม logical atlas ID ของ Minecraft 1.21.11 พร้อม fallback ที่แปลงโมเดลเกราะ vanilla ตอนโหลดเมื่อไม่มีแอสเซตเกราะเริ่มต้นใน resource pack
- สร้าง Enderman rig, mesh และคีย์เฟรม 17 ชุดจากซอร์ส CC0 ใน `replacement-assets/` รวมท่าเดิน โกรธ โจมตี และ teleport
- แก้แกนการเคลื่อนที่ของ roll และ step ให้สอดคล้องกับตัวอ่าน Coord และเพิ่มภาพ UI สำหรับแถบพลังกับเครื่องหมายเป้าหมายภายใต้ CC0
- ใช้ Holder ของ attribute ที่ลงทะเบียนจริงเพื่อให้ Minecraft serialize ค่าผู้เล่นและซิงก์ผ่านเครือข่ายได้ แก้ตัวแสดง skin layer ให้ใช้โมเดลปัจจุบันของ renderer
- ระบบสร้าง JAR ตรวจรายการและ SHA-256 ของแอสเซตทดแทนตาม `LICENSE-ASSETS` ของ upstream ซอร์สพอร์ต GPL-3.0 ใช้ resource pack ที่ได้รับอนุญาตเป็นแหล่ง override ได้

## ทำซ้ำ

ต้องใช้ Java 21 สำหรับ build และ Minecraft

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

สร้าง `run/eula.txt` ด้วย `eula=true` หลังผู้มีสิทธิ์ยอมรับ Minecraft EULA ในอินสแตนซ์ทดสอบ Dedicated Server แล้ว การทดสอบ Multiplayer แบบ local ใช้ loopback และบัญชีทดสอบ

## ผลทดสอบ

- `compileJava`, `clean build` และ `testPortData` ผ่าน ตรวจ JAR แบบ remapped และแอสเซต CC0 จำนวน 191 รายการ SHA-256 ของ JAR ที่ใช้ทดสอบ `6ff82c084b9fd3a981f96d88d0e6fc6110afaf2243f19e50fc297a84226e58ba`
- เปิด Client และเข้าโลก Singleplayer ด้วยแพ็กล่าสุด ใน Dedicated Server แบบ loopback ผู้เล่นเข้าโลกได้และเรนเดอร์ Enderman กับผู้เล่นที่สวม diamond chestplate พร้อม redstone spire trim
- ทดสอบด้วยการกดปุ่มจริงใน Client ที่ต่อ Dedicated Server พบคอมโบดาบเหล็ก 3 จังหวะทั้งฝั่ง Client และ Server ที่ระยะ 1.15 บล็อก HP ของเป้าหมายลดจาก 90 เหลือ 36 หลังเอาเป้าหมายออกแล้วตำแหน่ง Z เปลี่ยนจาก 8.50 เป็น 10.82 เมื่อกลิ้งไปหน้า และเป็น 8.09 เมื่อกลิ้งถอยหลัง
- เก็บ [Build Log](test-evidence/build.log) และ [Runtime Log](test-evidence/runtime.log) พร้อม SHA-256 ของมอดแพ็ก [Client](test-evidence/client-pack-sha256.txt) และ [Server](test-evidence/server-pack-sha256.txt)

## สิ่งที่ยังต้องยืนยัน

- หาไฟล์หรือ manifest ต้นฉบับของ Fala Lite 24 มอดที่ตรวจ SHA-256 ได้ แพ็ก [Fala Siaya Craft 1.0.0](https://drive.google.com/file/d/1N6CrXBTBOCfZyhZBaOaq0__UVd4P4h6H/view) ที่ให้ล่าสุดมีมอด Client 93 และ Server 36 ก่อนเพิ่ม Epic Fight ใช้ Minecraft 1.21.11 และ Fabric Loader 0.19.3
- แอสเซตทดแทนยังครอบคลุมเพียงส่วนหนึ่งของคลิปและเสียง ตัวอย่างที่ log ระบุคือ `zombie/idle` และ `creeper/idle` ตรวจชุดอาวุธ สกิล และม็อบที่เหลือแยกตาม resource ID
- ทดสอบหลายคนแบบยืนยันบัญชีบนเซิร์ฟเวอร์ที่ได้รับอนุญาตและทดสอบประสิทธิภาพบน GPU จริงก่อนเผยแพร่
