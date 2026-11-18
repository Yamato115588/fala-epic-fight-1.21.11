# Fala SiayaCraft · พอร์ต Epic Fight สำหรับ Fabric 1.21.11

ชุดซอร์สสำหรับพอร์ตตัวมอด Epic Fight ให้โหลดและเล่นได้บน Minecraft Java **1.21.11**, Java 21, Fabric Loader **0.19.3** และ Fabric API **0.141.6+1.21.11** ทดสอบ Epic Fight กับ Fabric ในอินสแตนซ์แยกก่อนนำไปรวมกับแพ็ก Fala ฐานคือสาขา Fabric 1.21.1 ของทีม Epic Fight ที่ commit `866a2a1e4268d0d7897c6a5be4ef1e58e47d7443` [Epic Fight Fabric ต้นทาง](https://github.com/Antikythera-Studios/epicfight/tree/866a2a1e4268d0d7897c6a5be4ef1e58e47d7443)

| มอด | หน้าที่ | โปรเจกต์สำหรับบิลด์ |
| --- | --- | --- |
| `epicfight` | ระบบต่อสู้ Epic Fight ใช้ได้โดยอิสระจาก CustomFigura เมื่อพอร์ตเสร็จ | สร้างซอร์สด้วย `tools/prepare_fabric_port.py` |
| `fala_figura_compat` | มอดเสริมฝั่งไคลเอนต์สำหรับ Epic Fight และ CustomFigura | `figura-compat/` |

## ส่วนที่พอร์ตแล้วในซอร์ส

- ย้ายชื่อคลาสและ descriptor ตาม Mojang mappings ของ 1.21.11 รวมถึง `ResourceLocation` → `Identifier`
- ย้ายหมวดคีย์เป็น `KeyMapping.Category` และปรับการนับการกดปุ่มตามวิธีเรียกคีย์ของเกมรุ่นใหม่
- ย้ายการรับทิศทาง เดิน และกระโดดไปที่ `ClientInput.tick()` ของ 1.21.11 การเขียนสถานะจากสกิลเก็บคีย์วิ่งเดิมไว้ และให้เกมคำนวณความเร็วตอนย่อตามปกติ
- ปรับตัวส่งแพ็กเก็ตให้ใช้ Fabric `PlayerLookup` สำหรับผู้เล่นที่ติดตามชังก์นั้น และคงรหัสแพ็กเก็ตเดิม
- ย้ายการรับตำแหน่งระหว่างท่าต่อสู้ไปใช้ `InterpolationHandler` ของ 1.21.11 โดยคงรูปแบบแพ็กเก็ตเดิม รักษามุมหันที่เกมกำลังปรับ และใช้จำนวนทิกที่มากับแพ็กเก็ตเฉพาะการเคลื่อนที่รอบนั้น
- ปรับการลงทะเบียน Listener เป็น Fabric `ResourceLoader` พร้อมรักษาลำดับการโหลดที่กำหนด และย้ายตัวอ่าน JSON 12 ตัวไปยัง API แบบ `Codec`
- ย้ายการอ่านรายการอีโมตที่ผู้เล่นบันทึกไว้ไปยัง NBT และ registry API ของ 1.21.11 เก็บรูปแบบข้อมูลเดิมและอ่านรายการที่มีช่องเกินหรือ ID ที่ไม่ถูกต้องได้
- ย้าย Game Rules ทั้ง 13 รายการไปใช้ Fabric Game Rule API โดยใช้ชื่อแบบ `epicfight:weight_penalty` ในคำสั่งของเกม เก็บชื่อที่ใช้ในแพ็กเก็ตซิงก์เดิมไว้ และแปลงค่าในเซฟจากกฎรุ่นเก่าเมื่อเปิดเวิลด์
- อ่านสกิลที่ติดตั้ง สกิลที่เรียนไว้ และโหมดผู้เล่นด้วย NBT และ registry API ของ 1.21.11 เก็บคีย์และรูปแบบเซฟเดิมไว้
- ย้ายตัวลงทะเบียนไอเทมและสกิลไปใช้ Registry API ของ 1.21.11 ทั้งการค้นหา Holder และการเพิ่มรายการภายหลังใน Registry ที่ล็อกแล้ว ตัวเพิ่มรายการภายหลังรักษาแท็กของรายการเดิมไว้
- ย้ายจุดเรียกตัวสร้าง RenderType มาตรฐาน 36 จุดไปที่ `RenderTypes` ของ 1.21.11 ตรวจลายเซ็นที่ใช้ครบ 14 แบบด้วย `javac` กับคลาสเกมรุ่นเป้าหมาย
- ย้ายการวาดแถบ Stamina แถบชาร์จสกิล และแถบเกราะบอสไปใช้ GUI render pipeline ของ 1.21.11 ใช้เมทริกซ์ 2 มิติกับการเลื่อน HUD และส่งสีแถบ Stamina แยกในแต่ละคำสั่งวาด
- ย้ายอาวุธที่มีระดับวัสดุ 30 รายการและ Bokken ไปใช้ `ToolMaterial` และ item components คง ID เดิม ค่าพลังโจมตี ความเร็ว ความทน การซ่อม และระดับวัสดุที่ Epic Fight ใช้คำนวณโบนัสต่อสู้
- ย้ายเกราะ Stray และการคำนวณ weight กับ stun armor ไปใช้ `Equippable` และค่าป้องกันจาก item components คงชื่อ modifier ของช่องเกราะเดิมและสูตรคำนวณเดิม
- ย้าย collider, debug quad และ GUI triangle ไปใช้ `RenderPipeline` และ `RenderSetup` เปลี่ยนทางโหลด compute shader เป็น Fabric resource reload และปรับการเข้าถึง `GameRenderer.getFov`, `AbstractArrow.isInGround` และตัวสร้าง `RenderType` ให้ตรงกับ mappings 1.21.11

## เตรียมและตรวจซอร์ส

ใช้ Python 3.11 ขึ้นไป, Git และ JDK 21 สคริปต์ตรวจ SHA-256 ของ archive ต้นทาง สร้างซอร์สในโฟลเดอร์ใหม่ และใช้แพตช์ตามลำดับ ไฟล์แอสเซตและชุดทรัพยากรที่มากับต้นทางถูกตัดออกจากซอร์สที่สร้าง

```sh
python3 tools/prepare_fabric_port.py epicfight-fabric-work
cd epicfight-fabric-work
./gradlew clean build
```

บน Windows ใช้ `py -3 tools\prepare_fabric_port.py epicfight-fabric-work` แล้วรัน `gradlew.bat clean build` จากโฟลเดอร์ที่สร้าง สคริปต์รับ `--upstream-archive` สำหรับ archive ที่ดาวน์โหลดไว้แล้ว โดยตรวจ checksum เดียวกัน Gradle Wrapper ใช้ Gradle 9.5.1 และตรวจ SHA-256 ของไฟล์ Gradle ที่ดาวน์โหลด

GitHub Actions ชื่อ **Fabric 1.21.11 code build** รันบนสาขา `fabric-1.21.11` เมื่อบิลด์สำเร็จ เปิดหน้า Actions แล้วดาวน์โหลด `epicfight-fabric-1.21.11-code-only` จากส่วน Artifacts ได้ ไฟล์นี้ใช้ตรวจบิลด์ซอร์ส ส่วนแพ็กพร้อมเล่นต้องมีแอสเซตที่ได้รับอนุญาตและผ่านการทดสอบในเกม

## ผลทดสอบและสถานะ

- ซอร์ส Fabric 1.21.1 ต้นทางคอมไพล์ผ่านด้วย Gradle 9.5.1, Loom 1.17.19 และ Java 21
- การเตรียมซอร์ส 1.21.11 จาก archive ที่ตรึงเวอร์ชันผ่าน ตัวส่งแพ็กเก็ตและโค้ดปุ่มที่แก้ผ่านการคอมไพล์เฉพาะส่วนกับคลาสของ Minecraft 1.21.11 และ Fabric API
- ทดสอบการอ่านและเขียน `ClientInput` ด้วยคลาสเกม 1.21.11 ที่ Loom เปิดสิทธิ์เข้าถึงแล้ว ผ่านกรณีส่งค่าแกน ทิศทางหลบ กระโดด ย่อ รักษาคีย์วิ่ง และล็อกการเคลื่อนที่ ยืนยันว่าจุดเรียก `ClientInput.tick()` อยู่ใน `LocalPlayer.aiStep()`
- โค้ดซิงก์ตำแหน่งผ่าน GameTest แบบแยกบน Minecraft 1.21.11 และ Fabric Loader 0.19.3 ทดสอบการเคลื่อนที่ 1 และ 2 ทิก เป้าหมายที่ได้รับซ้ำ การหยุดเมื่อได้รับ 0 ทิก การเก็บมุมหัน และการคืนค่าจำนวนทิกปกติของเกม
- ตัวอ่านอีโมตผ่านการทดสอบในโปรแกรมทดสอบแยกด้วย NBT และ registry จริงของ Minecraft 1.21.11 มีตัวอย่างบันทึกแล้วอ่านกลับ ค่าเริ่มต้น ID ที่ไม่ถูกต้อง และรายการที่มีช่องเกิน
- ทดสอบ Game Rules ด้วยมอดทดสอบใน Fabric Loader 0.19.3 บน Minecraft 1.21.11 เข้าได้ถึงช่วงเริ่มต้นมอดและผ่านการลงทะเบียน การอ่านค่าจาก NBT ผ่าน `LevelSettings` และการเรียก callback ซิงก์ ส่วนการส่งแพ็กเก็ตให้ผู้เล่นจริงยังต้องทดสอบกับมอดเต็ม
- ตัวอ่านสกิลผ่านการทดสอบบันทึกและอ่านกลับด้วย NBT และ registry จริง รวมถึงกรณีข้อมูลขาดหายและ ID ที่ไม่ถูกต้อง
- ทดสอบตัวลงทะเบียนและ Holder ด้วยมอดทดสอบบน Fabric 1.21.11 ผ่านทั้งการเริ่มลงทะเบียน การเพิ่มหลังล็อก Registry การรักษาแท็กเก่า และการปฏิเสธ ID ซ้ำ
- `compileJava` ตรวจผ่าน `BattleModeGui` และคำสั่งวาดแถบเกราะที่แก้ การแสดงตำแหน่ง สี และภาพในเกมยังรอทดสอบกับ Epic Fight ตัวเต็ม
- GameTest บน Fabric 1.21.11 ลงทะเบียนชนิดอาวุธ Greatsword, Dagger, Longsword, Spear และ Tachi จากซอร์สจริง ตรวจค่าวัสดุ ความทน การซ่อม ค่าเสริมพลัง และค่าปรับของ Greatsword ผ่าน การใช้คอมโบในเกมต้องทดสอบกับมอดตัวเต็ม
- GameTest ของเกราะผ่านการตรวจช่องสวมใส่ ค่าป้องกัน แท็กซ่อมด้วย string และ equipment asset ของ Stray การตรวจ RenderPipeline ทั้งสามตัวผ่านใน JVM ด้วยคลาส Minecraft 1.21.11 การวาดในเกมและการประมวลผล compute shader ยังรอทดสอบ
- `processResources` ของ 1.21.11 ผ่าน การคอมไพล์ทั้งมอดยังติด API เรนเดอร์, Registry, NBT ในส่วนอื่น, mixin targets และมอดเสริม และ `validateAccessWidener` ยังพบสมาชิก Minecraft ที่ต้องย้าย จึงยังไม่มี JAR สำหรับเล่น การทดสอบคอมโบ แอนิเมชันและการซิงก์ระหว่างผู้เล่นต้องทำหลังได้ build ที่เปิดเกมได้
- Arclight ที่พบในเซิร์ฟเวอร์ Fala ฝัง Fabric Loader 0.19.2 ต้องทดสอบด้วย Arclight สำหรับ 1.21.11 ที่มี Loader ตรงตามข้อกำหนด และทดสอบร่วมกับ CustomFigura, Emotecraft และ Geyser ในเซิร์ฟเวอร์ทดสอบก่อนรวมแพ็กจริง [เวอร์ชันที่ Arclight ตรึงไว้](https://github.com/IzzelAliz/Arclight/blob/8a57510/gradle/libs.versions.toml#L34-L35)

## บิลด์มอดเสริม CustomFigura

ใช้ Gradle 9.5.1, JDK 21 และ JAR ของ CustomFigura 1.21.11 จากแพ็ก Fala `bridge-api/` มีอินเทอร์เฟซที่คอมไพล์เข้า Epic Fight ส่วนมอดเสริมใช้ไฟล์เดียวกันขณะคอมไพล์ โดย Fabric เรียกอินเทอร์เฟซจาก Epic Fight ตอนเปิดเกม

```sh
gradle -p figura-compat build -PfiguraJar=/path/to/figura-custom-0.1.6+1.21.11-metadatafix.jar
```

ไฟล์ออกที่ `figura-compat/build/libs/fala-figura-compat-0.1.0-alpha.1.jar` และต้องใช้คู่กับ Epic Fight พอร์ต `21.17.3-fala.2` และ CustomFigura `0.1.6+1.21.11` ในไคลเอนต์ มอดเสริมจะให้ Minecraft และ Figura เป็นผู้วาดผู้เล่นที่โหลดอวตารและมีตัวเรนเดอร์พร้อม ทั้งตัวละครในโลกและมุมมองบุคคลที่หนึ่ง ผู้เล่นคนอื่นยังใช้การเลือกโมเดลปกติของ Epic Fight

ทดสอบช่วงเริ่มต้นของ Fabric Client 1.21.11 ด้วย CustomFigura ของแพ็กและมอดทดสอบที่ใช้ API ของ Epic Fight แล้ว Fabric พบมอดเสริมเมื่อมีครบทั้งคู่ และแจ้ง dependency เมื่อขาดมอดที่ต้องใช้

JAR นี้เป็นรุ่นทดสอบ การเล่นด้วยทั้งสองมอดและการวาดอวตารในเกมยังรอบิลด์ Epic Fight ตัวเต็ม ส่วนการส่งท่าต่อสู้ไปยังกระดูกของอวตารเป็นงานเพิ่มเติม [Figura ExtraFight](https://modrinth.com/mod/figura_extrafight/versions), [Fightura](https://fightura.isaacdev.org/)

## สิทธิ์การใช้งาน

ซอร์ส Epic Fight ใช้ GPL-3.0 ส่วนโมเดล แอนิเมชัน ภาพ เสียง และทรัพยากรเดิมสงวนสิทธิ์ รุ่นสำหรับแจกต้องใช้แอสเซตที่ได้รับอนุญาตหรือที่โครงการมีสิทธิ์ใช้เอง [เงื่อนไขของ Epic Fight](https://github.com/Antikythera-Studios/epicfight/blob/866a2a1e4268d0d7897c6a5be4ef1e58e47d7443/README.md#license)

Equipment JSON ของ Stray ใช้ `assets/epicfight/textures/entity/equipment/humanoid/stray_cloth.png` และ `assets/epicfight/textures/entity/equipment/humanoid_leggings/stray_cloth.png` สำหรับเลเยอร์ตัวและขาตามลำดับ ให้วางภาพที่ได้รับอนุญาตไว้ตามสองพาธนี้ก่อนทดสอบการวาดเกราะ
