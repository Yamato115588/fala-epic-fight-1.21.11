# สถานะพอร์ต Epic Fight Fabric 1.21.11

งานต่อยอดอยู่บนสาขา `fabric-1.21.11` ของ Fala SiayaCraft ใช้ซอร์ส Epic Fight Fabric ที่ `866a2a1e4268d0d7897c6a5be4ef1e58e47d7443` เป็นฐานและตรวจ SHA-256 ของ archive ก่อนใช้แพตช์ สถานะก่อนเริ่มแก้คือ commit `fcb6bf0bba29dcba2f0fe3c951a4eaa55d9a2382` ซึ่ง `compileJava` รายงาน 2,521 รายการเมื่อขยายขีดจำกัดของ `javac` ตัวเลขนับข้อความวินิจฉัยและอาจมีหลายรายการจาก API ต้นเหตุเดียวกัน

## การตรวจล่าสุด

| การตรวจ | ผล |
| --- | --- |
| `compileJava` และ `clean build` | ยังติดการคอมไพล์ตัวมอดเต็ม 190 รายการจากการรันใน workspace ด้วย JDK 21 |
| `validateAccessWidener` | ผ่านกับ Minecraft 1.21.11 |
| `testPortData` | ผ่านการอ่านแอสเซต CC0, การให้ resource pack มีลำดับความสำคัญสูงกว่าไฟล์ใน JAR, โมเดลหนังสือสกิล, รูปแบบ NBT เดิมและ `ForgeData` |
| `testComputeRenderPass` | ผ่านการอ่านพิกเซลจาก Minecraft `RenderPass` 6 เฟรมบน Mesa llvmpipe ตรวจ skinning สองข้อต่อ, stride ของ Vanilla และ Iris, การซ่อนสามเหลี่ยมและการคืนช่วง SSBO |
| รอยอาวุธและอนุภาค | ผ่านการส่งตำแหน่ง สี UV และแสงเข้า `SubmitNodeStorage` และการสร้างสามเหลี่ยมฟ้าแลบด้วย `BufferBuilder` จริง |
| `runClient` และ `runServer` | ติด `compileJava` ก่อนเริ่ม Minecraft ตัวเต็ม |
| JAR และการเล่น | ยังไม่มี JAR ใน `build/libs` ที่ติดตั้งได้ จึงยังไม่มีผลทดสอบ Singleplayer, Multiplayer, dedicated server และ Fala Lite ร่วมกับมอดเต็ม |

