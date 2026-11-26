"""Build a private target-specific e4mc file from the exact existing MIT-licensed mod."""
import hashlib,json,subprocess,sys,tempfile,zipfile
from pathlib import Path
original, destination, java_home, asm = sys.argv[1:]
required='6e24087ebdc0a658c68d6b687e8b59d498fd201a57daa5092d78a4c3c474336b'
assert hashlib.sha256(Path(original).read_bytes()).hexdigest()==required
with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(original) as src:
    d=Path(tmp); name='link/e4mc/E4mcClient.class'
    assert not any(n.upper().endswith(('.SF','.RSA','.DSA')) for n in src.namelist())
    (d/'in.class').write_bytes(src.read(name))
    jdk=Path(java_home)/'bin'
    subprocess.run([jdk/'javac','-cp',asm,'-d',d,Path(__file__).with_name('UpdateOwnerCheck.java')],check=True)
    subprocess.run([jdk/'java','-cp',str(d)+':'+asm,'UpdateOwnerCheck',d/'in.class',d/'out.class'],check=True)
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as out:
        for entry in src.infolist():
            data=src.read(entry)
            if entry.filename==name:data=(d/'out.class').read_bytes()
            elif entry.filename=='fabric.mod.json':
                meta=json.loads(data)
                meta['version']='6.2.1+fala.mc1.21.11.1'
                meta['depends']['minecraft']='=1.21.11'
                data=(json.dumps(meta,indent=2)+'\n').encode()
            out.writestr(entry,data)
        for filename in ['LICENSE-e4mc','FALA-CHANGE.txt']:
            entry=zipfile.ZipInfo('META-INF/'+filename,(2026,11,25,0,0,0))
            out.writestr(entry,Path(__file__).with_name(filename).read_bytes())
print(hashlib.sha256(Path(destination).read_bytes()).hexdigest(),Path(destination).name)
