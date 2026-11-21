from pathlib import Path
import argparse
import ctypes
import hashlib
import io
import json
import os
import shutil
import signal
import struct
import subprocess
import sys
import time
from zipfile import ZipFile

parser = argparse.ArgumentParser(description="Observe boss AI transitions with two production Fabric clients on loopback.")
for name in ("jar", "probe", "pack", "mod-cache", "eula-file", "output", "game-cache", "game-libs",
             "loader-libs", "loader-json", "assets", "java", "xvfb"):
    parser.add_argument("--" + name, type=Path, required=True)
parser.add_argument("--xvfb-library", type=Path)
parser.add_argument("--xvfb-tcp", action="store_true", help="Use cookie-authenticated TCP when Unix sockets are unavailable")
args = parser.parse_args()
for key, value in vars(args).items():
    if isinstance(value, Path):
        setattr(args, key, value.resolve())
repo = Path(__file__).resolve().parents[2]
root = args.output
proof = root / "logs"
jar, probe = args.jar, args.probe
launch = Path(__file__).with_name("launch_production.py")
processes = []
env = dict(os.environ, LIBGL_ALWAYS_SOFTWARE="1", ALSOFT_DRIVERS="null", LP_NUM_THREADS="2")


def read(path):
    return path.read_text(errors="replace") if path.exists() else ""


def start(command, name, console=False):
    log = proof / (name + ".log")
    with log.open("w") as out:
        process = subprocess.Popen(command, env=env, stdout=out, stderr=subprocess.STDOUT,
                                   stdin=subprocess.PIPE if console else None, start_new_session=True)
    processes.append(process)
    if console:
        process.stdin = io.TextIOWrapper(process.stdin, encoding="utf-8", write_through=True)
    return process, log


