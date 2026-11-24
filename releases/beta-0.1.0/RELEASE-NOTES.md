# Epic Fight Fabric 1.21.11 — Beta 0.1.0

Beta ของพอร์ต Fala จาก commit [`b7875ca3b1ed`](https://github.com/Yamato115588/fala-epic-fight-1.21.11/commit/b7875ca3b1ed15ddec14f64d9466a040f2aba52a) พร้อม JAR ที่ตรงกับผลทดสอบเดิม ไม่ใช่ Stable หรือรุ่นทางการของ Epic Fight

**Repository ยังเป็น Private: เฉพาะผู้มีสิทธิ์เข้าถึงเท่านั้นที่ดาวน์โหลดได้ ยังไม่ได้เปิด Public distribution**

## ดาวน์โหลดและติดตั้ง

- Production JAR: `epicfight-fabric-1.21.11-beta-0.1.0.jar`
- SHA-256: `034d5f19c96f4bdd28c06299bc7d1cf73d070a70dcc5d9186a00a8f9a36c90ff`
- Internal mod version: `21.17.3-fala.2+mc1.21.11`
- ต้องใช้ Minecraft Java **1.21.11**, Java **21**, Fabric Loader **0.19.3**, Fabric API **0.141.6+1.21.11**
- วาง JAR และ Fabric API ใน `mods/` ของ instance ทดสอบ สำรองโลกก่อนใช้ Beta ดู `INSTALL-TH.md` ที่แนบสำหรับ checksum และการใช้กับ Fala Lite โดยรักษา 24 มอดเดิม

## หลักฐานที่ใช้

[GitHub Actions ผ่าน](https://github.com/Yamato115588/fala-epic-fight-1.21.11/actions/runs/44862928688): clean build, replacement assets, RenderPass ด้วย llvmpipe, JAR validation และ boss smoke

JAR จาก CI มี SHA-256 ตรงกับ [ผล runtime เดิม](https://github.com/Yamato115588/fala-epic-fight-1.21.11/blob/b7875ca3b1ed15ddec14f64d9466a040f2aba52a/test-evidence/lite-lifecycle.json): Fala Lite 24 มอด สอง Client กับ Dedicated แบบ loopback, คอมโบดาบเหล็ก 3 จังหวะ/ความเสียหาย/กลิ้งหน้า, มังกร 6 เฟส/IK และ Wither ตามสถานะที่บันทึก บอสใช้ controlled lifecycle inputs เสียงตรวจ sound-manager events ด้วย null audio output ไม่ใช่การฟังเสียงผ่านอุปกรณ์

**Authenticated multiplayer: NOT TESTED**

ยังไม่มีการยืนยันครบสำหรับ GPU จริงหลายรุ่น อาวุธ/สกิลทุกชนิด และ optional integrations ทั้งหมด รอบ Release ใช้ผลเดิมที่ผูกกับ hash เดียวกัน ไม่รันเกมหรือ Gradle ซ้ำ

## สิทธิ์และ Source

โค้ด GPL-3.0; แอสเซตทดแทนที่สร้างเอง 322 รายการ CC0-1.0 พร้อม manifest และอีก 5 resources จาก port patches ตรวจ allowlist/SHA-256 ผ่าน ไม่รวมแอสเซตต้นฉบับที่สงวนสิทธิ์หรือไฟล์เกม Minecraft รวม NightConfig core/toml 3.8.0 ภายใต้ LGPL-3.0

แนบซอร์สเต็มที่เตรียมจาก commit นี้ แพตช์/ขั้นตอน build ซอร์ส NightConfig ใบอนุญาต `THIRD-PARTY-NOTICES.txt`, `PROVENANCE.json`, และ `SHA256SUMS.txt` ให้ตรวจสอบย้อนกลับได้
