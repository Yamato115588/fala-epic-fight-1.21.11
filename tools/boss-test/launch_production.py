#!/usr/bin/env python3
"""Start a production Fabric JAR from previously downloaded, verified Minecraft files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from zipfile import ZipFile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("game-cache", "game-libs", "loader-libs", "loader-json", "assets", "java", "game-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--side", choices=("client", "server"), required=True)
    parser.add_argument("--username")
    parser.add_argument("--address", choices=("127.0.0.1:25584",))
    args = parser.parse_args()
    if args.side == "client" and (not args.address or not args.username):
        parser.error("a fixture username and the loopback address are required for the test client")
    args.game_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((args.game_cache / "mojang_minecraft_info.json").read_text())
    loader = json.loads(args.loader_json.read_text())
    entries = []
    for library in loader["libraries"]:
        group, name, version = library["name"].split(":")
        path = args.loader_libs / f"{name}-{version}.jar"
        if not path.is_file():
            raise FileNotFoundError(path)
        entries.append(str(path))
    archive = args.game_cache / f"minecraft-{args.side}.jar"
    assert hashlib.sha1(archive.read_bytes()).hexdigest() == manifest["downloads"][args.side]["sha1"]
    game_jar = archive
    if args.side == "server":
        with ZipFile(archive) as bundle:
            for section in ("libraries", "versions"):
                for line in bundle.read(f"META-INF/{section}.list").decode().splitlines():
                    checksum, identifier, relative = line.split("\t")
                    path = args.loader_libs / section / relative
                    data = bundle.read(f"META-INF/{section}/{relative}")
                    assert hashlib.sha256(data).hexdigest() == checksum
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
                        path.write_bytes(data)
                    entries.append(str(path))
                    if section == "versions":
                        game_jar = path
        game_args = ["net.fabricmc.loader.impl.launch.knot.KnotServer", "nogui"]
    else:
        asset_id = manifest["assetIndex"]["id"]
        index = args.assets / "indexes" / f"{asset_id}.json"
        if not index.is_file():
            index = args.assets / "indexes" / f"{manifest['id']}-{asset_id}.json"
        assert hashlib.sha1(index.read_bytes()).hexdigest() == manifest["assetIndex"]["sha1"]
        for name, asset in json.loads(index.read_text())["objects"].items():
            path = args.assets / "objects" / asset["hash"][:2] / asset["hash"]
            assert path.stat().st_size == asset["size"], name
            assert hashlib.sha1(path.read_bytes()).hexdigest() == asset["hash"], name
        for library in manifest["libraries"]:
            rules = library.get("rules", [])
            if rules and not any(rule["action"] == "allow" and
                                 rule.get("os", {}).get("name", "linux") == "linux" for rule in rules):
                continue
            artifact = library["downloads"]["artifact"]
            name = Path(artifact["path"]).name
            path = args.game_libs / name
            if not path.is_file():
                path = args.loader_libs / name
            assert hashlib.sha1(path.read_bytes()).hexdigest() == artifact["sha1"], name
            entries.append(str(path))
        entries.append(str(archive))
        game_args = ["net.fabricmc.loader.impl.launch.knot.KnotClient", "--gameDir", str(args.game_dir),
                     "--username", args.username, "--accessToken", "0", "--version", manifest["id"],
                     "--assetsDir", str(args.assets), "--assetIndex", index.stem,
                     "--width", "858", "--height", "492", "--quickPlayMultiplayer", args.address]
    command = [str(args.java), "-Xmx1600m", "-XX:ActiveProcessorCount=3",
               "-Djava.awt.headless=" + str(args.side == "server").lower(),
               "-Dfabric.gameJarPath=" + str(game_jar),
               "-cp", os.pathsep.join(dict.fromkeys(entries)), *game_args]
    return subprocess.call(command, cwd=args.game_dir)


if __name__ == "__main__":
    raise SystemExit(main())
