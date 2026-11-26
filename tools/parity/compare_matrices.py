"""Compare pinned upstream algorithms and port bytecode on the same target runtime."""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_fabric_port import extract_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("classpath_file", type=Path)
    parser.add_argument("--animation-only", action="store_true")
    args = parser.parse_args()
    archive, cp_file = args.archive, args.classpath_file
    classpath = cp_file.read_text().strip()
    javac = Path(os.environ["JAVA_HOME"]) / "bin/javac"
    java = javac.with_name("java")
    cases = {"MatrixScenario": "4096 poses ", "AnimationScenario": "2112 animation samples "}
    if args.animation_only:
        del cases["MatrixScenario"]
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        code, original, fixture = (work / name for name in ("source", "official", "fixtures"))
        for folder in (code, original, fixture):
            folder.mkdir()
        extract_code(archive, code)
        api = code / "src/main/java/yesman/epicfight/api"
        classes = [api / "utils/math" / (s + ".java") for s in ("OpenMatrix4f", "Vec3f", "Vec4f")]
        classes += [api / "animation" / (s + ".java") for s in ("Keyframe", "JointTransform", "TransformSheet", "Pose")]
        subprocess.run([javac, "-proc:none", "-cp", classpath, "-d", original, *classes], check=True)
        runners = [Path(__file__).with_name(name + ".java") for name in cases]
        subprocess.run([javac, "-proc:none", "-cp", classpath, "-d", fixture, *runners], check=True)
        for name, prefix in cases.items():
            def run(entries, reference):
                cmd = [java, "-cp", os.pathsep.join(map(str, entries)), name]
                if name == "AnimationScenario":
                    cmd.extend([str(original), str(reference).lower()])
                output = subprocess.check_output(cmd, text=True, cwd=work)
                return next(line for line in output.splitlines() if line.startswith(prefix))
            reference = run([fixture, original, classpath], True)
            target = run([fixture, classpath], False)
            if target != reference:
                raise AssertionError((name, reference, target))
            print("PASS official Fabric / V3 outputs match bit-for-bit:", target)


if __name__ == "__main__":
    main()
