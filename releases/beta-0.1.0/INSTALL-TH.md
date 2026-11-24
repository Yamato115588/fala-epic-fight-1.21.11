# Epic Fight Fabric 1.21.11 — Beta 0.1.0

เป็น Beta ของพอร์ต Fala ที่ commit `b7875ca3b1ed15ddec14f64d9466a040f2aba52a` ชื่อเวอร์ชันภายใน JAR ยังคงเป็น `21.17.3-fala.2+mc1.21.11` เพื่อรักษาไฟล์ที่ทดสอบแล้ว ไม่ใช่เวอร์ชัน Stable หรือรุ่นทางการของทีม Epic Fight

## Dependencies

| รายการ | รุ่นที่ใช้ทดสอบ |
| --- | --- |
| Minecraft Java | 1.21.11 |
| Java | 21 |
| Fabric Loader | 0.19.3 |
| Fabric API | 0.141.6+1.21.11 |

Metadata กำหนด Minecraft `=1.21.11`, Java `>=21`, Fabric Loader `>=0.19.3`, Fabric API `*` แนะนำรุ่นที่ทดสอบข้างต้น NightConfig core/toml 3.8.0 รวมใน JAR แล้ว ไม่ต้องติดตั้งซ้ำ มอดใน `suggests` เป็นตัวเลือกและไม่ได้หมายความว่าทดสอบครบทุกตัว Figura compatibility bridge เป็นมอดแยก ไม่รวมในไฟล์นี้

## ติดตั้ง

1. ปิดเกมและสร้าง instance ทดสอบ Minecraft 1.21.11 ด้วย Java 21 และ Fabric Loader 0.19.3 สำรองโลกก่อนใช้ Beta
2. ติดตั้ง Fabric API 0.141.6+1.21.11 ลง `mods/` ของ instance นี้ หากมีรุ่นที่ตรงอยู่แล้วไม่ต้องเพิ่มซ้ำ
3. ดาวน์โหลด `epicfight-fabric-1.21.11-beta-0.1.0.jar` และไฟล์ `.sha256` ตรวจ checksum แล้ววาง JAR ใน `mods/` อย่าติดตั้ง Epic Fight หลาย JAR ที่มี mod ID เดียวกัน
4. เปิดเกม ตรวจว่าโหลดมอด `epicfight` แล้วเข้าโลกทดสอบ ตั้งปุ่ม Battle Mode/Attack/Dodge ใน Options → Controls ตามต้องการ
5. หากใช้ Fala Lite ให้คัดลอก instance ทดสอบและเพิ่ม Epic Fight โดยคงไฟล์เดิมทั้ง 24 มอด ไม่แก้หรือแทนไฟล์ชุดเดิม
6. Dedicated server ต้องใช้ Minecraft/Fabric/API รุ่นตรงกันและ Epic Fight JAR เดียวกับ Client ใช้เฉพาะมอดที่รองรับ Server อย่าคัดลอกมอด Client ทั้งชุดเข้า Server ผลเดิมใช้โปรไฟล์ 20 JAR โดย Fabric โหลด 13 มอดจากแพ็ก ส่วน Client คง 24 JAR ไม่ได้เปลี่ยนเซิร์ฟเวอร์ uniz.host ในรอบนี้

ตรวจ SHA-256 บน Linux/macOS:

```sh
sha256sum -c epicfight-fabric-1.21.11-beta-0.1.0.jar.sha256
# macOS หากไม่มี sha256sum:
shasum -a 256 -c epicfight-fabric-1.21.11-beta-0.1.0.jar.sha256
```

Windows PowerShell:

```powershell
Get-FileHash .\epicfight-fabric-1.21.11-beta-0.1.0.jar -Algorithm SHA256
```

ค่าที่ต้องตรง: `034d5f19c96f4bdd28c06299bc7d1cf73d070a70dcc5d9186a00a8f9a36c90ff`

## ขอบเขตผลทดสอบ

ใช้ผลเดิมของ JAR ที่มี SHA-256 ตรงกันจาก `HANDOFF.md` และ `test-evidence/lite-lifecycle.json`: CI clean build, asset validation, llvmpipe RenderPass, boss smoke และ Fala Lite สอง Client กับ Dedicated แบบ loopback ผ่านตามขอบเขตที่บันทึกไว้ มีคอมโบดาบเหล็ก 3 จังหวะ ความเสียหายจริง กลิ้งหน้า มังกร 6 เฟส/IK และสถานะ Wither ที่ระบุในหลักฐาน การทดสอบบอสใช้ controlled lifecycle inputs ผลเสียงเป็น sound-manager events และ null audio output

- **Authenticated multiplayer: NOT TESTED**
- GPU จริงหลายรุ่น, การฟังเสียงจากอุปกรณ์จริง, อาวุธ/สกิลทั้งหมด และ optional integrations ทั้งหมด: ยังไม่มีหลักฐานยืนยันครบ
- รอบเตรียม Release ตรวจไฟล์/สิทธิ์/checksum และใช้ผลทดสอบเกมเดิม งาน build อัตโนมัติที่เกิดจากการแก้ไฟล์ workflow ถูกยกเลิกระหว่างขั้น Gradle และข้าม runtime tests ไม่ใช้รอบที่ยกเลิกเป็นหลักฐานว่าผ่าน

## Source และสิทธิ์

แนบ `epicfight-fabric-1.21.11-beta-0.1.0-source.tar.gz` พร้อมซอร์สที่เตรียมจาก commit นี้ สคริปต์ build แพตช์ แอสเซตทดแทน และซอร์ส NightConfig ดู `THIRD-PARTY-NOTICES.txt` และใบอนุญาตที่แนบ

Repository ปัจจุบันเป็น Private ผู้ดาวน์โหลดผ่าน GitHub ต้องมีสิทธิ์เข้าถึง จึงยังไม่ใช่ลิงก์ Public ที่ทุกคนดาวน์โหลดได้