def wait(process, file, marker, timeout, offset=0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        contents = read(file)[offset:]
        if marker in contents:
            return contents
        if process.poll() is not None or "FALA_NATURAL ERROR" in contents:
            raise RuntimeError(f"{file.name} failed before {marker}")
        time.sleep(.5)
    excerpt = "\n".join(line for line in contents.splitlines() if "FALA_NATURAL " in line)
    raise RuntimeError(f"{file.name} exceeded {timeout}s waiting for {marker}\n"
                       + "\n".join(excerpt.splitlines()[-6:]))


def send(command):
    server.stdin.write(command + "\n")
    server.stdin.flush()


def action(command):
    offset = len(read(server_log))
    pending = root / "server/.natural-next"
    pending.write_text(command)
    pending.replace(root / "server/fala-natural-command")
    wait(server, server_log, "FALA_NATURAL command " + command + " complete", 12, offset)


def clients_have(marker, seconds=35):
    for process, log in ((client, client_log), (peer, peer_log)):
        wait(process, log, marker, seconds)
    print("Observed on both clients", marker, flush=True)


def exercise_combat():
    send("fill -6 79 -6 6 79 6 minecraft:stone")
    send("tp FalaNaturalA 0.5 80 0.5 0 12")
    send("item replace entity FalaNaturalA weapon.mainhand with minecraft:iron_sword")
    send("epicfight skill add FalaNaturalA dodge epicfight:roll")
    send("epicfight mode epicfight FalaNaturalA")
    send('summon minecraft:cow 0.5 80 1.4 {NoAI:1b,Tags:["fala_combat_target"]}')
    wait(server, server_log, "combat target health 10.0", 12)
    time.sleep(2)

    x11 = ctypes.CDLL("libX11.so.6")
    xtest = ctypes.CDLL("libXtst.so.6")
    x11.XOpenDisplay.restype = ctypes.c_void_p
    os.environ["XAUTHORITY"] = env["XAUTHORITY"]
    handle = ctypes.c_void_p(x11.XOpenDisplay(env["DISPLAY"].encode()))
    if not handle:
        raise RuntimeError("Cannot send combat input to Xvfb")
    try:
        for _ in range(7):
            xtest.XTestFakeButtonEvent(handle, 1, 1, 0)
            x11.XFlush(handle)
            time.sleep(.06)
            xtest.XTestFakeButtonEvent(handle, 1, 0, 0)
            x11.XFlush(handle)
            time.sleep(.36)
        for index in (1, 2, 3):
            wait(server, server_log, f"combat animation epicfight:biped/combat/sword_auto{index}", 10)
        wait(server, server_log, "combat target health 0.0", 10)
        time.sleep(1.2)
        keys = [x11.XKeysymToKeycode(handle, key) for key in (ord("w"), 0xffe9)]
        for pressed in (1, 0):
            for key in keys:
                xtest.XTestFakeKeyEvent(handle, key, pressed, 0)
            x11.XFlush(handle)
            time.sleep(.2)
        wait(server, server_log, "combat animation epicfight:biped/skill/roll_forward", 10)
    finally:
        x11.XCloseDisplay(handle)
    for sound in ("entity.weapon.whoosh", "entity.hit.blade", "skill.roll"):
        wait(client, client_log, "sound epicfight:" + sound, 10)
    assert "Missing resource epicfight:textures/gui/skills/weapon_innate/sweeping_edge.png" not in read(client_log)
    print("Combat: three sword animations, target 10 -> 0 HP, forward roll and sound events", flush=True)


def display_authority():
    # Use one private cookie for this display. FamilyWild allows auto-selection of the display number.
    cookie = os.urandom(16)
    authority = proof / "Xauthority"
    with os.fdopen(os.open(authority, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb") as output:
        for number in range(64):
            output.write(struct.pack("!H", 65535))
            for field in (b"", str(number).encode(), b"MIT-MAGIC-COOKIE-1", cookie):
                output.write(struct.pack("!H", len(field)) + field)
    env["XAUTHORITY"] = str(authority)
    return authority


def setup():
    if root.exists():
        raise ValueError("Choose a new output directory for each run")
    assert "eula=true" in args.eula_file.read_text().splitlines(), "An accepted test-server EULA file is required"
    assert hashlib.sha256(args.pack.read_bytes()).hexdigest() == (
        "2676674d1ce000613129d948cd77344e71393994c0704b4e7f597ea91af04415"), "Unexpected Fala Lite pack"
    with ZipFile(args.pack) as bundle:
        index = json.loads(bundle.read("modrinth.index.json"))
        for item in index["files"]:
            file = args.mod_cache / Path(item["path"]).name
            data = file.read_bytes()
            assert len(data) == item["fileSize"], item["path"]
            assert all(hashlib.new(algorithm, data).hexdigest() == digest
                       for algorithm, digest in item["hashes"].items()), item["path"]
        for name in bundle.namelist():
            if name.startswith("overrides/mods/") and name.endswith(".jar"):
                assert bundle.read(name) == (args.mod_cache / Path(name).name).read_bytes(), name
        proof.mkdir(parents=True)
        for name in bundle.namelist():
            if not name.startswith("overrides/") or name.endswith("/") or name.startswith("overrides/mods/"):
                continue
            path = Path(name.removeprefix("overrides/"))
            assert not path.is_absolute() and ".." not in path.parts
            for slot in ("server", "client", "client-peer"):
                dest = root / slot / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(bundle.read(name))
    for slot in ("server", "client", "client-peer"):
        dest = root / slot
        (dest / "mods").mkdir(parents=True, exist_ok=True)
        expected = repo / "test-evidence" / ("lite-server.sha256" if slot == "server" else "lite-client.sha256")
        for line in expected.read_text().splitlines():
            checksum, name = line.split(maxsplit=1)
            source = args.mod_cache / name
            assert hashlib.sha256(source.read_bytes()).hexdigest() == checksum, name
            shutil.copyfile(source, dest / "mods" / name)
        shutil.copyfile(jar, dest / "mods" / jar.name)
        shutil.copyfile(probe, dest / "mods" / probe.name)
        if slot != "server":
            (dest / "options.txt").write_text(
                "onboardAccessibility:false\nrenderDistance:6\nsimulationDistance:5\n"
                "pauseOnLostFocus:false\nmaxFps:45\nlang:en_us\n")
    shutil.copyfile(args.eula_file, root / "server/eula.txt")
    (root / "server/server.properties").write_text(
        "server-ip=127.0.0.1\nserver-port=25584\nonline-mode=false\n"
        "level-name=NaturalWorld\nlevel-seed=6572230548342028088\nlevel-type=minecraft\\:flat\nview-distance=8\n"
        "simulation-distance=5\nspawn-protection=0\nmotd=Fala authorized loopback test\n")


def command(side, slot, username="FalaNaturalA"):
    command = [sys.executable, str(launch)]
    for name in ("game-cache", "game-libs", "loader-libs", "loader-json", "assets", "java"):
        command.extend(["--" + name, str(getattr(args, name.replace("-", "_")))])
    return command + ["--side", side, "--game-dir", str(root / slot),
                      "--username", username, "--address", "127.0.0.1:25584"]


setup()
authority = display_authority()
transport = (["-listen", "tcp", "-nolisten", "unix", "-nolisten", "local"]
             if args.xvfb_tcp else ["-nolisten", "tcp"])
display_file = proof / "display-id"
with display_file.open("wb") as fd, (proof / "display.log").open("w") as out:
    display = subprocess.Popen(
        [str(args.xvfb), "-displayfd", str(fd.fileno()), "-screen", "0", "1024x768x24",
         "-auth", str(authority), *transport],
        pass_fds=(fd.fileno(),), stdout=out, stderr=subprocess.STDOUT,
        env=env | ({"LD_LIBRARY_PATH": str(args.xvfb_library)} if args.xvfb_library else {}),
        start_new_session=True)
processes.append(display)
try:
    for attempt in range(60):
        if display.poll() is not None:
            raise RuntimeError("Xvfb terminated during startup")
        number = read(display_file).strip()
        if number:
            env["DISPLAY"] = ("127.0.0.1:" if args.xvfb_tcp else ":") + number
            break
        time.sleep(.1)
    else:
        raise RuntimeError("Xvfb did not become ready")
    print("Production JAR SHA-256", hashlib.sha256(jar.read_bytes()).hexdigest(), flush=True)
    server, server_log = start(command("server", "server"), "server", console=True)
    wait(server, server_log, "Done (", 120)
    client, client_log = start(command("client", "client"), "client")
    wait(client, client_log, "ready FalaNaturalA", 120)
    exercise_combat()
    peer, peer_log = start(command("client", "client-peer", "FalaNaturalB"), "peer")
    wait(peer, peer_log, "ready FalaNaturalB", 120)
    print("Fala Lite 24 JARs on both clients connected", flush=True)
    clients_have("particle dust_contractive created")
    send("gamemode creative @a")
    send("execute in minecraft:the_end run tp @a 0.5 80 13.5 180 20")
    send("execute in minecraft:the_end run fill -22 60 -22 22 60 22 minecraft:obsidian")
    send("gamemode survival FalaNaturalA")
    send("effect give FalaNaturalA minecraft:resistance infinite 255 true")
    send("effect give FalaNaturalA minecraft:regeneration infinite 10 true")
    send("effect give FalaNaturalA minecraft:slow_falling infinite 0 true")
    time.sleep(8)
    action("start")
    wait(server, server_log, "dragon Ground Battle", 200)
    clients_have("dragon Ground Battle")
    clients_have("dragon IK active")
    offset = len(read(server_log))
    action("wound")
    wait(server, server_log, "dragon Crystal Link", 40, offset)
    clients_have("dragon Crystal Link")
    print("Natural crystal charging", flush=True)
    offset = len(read(server_log))
    wait(server, server_log, "dragon Ground Battle", 30, offset)
    time.sleep(1)
    offset = len(read(server_log))
    action("wound")
    wait(server, server_log, "dragon Crystal Link", 35, offset)
    time.sleep(1)
    action("interrupt")
    wait(server, server_log, "dragon Neutralized", 30)
    clients_have("dragon Neutralized")
    offset = len(read(server_log))
    clients_have("dragon animation epicfight:dragon/neutralized_recovery", 20)
    wait(server, server_log, "dragon Flying", 30, offset)
    clients_have("dragon animation epicfight:dragon/ground_to_fly")
    time.sleep(1)
    action("dragon-death")
    clients_have("dragon death true")
    time.sleep(11)

    send("execute in minecraft:the_end run fill -7 69 -4 7 69 10 minecraft:obsidian")
    send("execute in minecraft:the_end run tp @a 0.5 70 6.5 180 0")
    send('execute in minecraft:the_end run summon minecraft:wither 0.5 71 2.5 {Tags:["fala_natural"]}')
    time.sleep(3)
    action("wither-wound")
    wait(server, server_log, "wither armor true", 30)
    clients_have("wither armor true")
    clients_have("wither ghost true", 40)
    clients_have("wither clone", 20)
    clients_have("wither animation epicfight:wither/laser", 80)
    clients_have("sound epicfight:sfx.laser_blast", 20)
    time.sleep(3)
    action("wither-death")
    clients_have("wither death true")
    time.sleep(4)
    if client.poll() is not None or peer.poll() is not None:
        raise RuntimeError("A client quit before the scenario completed")
    send("stop")
    if server.wait(timeout=30) != 0:
        raise RuntimeError("The dedicated server exited with an error")
    markers = ("dragon Flying", "dragon Airstrike", "dragon Landing", "dragon Ground Battle",
               "dragon Crystal Link", "dragon Neutralized", "dragon IK active", "dragon death true",
               "dragon animation epicfight:dragon/neutralized_recovery",
               "dragon animation epicfight:dragon/ground_to_fly",
               "particle dust_contractive created", "wither armor true", "wither ghost true",
               "wither clone", "wither lasers 3", "wither death true",
               "sound epicfight:sfx.laser_blast", "sound epicfight:entity.enderdragon.dragon_breath")
    for log in (client_log, peer_log):
        contents = read(log)
        missing = [marker for marker in markers if marker not in contents]
        assert not missing, f"{log.name} missing {missing}"
        assert "FALA_NATURAL ERROR" not in contents, log.name
        assert "Encountered an unexpected exception" not in contents, log.name
        assert "Minecraft has crashed!" not in contents, log.name
    assert "FALA_NATURAL ERROR" not in read(server_log)
    result = {"jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
              "pack_sha256": hashlib.sha256(args.pack.read_bytes()).hexdigest(),
              "client_pack_jars": 24, "server_pack_jars": 20, "clients": 2,
              "combat": ["sword_auto1", "sword_auto2", "sword_auto3", "target HP 10 -> 0", "roll_forward",
                         "weapon whoosh, blade hit and roll sound events"],
              "markers": list(markers), "authenticated_multiplayer": "NOT TESTED",
              "inputs": ["world seeded and three crystals retained", "normal head damage",
                         "stun-impact API", "normal lethal damage"]}
    (proof / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Natural boss scenarios completed", flush=True)
finally:
    for process in reversed(processes):
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=6)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    authority.unlink()
