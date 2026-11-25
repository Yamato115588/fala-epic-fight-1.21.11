"""Compile the pinned, unmodified upstream math sources and compare the same inputs."""
from pathlib import Path
import os, subprocess, sys, tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_fabric_port import extract_code
def main():
    archive, cp_file = map(Path,sys.argv[1:3])
    cp = cp_file.read_text().strip()
    javac=Path(os.environ['JAVA_HOME'])/'bin/javac'
    java=javac.with_name('java')
    runner=Path(__file__).with_name('MatrixScenario.java')
    with tempfile.TemporaryDirectory() as tmp:
        work=Path(tmp);code=work/'source';code.mkdir();extract_code(archive,code)
        original=work/'official';original.mkdir();fixture=work/'fixtures';fixture.mkdir()
        math=code/'src/main/java/yesman/epicfight/api/utils/math'
        subprocess.run([javac,'-proc:none','-cp',cp,'-d',original,math/'OpenMatrix4f.java',math/'Vec3f.java',math/'Vec4f.java'],check=True)
        subprocess.run([javac,'-proc:none','-cp',cp,'-d',fixture,runner],check=True)
        def run(paths):
            result=subprocess.check_output([java,'-cp',os.pathsep.join(map(str,[fixture,*paths,cp])),'MatrixScenario'],text=True)
            return next(s for s in result.splitlines() if s.startswith('4096 poses '))
        reference=run([original])
        target=run([])
        if target!=reference:raise AssertionError((reference,target))
        print('PASS official Fabric / V3 matrix outputs match bit-for-bit:',target)
if __name__=='__main__':main()