GitHub Actions เรียก build, data test และกราฟิกทดสอบทุกครั้งที่ push สาขานี้ เมื่อ build ล้มเหลวให้เปิด `epicfight-compiler-diagnostics` ที่หน้า run เมื่อ build สำเร็จ workflow จะตรวจ remapped JAR และรายการแอสเซตก่อนอัปโหลด `epicfight-fabric-1.21.11` [GitHub Actions](https://github.com/Yamato115588/fala-epic-fight-1.21.11/actions/workflows/fabric-build.yml)

## ซอร์สและสิทธิ์

- พอร์ต GUI input และหน้าจอ HUD, registry และข้อมูลสูตรอาวุธ, API ฝั่งเซิร์ฟเวอร์สำหรับการต่อสู้และหลบ, การเก็บ NBT, การโหลดโมเดลไอเทม, particle render state และลำดับ depth pass สำหรับ afterimage
- ซอร์สที่ตรึงไว้ใช้ GPL-3.0 ทรัพยากรต้นฉบับภายใต้ `LICENSE-ASSETS` ถูกตัดออกตอนเตรียมซอร์สและตัวตรวจ JAR จะปฏิเสธไฟล์แอสเซตนอกบัญชี [LICENSE](https://github.com/Antikythera-Studios/epicfight/blob/866a2a1e4268d0d7897c6a5be4ef1e58e47d7443/LICENSE) · [LICENSE-ASSETS](https://github.com/Antikythera-Studios/epicfight/blob/866a2a1e4268d0d7897c6a5be4ef1e58e47d7443/LICENSE-ASSETS)
- ตัวสร้างใน `replacement-assets/` สร้างทรัพยากร CC0-1.0 จำนวน 41 รายการ ครอบคลุม rig ผู้เล่นแบบปกติและแขนเล็ก, คลิป 13 ท่า, โมเดลหนังสือสกิลหกแบบ, รอยอาวุธ, โมเดลอนุภาค, พื้นผิวเอฟเฟกต์และ compute shader รายการนี้ยังครอบคลุมเพียงส่วนหนึ่งของโมเดลและแอนิเมชันที่ตัวมอดลงทะเบียน
- `AssetResourceSource` ใช้ `ResourceProvider` ของ Fabric ก่อน แล้วจึงหาในไฟล์ที่บันเดิลไว้ เส้นทางแอนิเมชันฝั่งเซิร์ฟเวอร์ใช้ตัวอ่านเดียวกันและรายงานเมื่อหา asset ที่ต้องใช้ไม่พบ

## ทำซ้ำจากสาขาปัจจุบัน

ต้องมี Git, Python 3.11 ขึ้นไป และ JDK 21 การทดสอบกราฟิกต้องใช้ OpenGL 4.3 ขึ้นไป บน Linux ที่ไม่มีจอใช้ `xvfb-run` ตาม workflow

```bash
git clone --branch fabric-1.21.11 https://github.com/Yamato115588/fala-epic-fight-1.21.11.git
cd fala-epic-fight-1.21.11
git rev-parse HEAD
PORT_REPO=$(pwd)
python3 tools/prepare_fabric_port.py build/epicfight-1.21.11
cd build/epicfight-1.21.11
./gradlew -I "$PORT_REPO/tools/compiler-diagnostics.gradle" compileJava
./gradlew -I "$PORT_REPO/tools/compiler-diagnostics.gradle" --continue clean build
./gradlew --rerun-tasks validateAccessWidener
./gradlew -I "$PORT_REPO/tools/data-test/data.gradle" testPortData
LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a ./gradlew -I "$PORT_REPO/tools/renderpass-test/renderpass.gradle" testComputeRenderPass
./gradlew runClient
./gradlew runServer
python3 "$PORT_REPO/tools/check_fabric_jar.py" build/libs
```

ถ้ามี archive ที่ใช้ตรงกันให้ส่ง `--upstream-archive /path/to/archive.tar.gz` ให้สคริปต์เตรียมซอร์ส แก้ซอร์สในรูปแพตช์ตามลำดับใน `patches/` เพื่อให้ build ใหม่ทำซ้ำได้

## งานค้างที่ขวางการเปิดเกม

- ย้าย renderer ที่ยังใช้ entity/model ตรง ๆ ไปใช้ `EntityRenderState`, `SubmitNodeCollector` และ layer แบบใหม่ จุดหลักคือ `PresetRenderer`, `PatchedLivingEntityRenderer`, `WearableItemLayer`, `FirstPersonRenderer` และ Mixin เรนเดอร์ฝั่งไคลเอนต์
- ย้ายการวาด GUI ที่ยังพึ่ง Z offset, global shader state และ callback เก่าของรายการและ Grid ให้ผ่านระบบ GUI ของ 1.21.11
- ตรวจ optional adapters ของ Iris, Sodium, Wildfire และมอดอื่นตาม API รุ่นเป้าหมาย เมื่อ build ผ่านให้เปิดไคลเอนต์และ dedicated server แล้วตรวจ Mixin, การลงทะเบียน, การโหลดแอสเซต, คอมโบ, การหลบ, การซิงก์ระหว่างผู้เล่น และการเรนเดอร์ในโลกจริง
- ตรวจแพ็ก Fala Lite 24 มอดในอินสแตนซ์ทดสอบเมื่อมี JAR Epic Fight ที่เปิดเกมได้ และบันทึก SHA-256 ของแพ็กที่ใช้ทดสอบ
