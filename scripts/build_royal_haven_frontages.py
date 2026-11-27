"""Build four ground-only frontage overlays from the installed V1521 terrain.
Run with a verified V1521 standalone HTML. No synthetic stone grid is used:
the smaller setts are sampled from the existing hand-textured northern road.
"""
from pathlib import Path
import argparse,base64,io,json,re
import numpy as np
from PIL import Image, ImageFilter
P=argparse.ArgumentParser();P.add_argument('baseline');P.add_argument('out');a=P.parse_args()
p=Path(a.out);p.mkdir(parents=True,exist_ok=True)
s=Path(a.baseline).read_bytes()
d=json.loads(re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',s)[1])
world=Image.new('RGB',(6480,2600))
for k,v in d.items():
 x,y=map(int,k.split(':'));world.paste(Image.open(io.BytesIO(base64.b64decode(v.split(',')[1]))),(x*720,y*650))
# Paint the flagged forecourts with finer worn setts at the building line.
# Each entrance gets its own irregular material weathering, not a repeated decal.
rows=[
 ('foundry',125,1330,1370,104,[(350,'forge'),(805,'smith'),(1275,'leather')]),
 ('merchants',2160,1330,1770,104,[(2385,'market'),(2865,'item'),(3345,'alchemy')]),
 ('craft-west',150,1960,1320,102,[(335,'herbs'),(865,'arcane'),(1275,'wood')]),
 ('craft-east',2160,1960,1490,102,[(2325,'cloth'),(2865,'apothecary'),(3345,'bakery')]),
]
colors={'forge':(-21,-19,-17),'smith':(-14,-13,-11),'leather':(8,2,-7),'market':(9,5,-3),'item':(-4,1,3),'alchemy':(-5,5,0),'herbs':(-7,7,-10),'arcane':(2,0,5),'wood':(7,3,-5),'cloth':(5,2,-1),'apothecary':(-5,6,-7),'bakery':(13,9,3)}
rng=np.random.default_rng(1522)
sample=world.crop((1460,18,2090,550)).resize((430,363),Image.Resampling.LANCZOS)
tex=np.asarray(sample,dtype=np.float32)
atlas=Image.new('RGBA',(1792,4*112));meta=[]
for i,(key,x,y,w,h,doors) in enumerate(rows):
 base=np.asarray(world.crop((x,y,x+w,y+h)),dtype=np.float32)
 yy,xx=np.mgrid[:h,:w];n=np.asarray(Image.fromarray(rng.integers(0,256,(12,150),dtype=np.uint8)).resize((w,h),Image.Resampling.BICUBIC),dtype=np.float32)/255-.5
 # Nonuniform, weathered transition with full fade to the original paving.
 # The continuous fine-sett footway is deliberately flush, not a raised curb.
 t=(xx+113*i)%430;v=(yy+77*i)%363
 stone=tex[v,t].copy()
 stone=stone*1.04+np.array([5,4,3])
 # Thin darker gutter (broken by wear and individualized threshold crossings).
 mid=36+3*np.sin(xx/93+i)+n*5
 lip=np.exp(-((yy-mid)/2.25)**2)*.21
 stone=stone*(1-lip[:,:,None])
 edge=np.minimum(np.minimum(xx,w-1-xx)/25,np.minimum(yy,(h-1-yy))/12)
 edge=np.clip(edge,0,1)
 alpha=np.clip((1-(yy-33+n*12)/23),0,1)*.74*edge
 # Door-by-door worn entrances taper into the foreground, without a hard edge.
 wear=np.zeros((h,w),dtype=np.float32)
 tint=np.zeros((h,w,3),dtype=np.float32)
 for dx,kind in doors:
  center=dx-x
  gx=(xx-center)/(33+yy*.17);gy=(yy-20)/41
  f=np.exp(-1.2*(gx*gx+gy*gy))*np.clip((1.2-yy/h),0,1)*edge*(.85+n*.32)
  wear=np.maximum(wear,f*.65)
  tint+=f[:,:,None]*np.array(colors[kind])[None,None,:]
  # Polished threshold wears through the narrow gutter, retaining the stone texture.
  stone+=f[:,:,None]*np.array([7,5,3])
 stone=np.clip(stone+tint,0,255)
 blend=np.maximum(alpha,wear*.56)
 # Beyond the sett strip, keep the real underlying large flagstones; only shade them.
 shaded=np.clip(base+tint*1.12,0,255)
 material=(stone*alpha[:,:,None]+shaded*np.maximum(0,blend-alpha)[:,:,None])/np.maximum(blend[:,:,None],.001)
 rgba=np.dstack((np.clip(material,0,255),np.rint(blend*255))).astype(np.uint8)
 overlay=Image.fromarray(rgba,'RGBA')
 atlas.paste(overlay,(0,i*112))
 meta.append({'key':key,'x':x,'y':y,'w':w,'h':h,'sx':0,'sy':i*112,'doors':[{'x':dx,'y':y+3,'material':kind} for dx,kind in doors]})
 # Save a before/after comparison for local inspection.
 before=world.crop((x,y,x+w,y+h)).convert('RGBA');after=Image.alpha_composite(before,overlay)
 pair=Image.new('RGB',(w,h*2));pair.paste(before,(0,0));pair.paste(after,(0,h));pair.save('/tmp/rh-'+key+'-frontage.jpg',quality=93)
atlas.save(p/'frontages.webp',quality=87,method=6)
(p/'frontages.json').write_text(json.dumps(meta,indent=2)+'\n')
print('Packed',len(meta),'frontages',atlas.size,(p/'frontages.webp').stat().st_size,'bytes')
