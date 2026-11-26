# SPDX-License-Identifier: CC0-1.0
"""Create original, furnished structures as Minecraft NBT and Sponge v2 schematics."""
from pathlib import Path
import gzip, io, json, sys, zipfile
import nbtlib as n
from nbtlib import Compound, Int, List, String, Short, ByteArray, IntArray
VERSION=4671

def write_nbt(root, name=''):
    buf=io.BytesIO()
    n.File(root, root_name=name).write(buf)
    return gzip.compress(buf.getvalue(),mtime=0)
def blocks(kind):
    sizes={'house':(13,11),'school':(21,15),'shop':(15,11),'clinic':(19,13),'apartment':(13,13)}
    w,d=sizes[kind];grid={}
    def put(x,y,z,state):
        assert 0<=x<w and 0<=z<d and 0<=y<8
        grid[x,y,z]=state
    def row(x1,z1,x2,z2,y,s):
        for x in range(x1,x2+1):
            for z in range(z1,z2+1):put(x,y,z,s)
    def bed(x,z,color):
        put(x,1,z,f'{color}_bed[facing=south,part=foot]');put(x,1,z+1,f'{color}_bed[facing=south,part=head]')
    def desk(x,z):
        put(x,1,z,'dark_oak_fence');put(x,2,z,'spruce_pressure_plate');put(x,1,z+1,'spruce_stairs[facing=north]')
    wall={'house':'white_terracotta','school':'bricks','shop':'yellow_terracotta','clinic':'smooth_quartz','apartment':'light_gray_concrete'}[kind]
    row(0,0,w-1,d-1,0,'birch_planks' if kind!='clinic' else 'smooth_stone')
    for y in range(1,5):
        for x in range(w):
            for z in [0,d-1]:
                put(x,y,z,'glass' if y in (2,3) and x%5 in (2,3) else wall)
        for z in range(d):
            for x in [0,w-1]:
                put(x,y,z,'glass' if y in (2,3) and z%5 in (1,2) else wall)
    mid=w//2
    for y,half in [(1,'lower'),(2,'upper')]:put(mid,y,0,'oak_door[facing=north,half='+half+']')
    for x in (1,w-2):
        for z in (1,d-2):put(x,4,z,'sea_lantern')
    row(0,0,w-1,d-1,5,'stone_bricks')
    if kind=='school':
        for z in (4,7,10):
            for x in (3,7,13,17):desk(x,z)
        row(3,1,8,1,2,'green_concrete');row(3,1,8,1,3,'green_concrete')
        for z in (3,6,9,12):put(w-2,1,z,'bookshelf')
        put(mid,5,0,'bell[attachment=floor]')
    elif kind=='shop':
        for x in (2,5,10):
            for z in range(3,d-2):
                put(x,1,z,'barrel[facing=up]');put(x,2,z,'smooth_stone_slab')
        put(w-3,1,2,'chiseled_bookshelf');put(w-3,2,2,'lantern')
        for x in range(2,w-2):put(x,4,0,'red_wool' if x%2 else 'white_wool')
    elif kind=='clinic':
        for z in (4,8):
            for x in (2,5,12,15):bed(x,z,'white');put(x+1,1,z,'quartz_block')
        row(2,1,6,1,1,'smooth_quartz');put(6,2,1,'potted_fern')
        row(mid-1,0,mid+1,0,4,'red_concrete');put(mid,3,0,'red_concrete');put(mid,5,0,'red_concrete')
    else:
        for z in range(3,d-1):
            if z!=5:
                for y in (1,2,3):put(mid,y,z,'stripped_oak_wood')
        bed(2,d-4,'blue');put(3,1,d-3,'barrel[facing=up]');put(3,2,d-3,'lantern')
        for x in range(mid+2,w-2):put(x,1,d-3,'spruce_stairs[facing=north]')
        put(2,1,2,'furnace');put(3,1,2,'crafting_table');put(4,1,2,'water_cauldron[level=3]')
        desk(w-3,3)
        if kind=='house':
            for x in range(1,w-1):row(x,1,x,d-2,6 if 2<=x<=w-3 else 5,'deepslate_tiles')
        else:
            bed(2,4,'green');put(w-2,2,d-2,'bookshelf')
    return w,7,d,grid
def generate(kind):
    w,h,d,g=blocks(kind)
    palette=['minecraft:air']+sorted({'minecraft:'+s for s in g.values()})
    ids={s:i for i,s in enumerate(palette)}
    def tag(s):
        name,_,props=s.partition('[');v=Compound({'Name':String(name)})
        if props:v['Properties']=Compound({k:String(val) for k,val in (p.split('=') for p in props[:-1].split(','))})
        return v
    entries=[]; data=[]
    for y in range(h):
        for z in range(d):
            for x in range(w):
                i=ids['minecraft:'+g.get((x,y,z),'air')]
                entries.append(Compound({'pos':List[Int]([x,y,z]),'state':Int(i)}));data.append(i)
    assert len(palette)<128
    vanilla={'DataVersion':Int(VERSION),'size':List[Int]([w,h,d]),'palette':List[Compound](map(tag,palette)),'blocks':List[Compound](entries),'entities':List[Compound]([])}
    schem={'Version':Int(2),'DataVersion':Int(VERSION),'Width':Short(w),'Height':Short(h),'Length':Short(d),'Offset':IntArray([0,0,0]),'PaletteMax':Int(len(palette)),'Palette':Compound({s:Int(i) for s,i in ids.items()}),'BlockData':ByteArray(data),'BlockEntities':List[Compound]([]),'Entities':List[Compound]([])}
    return write_nbt(vanilla),write_nbt(schem,'Schematic')
def main():
    dest=Path(sys.argv[1]);dest.mkdir(exist_ok=True,parents=True)
    with zipfile.ZipFile(dest/'fala-original-prefabs.zip','w',zipfile.ZIP_DEFLATED) as pack:
        pack.writestr('pack.mcmeta',json.dumps({'pack':{'description':'Fala original roleplay buildings','min_format':[94,1],'max_format':[94,1]}}))
        pack.writestr('LICENSE.txt','Fala original building layouts. CC0 1.0 Universal. https://creativecommons.org/publicdomain/zero/1.0/\n')
        for kind in ('house','school','shop','clinic','apartment'):
            structure,schematic=generate(kind);pack.writestr('data/fala/structure/'+kind+'.nbt',structure)
            (dest/('fala_'+kind+'.schem')).write_bytes(schematic)
if __name__=='__main__':main()
