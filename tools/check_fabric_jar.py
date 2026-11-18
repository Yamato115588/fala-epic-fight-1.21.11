#!/usr/bin/env python3
"""Print the path of the verified, intermediary-namespaced Fabric mod JAR."""

import argparse
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile


def check_jar(directory):
    excluded = ('-sources.jar', '-dev.jar', '-api.jar', '-javadoc.jar')
    jars = [jar for jar in directory.glob('*.jar') if not jar.name.endswith(excluded)]
    if len(jars) != 1:
        raise ValueError(f'Expected one remapped mod JAR in {directory}; found {len(jars)}')

    jar = jars[0]
    with ZipFile(jar) as archive:
        if error := archive.testzip():
            raise ValueError(f'JAR has an unreadable entry: {error}')
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
