"""Offline Royal Haven V1524 landscape bake. No extra runtime scenery draws.
Usage: python build_royal_haven_landscape.py BASE.html geometry.json texture.png gardens.png OUTPUT_DIR
"""
import base64, heapq, io, json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy.ndimage import distance_transform_edt, gaussian_filter
BASE,GEO,TEX,GARD,OUT=sys.argv[1:]
out=Path(OUT);out.mkdir(parents=True,exist_ok=True)
geo=json.load(open(GEO)); plan=geo['plan']; W,H=6480,2600
rng=np.random.default_rng(1524)
raw=Path(BASE).read_bytes(); chunks=json.loads(re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',raw)[1]); old=Image.new('RGB',(W,H))
for key,v in chunks.items():
 x,y=map(int,key.split(':'));old.paste(Image.open(io.BytesIO(base64.b64decode(v.split(',')[1]))),(x*720,y*650))
# Make a top-down clearance grid from the unchanged actual runtime collision.
blocked=np.array([[c=='1' for c in line] for line in geo['blocked']]); clear=distance_transform_edt(~blocked)*10
def path(start,end):
 s=tuple(round(v/10) for v in start); e=tuple(round(v/10) for v in end)
 # Locate nearest clear starting/ending point (door threshold may be too close).
 def snap(p):
  x,y=p; candidates=[(dx*dx+dy*dy,x+dx,y+dy) for dx in range(-5,6) for dy in range(-5,6) if 0<=x+dx<blocked.shape[1] and 0<=y+dy<blocked.shape[0] and clear[y+dy,x+dx]>=20];return min(candidates)[1:]
 s=snap(s);e=snap(e); q=[(0,0,s)]; dist={s:0};prev={}; 
 while q:
  _,g,p=heapq.heappop(q)
  if p==e:break
  if g>dist[p]:continue
  for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
   nx,ny=p[0]+dx,p[1]+dy
   if not (0<=nx<blocked.shape[1] and 0<=ny<blocked.shape[0]) or clear[ny,nx]<20:continue
   if dx and dy and (clear[p[1],nx]<20 or clear[ny,p[0]]<20):continue
   ng=g+(1.414 if dx and dy else 1)+max(0,40-clear[ny,nx])*.025; n=(nx,ny)
   if ng<dist.get(n,1e9):
    dist[n]=ng;prev[n]=p;heapq.heappush(q,(ng+np.hypot(e[0]-nx,e[1]-ny),ng,n))
 else:return []
 p=e;steps=[p]
 while p!=s:p=prev[p];steps.append(p)
 steps=steps[::-1]
 # Simplify only when full segment is clear; make graceful visual routes.
 def free(a,b):
  for t in np.linspace(0,1,max(2,int(np.hypot(b[0]-a[0],b[1]-a[1])*2))):
   x,y=round(a[0]+(b[0]-a[0])*t),round(a[1]+(b[1]-a[1])*t)
   if clear[y,x]<20:return False
  return True
 simple=[steps[0]];i=0
 while i<len(steps)-1:
  j=min(i+20,len(steps)-1)
  while j>i+1 and not free(steps[i],steps[j]):j-=1
  simple.append(steps[j]);i=j
 return [[x*10,y*10] for x,y in simple]
specs=[
 ('Courtyard House Walk',[4177,906],[4170,1015]),('Cottage West Walk',[3995,964],[4000,1015]),
 ('Gatehouse Garden Approach',[4429,1170],[4960,1375]),('Longhouse Garden Walk',[5242,1170],[5250,1310]),
 ('East Residential Rear Lane',[5291,1818],[4960,1785]),('Stone Cottage Walk',[4864,2315],[4870,2425]),
 ('South Cottage Walk',[4565,2380],[4565,2420]),('Herb Courtyard Link',[3755,2312],[3760,2335]),
 ('West Residence Walk',[5294,1970],[5295,2075]),('East Residence Walk',[5540,1965],[5540,2075]),
 ('Warehouse Yard Link',[6150,2265],[6150,2140])]
links=[]
for name,a,b in specs:
 p=path(a,b)
 if len(p)>1:
  length=sum(np.hypot(q[0]-r[0],q[1]-r[1]) for r,q in zip(p,p[1:]))
  if length<=np.hypot(b[0]-a[0],b[1]-a[1])*1.85+70:links.append(dict(key=name,points=p,width=54 if length>100 else 46,kind='gravel',length=round(length)))
print('new connections',[(r['key'],r['points']) for r in links],flush=True)
# Masks match the established road layout, but vary the materials by use.
masks={k:Image.new('L',(W,H)) for k in ['cobble','flagstone','gravel']}
def stroke(img,pts,w):
 d=ImageDraw.Draw(img);pts=[tuple(p) for p in pts];d.line(pts,fill=255,width=round(w),joint='curve');r=w/2
 for x,y in pts:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
for r in plan['roads']:
 kind=r['kind']; 
 if r['key'] in ('Garden Lanes','Southern Cellar Lane','Southern Residential Walk','Hill Lane'):kind='gravel'
 stroke(masks[kind],r['points'],r['width'])
for c in plan['courts']:ImageDraw.Draw(masks[c['kind']]).polygon([tuple(p) for p in c['poly']],fill=255)
for r in links:stroke(masks['gravel'],r['points'],r['width'])
# Preserve inherited stone foundations and distant terrain beyond the changed city.
# Bake small stone thresholds into the new gravel residential lanes.
for r in links:
 if 'Warehouse' not in r['key']:
  x,y=r['points'][0];ImageDraw.Draw(masks['flagstone']).rounded_rectangle((x-26,y-20,x+26,y+20),radius=9,fill=255)
u=np.maximum.reduce([np.asarray(m) for m in masks.values()]); road=Image.fromarray(u)
# Identify off-road spaces close to buildings, not through-lanes; no collision is added.
road10=np.asarray(road.resize((648,260),Image.Resampling.NEAREST))[:,:646]>0
droad=distance_transform_edt(~road10)*10
garden_src=Image.open(GARD).convert('RGBA')
garden_cells=[]
# Cut out atlas cells. The generated edge alpha is preserved, with soft remnant
# pixels at the gutters removed only on cell boundaries.
for j in range(2):
 for i in range(2):
  a=garden_src.crop((i*768+10,j*512+9,(i+1)*768-10,(j+1)*512-9))
  alpha=a.getchannel('A'); bbox=alpha.point(lambda v: 255 if v>32 else 0).getbbox()
  garden_cells.append(a.crop(bbox) if bbox else a)
# Coordinates selected along verge pockets near residential courts and shop rows.
# Snap modestly to the nearest available clearance on grass.
requested=[(3890,1110,0),(4250,1170,3),(4630,1270,2),(4820,1190,1),(5500,1215,3),(5650,1420,2),(3990,1840,1),(4170,1915,2),(4500,2190,0),(4770,2230,3),(5000,2180,2),(5425,2020,0),(5675,1930,1),(3720,2160,3),(3930,2315,1),(4300,2270,2),(2550,2220,2),(1350,2190,3),(930,1430,0),(3710,1505,2),(1070,1770,1),(5800,2225,3)]
gardens=[]
for ox,oy,k in requested:
 candidates=[]
 for y in range(max(80,round(oy/10)-8),min(246,round(oy/10)+9)):
  for x in range(max(8,round(ox/10)-8),min(638,round(ox/10)+9)):
   if clear[y,x]>=35 and droad[y,x]>=33 and clear[y,x]<=150:
    candidates.append(((x*10-ox)**2+(y*10-oy)**2+max(0,clear[y,x]-55)*70,x*10,y*10))
 if not candidates:continue
 _,x,y=min(candidates);w=100 if k in [0,3] else 114;h=round(w*garden_cells[k].height/garden_cells[k].width*.76)
 if any(np.hypot(x-g['x'],y-g['y'])<110 for g in gardens):continue
 # Full placement fits outside paving on the screen; stay small and unblocked.
 if (np.asarray(road.crop((x-w//2,y-h//2,x+w//2,y+h//2)))>127).mean()>.04:continue
 gardens.append(dict(x=x,y=y,w=w,h=h,variant=k))
print('garden positions',gardens,flush=True)
# Atlas material sizes: physical stone scale in world pixels, not screen pixels.
src=Image.open(TEX).convert('RGB');half=src.width//2;pad=12
materials={}
def mincut(error):
 # Minimum-error seam: avoid straight joins across cracks and stones.
 h,w=error.shape;cost=error[0].copy();parent=np.zeros((h,w),np.int8)
 for y in range(1,h):
  c=np.stack((np.r_[np.inf,cost[:-1]],cost,np.r_[cost[1:],np.inf]))
  d=np.argmin(c,axis=0);parent[y]=d-1;cost=c[d,np.arange(w)]+error[y]
 j=int(cost.argmin());cut=np.empty(h,np.int32);cut[-1]=j
 for y in range(h-1,0,-1):j+=int(parent[y,j]);cut[y-1]=j
 return cut
def quilt(crop,seed,patch,overlap,wide=2160,high=1260):
 rnd=np.random.default_rng(seed)
 src=np.asarray(crop,dtype=np.float32);variants=[src,src[:,::-1],src[::-1],src[::-1,::-1]]
 step=patch-overlap;aw=((wide-patch+step-1)//step)*step+patch;ah=((high-patch+step-1)//step)*step+patch
 dst=np.zeros((ah,aw,3),dtype=np.float32)
 yy,xx=np.mgrid[:patch,:patch];valid=np.zeros((patch,patch),bool)
 for y in range(0,ah-patch+1,step):
  for x in range(0,aw-patch+1,step):
   region=dst[y:y+patch,x:x+patch]
   valid[:]=False
   if x:valid[:,:overlap]=True
   if y:valid[:overlap,:]=True
   best=None;score=float('inf')
   for _ in range(26 if x or y else 1):
    v=variants[rnd.integers(0,4)];sy=rnd.integers(0,src.shape[0]-patch+1);sx=rnd.integers(0,src.shape[1]-patch+1)
    p=v[sy:sy+patch,sx:sx+patch]
    err=((p-region)**2).mean(axis=2)
    sc=err[valid].mean() if valid.any() else 0
    if sc<score:score=sc;best=p;be=err
   weights=np.ones((patch,patch),np.float32)
   if x:
    cut=mincut(be[:,:overlap]);weights=np.minimum(weights,np.clip((xx-cut[:,None]+1.5)/3,0,1))
   if y:
    cut=mincut(be[:overlap,:].T);weights=np.minimum(weights,np.clip((yy-cut[None,:]+1.5)/3,0,1))
   region[:]=region*(1-weights[:,:,None])+best*weights[:,:,None]
 # Wrap at a distant position with crossfade only on the outer 20 pixels;
 # ordinary patch intersections use the irregular minimum-cost seams.
 a=dst[:high,:wide].copy();blend=np.linspace(0,1,20,dtype=np.float32)
 for j in range(20):
  a[:,wide-20+j]=a[:,wide-20+j]*(1-blend[j])+a[:,j]*blend[j]
  a[high-20+j]=a[high-20+j]*(1-blend[j])+a[j]*blend[j]
 return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
for k,(i,j,tw,th,patch,overlap) in zip(['cobble','flagstone','gravel','grass'],[(0,0,380,290,135,32),(1,0,345,260,150,43),(0,1,400,340,140,32),(1,1,600,450,190,38)]):
 crop=src.crop((i*half+pad,j*half+pad,(i+1)*half-pad,(j+1)*half-pad)).resize((tw,th),Image.Resampling.LANCZOS)
 materials[k]=quilt(crop,1524+i+2*j,patch,overlap)
 print('quilted',k,flush=True)
def texture(k,box):
 x0,y0,x1,y1=box;im=materials[k];tw,th=im.size;a=Image.new('RGB',(x1-x0,y1-y0))
 for y in range(y0//th*th,y1,th):
  for x in range(x0//tw*tw,x1,tw):a.paste(im,(x-x0,y-y0))
 return np.asarray(a,dtype=np.float32)
# Soft, irregular shoulders. Using low-frequency world-aligned noise gives
# continuity at tile borders and lets vegetation naturally eat into the paving.
def noise(nx,ny):
 ar=Image.fromarray(rng.integers(0,256,(ny,nx),dtype=np.uint8)).resize((W,H),Image.Resampling.BICUBIC)
 return ar
noise1=noise(210,88);noise2=noise(39,16)
# Output the original tiles above the Northern blend and retain a southern fade.
changed=[]; world=old.copy(); changed_materials={}
for iy in range(1,4):
 for ix in range(9):
  ox,oy=ix*720,iy*650;box=(ox,oy,ox+720,oy+650)
  margin=45; ex=(max(0,ox-margin),max(0,oy-margin),min(W,ox+720+margin),min(H,oy+650+margin));a,b,c,d=ex
  sl=(slice(oy-b,oy-b+650),slice(ox-a,ox-a+720))
  n=np.asarray(noise1.crop(box),dtype=np.float32)/255-.5
  n2=np.asarray(noise2.crop(box),dtype=np.float32)/255-.5
  y=np.arange(oy,oy+650)[:,None]
  fade=np.minimum(np.clip((y-700)/165,0,1),np.clip((2490-y)/75,0,1))
  olda=np.asarray(old.crop(box),dtype=np.float32); dst=olda.copy()
  distmask=np.asarray(road.crop(ex))>0
  sd=(distance_transform_edt(distmask)-distance_transform_edt(~distmask))[sl]
  shoulder=np.clip((sd+25+n*20)/37,0,1)
  verge=np.clip((sd+37+n*23)/35,0,1)
  # soften bare margins, preserve deep vegetation and underlying landscape.
  shadow=(1+n2*.13+n*.016)
  dirt=texture('gravel',box)*shadow[:,:,None]*np.array([.98,.99,.98])
  amt=(verge*(1-shoulder)*.72*fade)[:,:,None];dst=dst*(1-amt)+dirt*amt
  # Near-road natural grass, broken patches, leaf litter. Keep large old
  # terrain features and retain its large-scale green variation.
  grass=texture('grass',box)*shadow[:,:,None]*np.array([.84,.88,.83])
  amt=(np.clip((sd+86)/65,0,1)*(1-verge)*(.20+n*.14)*fade)[:,:,None];dst=dst*(1-amt)+grass*amt
  for k in ('gravel','cobble','flagstone'):
   m=np.asarray(masks[k].crop(ex))>0
   if not m.any():continue
   sk=(distance_transform_edt(m)-distance_transform_edt(~m))[sl]
   alpha=np.clip((sk+12+n*13)/22,0,1)*fade
   if k=='gravel':tone=np.array([.94,.96,.92])
   elif k=='cobble':tone=np.array([.94,.94,.92])
   else:tone=np.array([1.03,1.0,.95])
   mat=texture(k,box)*tone*shadow[:,:,None]
   # Stone surfaces are subtly darkened toward verge; irregular growth in
   # joints and gravel shoulders, but clear readable central walking routes.
   if k!='gravel':
    moss=np.clip((13-sk+n*20)/30,0,1)*.17
    mat=mat*(1-moss[:,:,None])+grass*moss[:,:,None]
   a2=(alpha*.96)[:,:,None];dst=dst*(1-a2)+mat*a2
  tile=Image.fromarray(np.clip(dst,0,255).astype(np.uint8)).convert('RGBA')
  for g in gardens:
   l,t=g['x']-g['w']//2,g['y']-g['h']//2
   if l+g['w']<=ox or l>=ox+720 or t+g['h']<=oy or t>=oy+650:continue
   cell=garden_cells[g['variant']].resize((g['w'],g['h']),Image.Resampling.LANCZOS)
   if g['x']%3:cell=ImageOps.mirror(cell)
   tile.alpha_composite(cell,(l-ox,t-oy))
  tile=tile.convert('RGB')
  if np.mean(np.abs(np.asarray(tile,dtype=np.int16)-olda))<.08:continue
  name=f'ground-{ix}-{iy}.webp';tile.save(out/name,'WEBP',quality=86,method=5);world.paste(tile,(ox,oy));changed.append(dict(key=f'{ix}:{iy}',file=name))
world.crop((0,0,6460,2600)).resize((1292,520),Image.Resampling.LANCZOS).save(out/'map.webp','WEBP',quality=88,method=5)
world.resize((1620,650)).save('/tmp/rh1524-new-world.jpg',quality=93)
world.crop((2100,1240,3620,1700)).save('/tmp/rh1524-new-detail.jpg',quality=93)
world.crop((3850,1000,5700,2420)).resize((925,710)).save('/tmp/rh1524-new-residential.jpg',quality=93)
meta=dict(version=1524,tiles=changed,materials=['irregular street cobble','large weathered courtyard flagstone','compacted gravel and earth','mossy grass and leaf litter'],links=links,gardens=gardens,geometry='unchanged',world=[6460,2600])
(out/'landscape.json').write_text(json.dumps(meta,indent=2)+'\n')
print('baked',len(changed),'tiles',sum((out/t['file']).stat().st_size for t in changed),'bytes',flush=True)
