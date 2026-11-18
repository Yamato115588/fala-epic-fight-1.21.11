# Fala SiayaCraft · พอร์ต Epic Fight สำหรับ Fabric 1.21.11

ชุดซอร์สสำหรับพัฒนาและคอมไพล์ระหว่างพอร์ต เป้าหมายคือ Minecraft Java **1.21.11**, Java 21, Fabric Loader **0.19.3** และ Fabric API **0.141.6+1.21.11** ฐานคือสาขา Fabric 1.21.1 ของทีม Epic Fight ที่ commit `866a2a1e4268d0d7897c6a5be4ef1e58e47d7443` [Epic Fight Fabric ต้นทาง](https://github.com/Antikythera-Studios/epicfight/tree/866a2a1e4268d0d7897c6a5be4ef1e58e47d7443)

## ส่วนที่พอร์ตแล้วในซอร์ส

- ย้ายชื่อคลาสและ descriptor ตาม Mojang mappings ของ 1.21.11 รวมถึง `ResourceLocation` → `Identifier`
- ย้ายหมวดคีย์เป็น `KeyMapping.Category` และปรับการนับการกดปุ่มตามวิธีเรียกคีย์ของเกมรุ่นใหม่
- ปรับตัวส่งแพ็กเก็ตให้ใช้ Fabric `PlayerLookup` สำหรับผู้เล่นที่ติดตามชังก์นั้น และคงรหัสแพ็กเก็ตเดิม
- ปรับการลงทะเบียน Listener เป็น Fabric `ResourceLoader` พร้อมรักษาลำดับการโหลดที่กำหนด และย้ายตัวอ่าน JSON 12 ตัวไปยัง API แบบ `Codec`
- ย้ายการอ่านรายการอีโมตที่ผู้เล่นบันทึกไว้ไปยัง NBT และ registry API ของ 1.21.11 เก็บรูปแบบข้อมูลเดิมและอ่านรายการที่มีช่องเกินหรือ ID ที่ไม่ถูกต้องได้
- ย้าย Game Rules ทั้ง 13 รายการไปใช้ Fabric Game Rule API โดยใช้ชื่อแบบ `epicfight:weight_penalty` ในคำสั่งของเกม เก็บชื่อที่ใช้ในแพ็กเก็ตซิงก์เดิมไว้ และแปลงค่าในเซฟจากกฎรุ่นเก่าเมื่อเปิดเวิลด์
- อ่านสกิลที่ติดตั้ง สกิลที่เรียนไว้ และโหมดผู้เล่นด้วย NBT และ registry API ของ 1.21.11 เก็บคีย์และรูปแบบเซฟเดิมไว้

## เตรียมและตรวจซอร์ส

ใช้ Python 3.11 ขึ้นไป, Git และ JDK 21 สคริปต์ตรวจ SHA-256 ของ archive ต้นทาง สร้างซอร์สในโฟลเดอร์ใหม่ และใช้แพตช์ตามลำดับ ไฟล์แอสเซตและชุดทรัพยากรที่มากับต้นทางถูกตัดออกจากซอร์สที่สร้าง

```sh
python3 tools/prepare_fabric_port.py epicfight-fabric-work
cd epicfight-fabric-work
./gradlew compileJava
```

บน Windows ใช้ `py -3 tools\prepare_fabric_port.py epicfight-fabric-work` แล้วรัน `gradlew.bat compileJava` จากโฟลเดอร์ที่สร้าง สคริปต์รับ `--upstream-archive` สำหรับ archive ที่ดาวน์โหลดไว้แล้ว โดยตรวจ checksum เดียวกัน

## ผลทดสอบและสถานะ

- ซอร์ส Fabric 1.21.1 ต้นทางคอมไพล์ผ่านด้วย Gradle 9.5.1, Loom 1.17.19 และ Java 21
- การเตรียมซอร์ส 1.21.11 จาก archive ที่ตรึงเวอร์ชันผ่าน ตัวส่งแพ็กเก็ตและโค้ดปุ่มที่แก้ผ่านการคอมไพล์เฉพาะส่วนกับคลาสของ Minecraft 1.21.11 และ Fabric API
- ตัวอ่านอีโมตผ่านการทดสอบในโปรแกรมทดสอบแยกด้วย NBT และ registry จริงของ Minecraft 1.21.11 มีตัวอย่างบันทึกแล้วอ่านกลับ ค่าเริ่มต้น ID ที่ไม่ถูกต้อง และรายการที่มีช่องเกิน
- ทดสอบ Game Rules ด้วยมอดทดสอบใน Fabric Loader 0.19.3 บน Minecraft 1.21.11 เข้าได้ถึงช่วงเริ่มต้นมอดและผ่านการลงทะเบียน การอ่านค่าจาก NBT ผ่าน `LevelSettings` และการเรียก callback ซิงก์ ส่วนการส่งแพ็กเก็ตให้ผู้เล่นจริงยังต้องทดสอบกับมอดเต็ม
- ตัวอ่านสกิลผ่านการทดสอบบันทึกและอ่านกลับด้วย NBT และ registry จริง รวมถึงกรณีข้อมูลขาดหายและ ID ที่ไม่ถูกต้อง
- `processResources` ของ 1.21.11 ผ่าน การคอมไพล์ทั้งมอดยังติด API เรนเดอร์, Registry, NBT ในส่วนอื่น, mixin targets และมอดเสริม และ `validateAccessWidener` ยังพบสมาชิก Minecraft ที่ต้องย้าย จึงยังไม่มี JAR สำหรับเล่น การทดสอบคอมโบ แอนิเมชันและการซิงก์ระหว่างผู้เล่นต้องทำหลังได้ build ที่เปิดเกมได้
- Arclight ที่พบในเซิร์ฟเวอร์ Fala ฝัง Fabric Loader 0.19.2 ต้องทดสอบด้วย Arclight สำหรับ 1.21.11 ที่มี Loader ตรงตามข้อกำหนด และทดสอบร่วมกับ CustomFigura, Emotecraft และ Geyser ในเซิร์ฟเวอร์ทดสอบก่อนรวมแพ็กจริง [เวอร์ชันที่ Arclight ตรึงไว้](https://github.com/IzzelAliz/Arclight/blob/8a57510/gradle/libs.versions.toml#L34-L35)

## สิทธิ์การใช้งาน

ซอร์ส Epic Fight ใช้ GPL-3.0 ส่วนโมเดล แอนิเมชัน ภาพ เสียง และทรัพยากรเดิมสงวนสิทธิ์ รุ่นสำหรับแจกต้องใช้แอสเซตที่ได้รับอนุญาตหรือที่โครงการมีสิทธิ์ใช้เอง [เงื่อนไขของ Epic Fight](https://github.com/Antikythera-Studios/epicfight/blob/866a2a1e4268d0d7897c6a5be4ef1e58e47d7443/README.md#license)
