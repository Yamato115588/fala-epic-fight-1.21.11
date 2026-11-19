#!/usr/bin/env python3
"""Print the path of the verified, intermediary-namespaced Fabric mod JAR."""

import argparse
import json
from hashlib import sha256
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import BadZipFile, ZipFile


# Resources introduced by the earlier port patches, before the replacement artwork.
PORT_ASSETS = {
    'assets/epicfight/equipment/stray_cloth.json': '5a6fbd02c80121efc3ceefdff86c4c56dc9ffc57b72ec652ec5c213de4a5a063',
    'assets/epicfight/shaders/compute/vertex_buffer_pack.comp': '2ef532869127b6a1a0e2f0bd820d753373013c09b9933a41fe39e12ac8b3171e',
    'assets/epicfight/shaders/core/colored_glint.fsh': '6c27439b55072adad1a6aa8b899ab85ae7a6929bff2a7b612f9fe5f1fba9f4ad',
    'assets/epicfight/shaders/core/preview_model.fsh': 'f5c1a6cc9cf585b44bb2c6face834b149c2016d1424a67d9d463e8a428d1f360',
    'assets/epicfight/shaders/core/preview_model.vsh': 'be2328e518014a0967ae0c2320acc741fe67eab81ccbc8866b708d0f0ed30fd2'
}

def check_asset_entries(archive):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = Path(__file__).resolve().parents[1] / 'replacement-assets/build_assets.py'
        subprocess.run([sys.executable, str(source), str(root)], check=True)
        expected = dict(PORT_ASSETS)
        for entry in root.rglob('*'):
            if entry.is_file():
                expected[entry.relative_to(root).as_posix()] = sha256(entry.read_bytes()).hexdigest()
        listed = [entry.filename for entry in archive.infolist() if not entry.is_dir() and
                  entry.filename.startswith(('assets/', 'resourcepacks/', 'META-INF/fala-replacement-assets/'))]
        if len(listed) != len(set(listed)) or set(listed) != expected.keys():
            raise ValueError('Unexpected, duplicate or missing packaged assets: ' +
                             str(sorted(set(listed) ^ expected.keys())))
        for name, digest in expected.items():
            if sha256(archive.read(name)).hexdigest() != digest:
                raise ValueError(f'Packaged asset differs from its reviewed source: {name}')


def check_jar(directory):
    excluded = ('-sources.jar', '-dev.jar', '-api.jar', '-javadoc.jar')
    jars = [jar for jar in directory.glob('*.jar') if not jar.name.endswith(excluded)]
    if len(jars) != 1:
        raise ValueError(f'Expected one remapped mod JAR in {directory}; found {len(jars)}')

    jar = jars[0]
    with ZipFile(jar) as archive:
        if error := archive.testzip():
            raise ValueError(f'JAR has an unreadable entry: {error}')
        check_asset_entries(archive)
        metadata = json.loads(archive.read('fabric.mod.json'))
        if metadata['id'] != 'epicfight' or metadata['depends']['minecraft'] != '=1.21.11':
            raise ValueError('Unexpected Fabric mod ID or Minecraft version')
        if not {'fabricloader', 'fabric-api', 'java'} <= metadata['depends'].keys():
            raise ValueError('Fabric, Fabric API or Java dependency is missing')
        for side in ('main', 'client'):
            for entrypoint in metadata['entrypoints'][side]:
                archive.getinfo(entrypoint.replace('.', '/') + '.class')
        widener = archive.read(metadata['accessWidener']).splitlines()[0].split()
        if widener != [b'accessWidener', b'v2', b'intermediary']:
            raise ValueError('The JAR access widener is not remapped to intermediary')

    return jar.resolve()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    try:
        print(check_jar(args.directory))
    except (OSError, ValueError, KeyError, IndexError, BadZipFile) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
