"""Compare the pinned official NeoForge parent, official Fabric commit and prepared target."""
import argparse
import collections
import hashlib
import json
import tarfile
from pathlib import Path
from prepare_fabric_port import ARCHIVE_SHA256, UPSTREAM

PARENT = 'a78aa24b72e90a9d09f5fd61925e4369d117abaf'
PARENT_SHA256 = 'b5ee985bd04a2975b774406df1ee8ef51473ad0527221a760fbae2b20bb62555'
PREFIX = 'src/main/java/'
ASSETS = 'src/main/resources/assets/'
def digest(data):
    return hashlib.sha256(data).hexdigest()
def read_archive(path, expected, revision):
    with path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != expected: raise ValueError('Archive SHA-256 mismatch: '+str(path))
    java, assets = {}, set()
    with tarfile.open(path) as tar:
        root='epicfight-'+revision+'/'
        for member in tar:
            if not member.isfile(): continue
            if not member.name.startswith(root): raise ValueError('Unexpected upstream archive')
            name = member.name[len(root):]
            if name.startswith(PREFIX) and name.endswith('.java'):
                java[name[len(PREFIX):]] = digest(tar.extractfile(member).read().replace(b'\r\n',b'\n'))
            elif name.startswith(ASSETS): assets.add(name[len(ASSETS):])
    return java, assets
def compare(a,b,path):
    if path not in a: return 'added' if path in b else 'absent_both'
    if path not in b: return 'absent'
    return 'identical' if a[path]==b[path] else 'changed'
def main():
    p=argparse.ArgumentParser()
    for n in ('neoforge_archive','fabric_archive','target','output'):p.add_argument(n,type=Path)
    a=p.parse_args()
    neo,_=read_archive(a.neoforge_archive,PARENT_SHA256,PARENT)
    fabric,original_assets=read_archive(a.fabric_archive,ARCHIVE_SHA256,UPSTREAM)
    root=a.target/PREFIX
    port={f.relative_to(root).as_posix():digest(f.read_bytes().replace(b'\r\n',b'\n')) for f in root.rglob('*.java')}
    if not port: raise ValueError('Missing prepared Java sources')
    output_assets={f.relative_to(a.target/ASSETS).as_posix() for f in (a.target/ASSETS).rglob('*') if f.is_file()}
    a.output.mkdir(parents=True,exist_ok=True)
    families=collections.defaultdict(collections.Counter)
    with (a.output/'source-diff.tsv').open('w') as out:
        out.write('java_path\tneoforge_to_official_fabric\tofficial_fabric_to_v3\tneoforge_sha256\tofficial_fabric_sha256\tv3_sha256\n')
        for path in sorted(neo.keys()|fabric.keys()|port.keys()):
            family=path.removeprefix('yesman/epicfight/').split('/')[:-1]
            change=compare(fabric,port,path)
            families['/'.join(family[:2]) or '.'][change]+=1
            out.write('\t'.join([path,compare(neo,fabric,path),change,neo.get(path,''),fabric.get(path,''),port.get(path,'')])+'\n')
    def counts(a,b):return dict(collections.Counter(compare(a,b,p) for p in a.keys()|b.keys()))
    summary={'neoforge':PARENT,'official_fabric':UPSTREAM,'neoforge_files':len(neo),'fabric_files':len(fabric),'port_files':len(port),'neoforge_to_official_fabric':counts(neo,fabric),'official_fabric_to_v3':counts(fabric,port),'removed_paths':sorted(fabric.keys()-port.keys()),'original_asset_paths':len(original_assets),'prepared_asset_paths':sorted(output_assets),'packages':families}
    (a.output/'source-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k.endswith('_files') or k=='official_fabric_to_v3'}))
if __name__=='__main__':main()
