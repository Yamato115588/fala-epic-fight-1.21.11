"""Stage the locked mod directories for a new, isolated Fabric QA profile."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parent


def digest(path, algorithm="sha256"):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def obtain(source, index, row, path, args):
    if row.get("local_build"):
        shutil.copyfile(args.local_builds / row["name"], path)
        return
    if "archive_entry" in row:
        with source.open(row["archive_entry"]) as entry, path.open("wb") as out:
            shutil.copyfileobj(entry, out)
        return
    if "index_path" in row:
        entry = index[row["index_path"]]
        url, checksum = entry["downloads"][0], entry["hashes"]["sha512"]
    else:
        url, checksum = row["url"], row["download_sha512"]
    cached = args.cache / checksum if args.cache else None
    if cached and cached.is_file():
        shutil.copyfile(cached, path)
    else:
        if args.offline or urlsplit(url).scheme != "https":
            raise ValueError(f"Missing cached download for {row['name']}")
        request = Request(url, headers={"User-Agent": "Fala-SiayaCraft-QA/3"})
        with urlopen(request, timeout=60) as stream, path.open("wb") as out:
            shutil.copyfileobj(stream, out)
    if digest(path, "sha512") != checksum:
        raise ValueError(f"Invalid download SHA-512 for {row['name']}")


def stage(args):
    lock = json.loads((ROOT / "roleplay-inventory.json").read_text())
    if digest(args.mrpack) != lock["base_sha256"]:
        raise ValueError("Base mrpack SHA-256 mismatch")
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as temp, zipfile.ZipFile(args.mrpack) as source:
        temp = Path(temp)
        staged = temp / "profile"
        for side in ["client", "server"]:
            (staged / side / "mods").mkdir(parents=True)
        index = {r["path"]: r for r in json.loads(source.read("modrinth.index.json"))["files"]}
        names, ids = set(), set()
        for row in lock["mods"]:
            name, mod_id = row["name"], row["id"]
            if name != Path(name).name or name.casefold() in names or mod_id in ids:
                raise ValueError(f"Duplicate or invalid mod {name} ({mod_id})")
            names.add(name.casefold())
            ids.add(mod_id)
            if row["side"] not in {"client", "both", "server"}:
                raise ValueError(f"Unknown environment for {mod_id}")
            file = temp / name
            obtain(source, index, row, file, args)
            if row.get("base_file"):
                if digest(file) != row["base_sha256"]:
                    raise ValueError(f"Unexpected patch input for {name}")
                if not args.java_home or not args.asm_classpath:
                    raise ValueError("The locked e4mc adaptation needs --java-home and --asm-classpath")
                original = temp / "e4mc-original.jar"
                file.rename(original)
                subprocess.run([sys.executable, str(ROOT / "e4mc/patch.py"), str(original),
                                str(file), args.java_home, args.asm_classpath], check=True)
            if digest(file) != row["sha256"]:
                raise ValueError(f"Installed SHA-256 mismatch for {name}")
            with zipfile.ZipFile(file) as jar:
                meta = json.loads(jar.read("fabric.mod.json"), strict=False)
            if meta["id"] != mod_id or meta["version"] != row["version"]:
                raise ValueError(f"Fabric metadata mismatch for {name}")
            for side in ("client", "server"):
                if row["side"] in {side, "both"}:
                    os.link(file, staged / side / "mods" / name)
        # Preserve even an empty pre-existing profile if a concurrent caller created it.
        args.output.mkdir()
        try:
            for side in ("client", "server"):
                (staged / side).rename(args.output / side)
        except BaseException:
            for side in ("client", "server"):
                published = args.output / side
                if published.is_dir() and not (staged / side).exists():
                    published.rename(staged / side)
            args.output.rmdir()
            raise
    print("Verified " + ", ".join(f"{len(list((args.output / side / 'mods').glob('*.jar')))} {side}"
                                  for side in ["client", "server"]) + " mods")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mrpack", type=Path)
    parser.add_argument("output", type=Path, help="New directory for the staged mod files")
    parser.add_argument("--cache", type=Path, help="Existing downloads named by SHA-512")
    parser.add_argument("--local-builds", type=Path, required=True, help="Directory with both SHA-pinned QA builds")
    parser.add_argument("--java-home", default=os.environ.get("JAVA_HOME"))
    parser.add_argument("--asm-classpath", default=os.environ.get("ASM_CLASSPATH"), help="ASM and asm-tree 9.x jars")
    parser.add_argument("--offline", action="store_true")
    stage(parser.parse_args())
