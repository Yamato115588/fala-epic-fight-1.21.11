#!/usr/bin/env python3
"""Release the already-tested b7875ca binary; never rebuild or alter that JAR."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

REPO = 'Yamato115588/fala-epic-fight-1.21.11'
BASE = f'repos/{REPO}'
COMMIT = 'b7875ca3b1ed15ddec14f64d9466a040f2aba52a'
RUN = 44862928688
ARTIFACT = 14690119140
RELEASE = 456413733
TAG = 'v0.1.0-beta'
JAR_SHA = '034d5f19c96f4bdd28c06299bc7d1cf73d070a70dcc5d9186a00a8f9a36c90ff'
ZIP_SHA = '8eb408faeee23c1040c64fa2fd4b364168bf6407bad33c7d8aa384977fbf4ccc'
JAR_NAME = 'epicfight-fabric-1.21.11-beta-0.1.0.jar'
NIGHT_COMMIT = '64a63d7aa37b6cd7bf1a889b0356dc6dfcad6d4e'
NIGHT_SHA = '4fbfd61545cad39f0bfd0eaeca3dd9ac86df22ef9cfb0db8cea72255588a66fc'
DOCS = Path(__file__).resolve().parent


def gh(*args):
    return subprocess.check_output(['gh', *args])


def api(path):
    return json.loads(gh('api', path))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(archive, destination):
    destination.mkdir()
    with tarfile.open(archive) as tar:
        roots = {Path(e.name).parts[0] for e in tar.getmembers()}
        assert len(roots) == 1, roots
        tar.extractall(destination, filter='data')
    return destination / roots.pop()


def check_release(release):
    assert release['id'] == RELEASE and release['tag_name'] == TAG
    assert release['target_commitish'] == COMMIT and release['prerelease']


def main():
    run = api(f'{BASE}/actions/runs/{RUN}')
    assert run['head_sha'] == COMMIT and run['conclusion'] == 'success'
    artifact = api(f'{BASE}/actions/artifacts/{ARTIFACT}')
    assert artifact['workflow_run']['id'] == RUN and not artifact['expired']
    assert artifact['digest'] == 'sha256:' + ZIP_SHA
    release = api(f'{BASE}/releases/{RELEASE}')
    check_release(release)
    if not release['draft']:
        assets = {a['name']: a for a in release['assets']}
        assert assets[JAR_NAME]['digest'] == 'sha256:' + JAR_SHA
        assert {'SHA256SUMS.txt', 'INSTALL-TH.md', 'THIRD-PARTY-NOTICES.txt',
                'epicfight-fabric-1.21.11-beta-0.1.0-source.tar.gz'} <= assets.keys()
        print('Release already published:', release['html_url'])
        return

    with tempfile.TemporaryDirectory(prefix='verified-beta-') as tmp:
        work = Path(tmp)
        archive = work / 'artifact.zip'
        archive.write_bytes(gh('api', f'{BASE}/actions/artifacts/{ARTIFACT}/zip'))
        assert digest(archive) == ZIP_SHA
        binary = work / 'binary'
        binary.mkdir()
        with zipfile.ZipFile(archive) as zipf:
            assert len(zipf.namelist()) == 2
            for name in zipf.namelist():
                assert Path(name).name == name
                (binary / name).write_bytes(zipf.read(name))
        jar, = binary.glob('*.jar')
        assert digest(jar) == JAR_SHA
        assert (binary / (jar.name + '.sha256')).read_text().split()[0] == JAR_SHA

        source_tar = work / 'port.tar.gz'
        source_tar.write_bytes(gh('api', f'{BASE}/tarball/{COMMIT}'))
        recipe = extract(source_tar, work / 'recipe')
        evidence = json.loads((recipe / 'test-evidence/lite-lifecycle.json').read_text())
        assert evidence['jar_sha256'] == JAR_SHA
        assert evidence['authenticated_multiplayer'] == 'NOT TESTED'
        subprocess.run(['python3', str(recipe / 'tools/check_fabric_jar.py'), str(binary)], check=True)
        generated = work / 'gradle-project'
        subprocess.run(['python3', str(recipe / 'tools/prepare_fabric_port.py'), str(generated)], check=True)

        night = work / 'night-config-3.8.0-source.tar.gz'
        night.write_bytes(gh('api', f'repos/TheElectronWill/night-config/tarball/{NIGHT_COMMIT}'))
        assert digest(night) == NIGHT_SHA
        out = work / 'release'
        out.mkdir()
        shutil.copyfile(jar, out / JAR_NAME)
        (out / (JAR_NAME + '.sha256')).write_text(f'{JAR_SHA}  {JAR_NAME}\n')
        for name in ['INSTALL-TH.md', 'RELEASE-NOTES.md', 'PROVENANCE.json', 'THIRD-PARTY-NOTICES.txt']:
            shutil.copyfile(DOCS / name, out / name)
        for original, name in [(recipe / 'LICENSE', 'LICENSE-GPL-3.0.txt'),
                               (recipe / 'replacement-assets/CC0-1.0.txt', 'LICENSE-CC0-1.0.txt'),
                               (generated / 'LICENSE-ASSETS', 'UPSTREAM-LICENSE-ASSETS.txt')]:
            shutil.copyfile(original, out / name)
        with tarfile.open(night) as tar:
            licenses = [e for e in tar if e.isfile() and len(Path(e.name).parts) == 2
                        and Path(e.name).name == 'LICENSE']
            assert len(licenses) == 1
            (out / 'NightConfig-LICENSE').write_bytes(tar.extractfile(licenses[0]).read())

        with tarfile.open(out / 'epicfight-fabric-1.21.11-beta-0.1.0-source.tar.gz', 'w:gz') as tar:
            prefix = 'epicfight-beta-0.1.0'
            tar.add(generated, arcname=prefix + '/gradle-project')
            tar.add(recipe, arcname=prefix + '/port-recipe',
                    filter=lambda e: None if '__pycache__' in Path(e.name).parts else e)
            tar.add(night, arcname=prefix + '/third-party/' + night.name)
            for path in out.iterdir():
                if path.suffix in ('.md', '.txt', '.json') or path.name == 'NightConfig-LICENSE':
                    tar.add(path, arcname=prefix + '/release/' + path.name)
        sums = ''.join(f'{digest(p)}  {p.name}\n' for p in sorted(out.iterdir()))
        (out / 'SHA256SUMS.txt').write_text(sums)
        # Only replace assets while this exact release is still a draft.
        release = api(f'{BASE}/releases/{RELEASE}')
        check_release(release)
        assert release['draft']
        gh('release', 'upload', TAG, *[str(p) for p in sorted(out.iterdir())], '--repo', REPO, '--clobber')
        release = api(f'{BASE}/releases/{RELEASE}')
        assets = {a['name']: a for a in release['assets']}
        assert set(assets) == {p.name for p in out.iterdir()}
        for path in out.iterdir():
            entry = assets[path.name]
            assert entry['state'] == 'uploaded' and entry['size'] == path.stat().st_size
            assert entry['digest'] == 'sha256:' + digest(path), path.name
        published = json.loads(gh('api', '--method', 'PATCH', f'{BASE}/releases/{RELEASE}', '-F', 'draft=false'))
        check_release(published)
        assert not published['draft']
        tag = api(f'{BASE}/git/ref/tags/{TAG}')
        assert tag['object']['type'] == 'commit' and tag['object']['sha'] == COMMIT
        print('Published verified prerelease:', published['html_url'])
        print('JAR SHA-256:', JAR_SHA)


if __name__ == '__main__':
    main()
