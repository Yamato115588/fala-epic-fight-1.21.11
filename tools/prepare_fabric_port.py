#!/usr/bin/env python3
"""Prepare the pinned, code-only Epic Fight Fabric 1.21.11 port workspace."""

import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile
from urllib.request import urlopen

from migrate_mojmap import migrate


UPSTREAM = '866a2a1e4268d0d7897c6a5be4ef1e58e47d7443'
ARCHIVE_SHA256 = '4a50f322d45fbf53f65cf8733b79c7c23676a1f28475561b73f698cf30b021c7'
UPSTREAM_URL = f'https://codeload.github.com/Antikythera-Studios/epicfight/tar.gz/{UPSTREAM}'
PROJECT = Path(__file__).resolve().parents[1]
BUILD_FILES = {
    'build.gradle', 'settings.gradle', 'gradle.properties', 'gradlew', 'gradlew.bat',
    'LICENSE', 'LICENSE-ASSETS', 'README.md',
}


def extract_code(archive, destination):
    with archive.open('rb') as source:
        if hashlib.file_digest(source, 'sha256').hexdigest() != ARCHIVE_SHA256:
            raise ValueError('Upstream archive checksum does not match the pinned commit')

    with tarfile.open(archive, 'r:gz') as source:
        for entry in source:
            path = PurePosixPath(entry.name)
            if path.is_absolute() or '..' in path.parts or not path.parts:
                raise ValueError(f'Invalid upstream archive path: {entry.name}')
            if path.parts[0] != f'epicfight-{UPSTREAM}':
                raise ValueError(f'Unexpected upstream archive root: {path.parts[0]}')
            parts = path.parts[1:]
            if not parts or entry.isdir():
                continue
            if parts[0] not in ('src', 'gradle') and (len(parts) != 1 or parts[0] not in BUILD_FILES):
                continue
            if parts[0] == 'src' and parts[2:3] == ('resources',) and (
                'assets' in parts[3:] or 'resourcepacks' in parts[3:]
            ):
                continue
            if not entry.isfile():
                raise ValueError(f'Expected an ordinary source file: {entry.name}')
            target = destination.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.extractfile(entry) as contents, target.open('xb') as output:
                shutil.copyfileobj(contents, output)
            if entry.mode & 0o100:
                target.chmod(0o755)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New directory for the generated Gradle project')
    parser.add_argument('--upstream-archive', type=Path, help='Use the pinned tar.gz from disk')
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        parser.error('Choose a new output directory')
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='.epicfight-port-', dir=output.parent) as temporary:
        temporary = Path(temporary)
        archive = args.upstream_archive
        if archive is None:
            archive = temporary / 'upstream.tar.gz'
            with urlopen(UPSTREAM_URL, timeout=60) as response, archive.open('wb') as target:
                shutil.copyfileobj(response, target)
        stage = temporary / 'source'
        stage.mkdir()
        extract_code(archive, stage)
        # Apply against the extracted tree even when output is inside the checkout.
        patch_env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(temporary))
        for patch in sorted((PROJECT / 'patches').glob('*.patch')):
            subprocess.run(
                ['git', '-c', 'core.whitespace=trailing-space,space-before-tab,cr-at-eol',
                 'apply', '--whitespace=error', str(patch)],
                cwd=stage, env=patch_env, check=True,
            )
        shutil.copytree(PROJECT / 'bridge-api/src/main/java', stage / 'src/main/java',
                        dirs_exist_ok=True)
        migrated = migrate(stage)
        stage.rename(output)
        print(f'Prepared {output}; updated Minecraft class references in {migrated} Java files.')


if __name__ == '__main__':
    main()
