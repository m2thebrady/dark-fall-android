"""Bake an original, continuous town floor using Dark Fall's existing high-detail materials."""
import argparse,base64,io,json,math,random,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
import numpy as np
from scipy.ndimage import distance_transform_edt
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-html',required=True,type=Path,help='Previous V1520 HTML, including original terrain and paving materials.')
parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'game-bundle/patches/art-v1521')
parser.add_argument('--preview-dir',type=Path,default=None)
args=parser.parse_args()
root=args.out;plan=json.loads((root/'layout.json').read_text())
W,H=6480,2600; TW,TH=720,650
html=args.source_html.read_bytes()
chunks=json.loads(re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html)[1])
def from_url(url):return Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGB')
base=Image.new('RGB',(W,H))
for key,url in chunks.items():
 ix,iy=map(int,key.split(':'));base.paste(from_url(url).resize((TW,TH),Image.Resampling.LANCZOS),(ix*TW,iy*TH))
# Match the original review bake's high-quality intermediate.
buf=io.BytesIO();base.save(buf,format='JPEG',quality=93);buf.seek(0);base=Image.open(buf).convert('RGB')
source=Image.open(io.BytesIO(base64.b64decode(re.search(rb'rh191PaveArt.src="data:image/[^;]+;base64,([^"]+)"',html)[1]))).convert('RGB')
rng=np.random.default_rng(1521)
rnd=random.Random(1521)
# Material patches are assembled across the *entire* world before tile slicing.
# The texture quilting uses overlap only for natural ground; the stone has a
# stable masonry scale and world-aligned joints, never independent tile repeats.
grass=Image.new('RGB',(W,H),(54,59,37))
# A feathered square overlaps its neighbor; variable sample coordinates remove
# regular checkerboard repetition from grass and old unpaved terrain.
n,over=420,128;st=n-over
mask=np.ones((n,n),dtype=np.float32)
axis=np.minimum(np.arange(n),np.arange(n)[::-1]);a=np.clip(axis/(over*.95),0,1);a=a*a*(3-2*a)
mask=np.minimum(a[:,None],a[None,:]);mask=Image.fromarray(np.uint8(mask*255),'L')
regions=[(20,0,1360,480),(2160,0,2800,550),(3400,0,4390,520),(2500,2225,3560,2600),(0,2220,1250,2600),(4580,0,5650,430)]
for yy in range(-over,H,st):
 for xx in range(-over,W,st):
  l,t,r,b=rnd.choice(regions)
  if b-t<n: l,t,r,b=regions[0]
  x=rnd.randrange(l,max(l+1,r-n));y=rnd.randrange(t,max(t+1,b-n))
  p=base.crop((x,y,x+n,y+n))
  if rnd.random()<.5:p=p.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  if rnd.random()<.5:p=p.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
  p=ImageEnhance.Brightness(p).enhance(rnd.uniform(.88,1.13))
  grass.paste(p,(xx,yy),mask)
# Real painted cobblestone stays at the original stone scale. The texture's
# outer joins are mirrored and mottled, and the broad color field is continuous.
def repeat_tile(im,sx,sy,mirror=False):
 out=Image.new('RGB',(W,H));im=im.resize((sx,sy),Image.Resampling.LANCZOS)
 for iy,y in enumerate(range(0,H,sy)):
  for ix,x in enumerate(range(0,W,sx)):
   tile=im
   if mirror and ix%2:tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
   if mirror and iy%2:tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
   out.paste(tile,(x,y))
 return out
# Crop a pure old cobble patch without any boundary or painted object.
cobble=repeat_tile(base.crop((2350,900,2830,1270)),480,370,True)
flagstone=repeat_tile(source,322,322,True)
# Paint broad road masks, connected stone courts, and walkable insets.
# Distances and noise are evaluated globally; the tiles therefore meet exactly.
scale=.5;mw,mh=int(W*scale),int(H*scale)
def mask_layer(kind):
 im=Image.new('L',(mw,mh));d=ImageDraw.Draw(im)
 for r in plan['roads']:
  if r['kind']!=kind:continue
  pts=[(round(x*scale),round(y*scale)) for x,y in r['points']]
  wide=round(r['width']*scale)
  d.line(pts,fill=255,width=wide,joint='curve')
  for x,y in pts:d.ellipse((x-wide/2,y-wide/2,x+wide/2,y+wide/2),fill=255)
 for c in plan['courts']:
  if c['kind']!=kind:continue
  d.polygon([(round(x*scale),round(y*scale)) for x,y in c['poly']],fill=255)
 return np.asarray(im)>0
def field(w,h,cell):
 a=rng.random((math.ceil(h/cell)+2,math.ceil(w/cell)+2),dtype=np.float32)
 return np.asarray(Image.fromarray(a,'F').resize((w,h),Image.Resampling.BICUBIC))
big=field(mw,mh,75).clip(0,1);med=field(mw,mh,19).clip(0,1);fine=field(mw,mh,3).clip(0,1)
def smooth(z):
 z=np.clip(z,0,1);return z*z*(3-2*z)
c=mask_layer('cobble');f=mask_layer('flagstone')
# one unified road edge, with irregular cobbles and earthy worn transitions
union=c|f;d=(distance_transform_edt(union)-distance_transform_edt(~union))*2
jitter=(med-.5)*17+(fine-.5)*7
d=(d+jitter).astype(np.float32)
dfa=((distance_transform_edt(f)-distance_transform_edt(~f))*2+jitter*.5).astype(np.float32)
street=smooth((d+13)/24)
flag=smooth((dfa+6)/12)
# Broad dirt/grass verge, subtle mortar/grit in the shoulder, recessed drainage
# trace (a painted surface, no physical curb), patchy green joints at edges.
earth=smooth((d+32)/30)*(1-street)*(.48+med*.18)
gutter=np.exp(-((d-7)/4.2)**2)*(0.31+0.56*med)*street
wear=smooth((d-8)/55)*(.35+.65*big)
moss=np.exp(-((d-2)/14)**2)*smooth((med-.38)/.5)
def lerp(a,b,t):return a+(b-a)*t[...,None]
def full(field):return np.asarray(Image.fromarray(field.astype(np.float32),'F').resize((W,H),Image.Resampling.BILINEAR),dtype=np.float32)
# Process in horizontal bands to avoid a large full-resolution temporary array.
fields=[full(a) for a in [street,flag,earth,gutter,wear,moss,big,med]]
out=Image.new('RGB',(W,H))
for y in range(0,H,200):
 j=min(H,y+200);region=(0,y,W,j);sl=slice(y,j)
 G=np.asarray(grass.crop(region),dtype=np.float32);C=np.asarray(cobble.crop(region),dtype=np.float32);F=np.asarray(flagstone.crop(region),dtype=np.float32)
 stv,fl,ea,gu,we,mo,bi,me=[a[sl] for a in fields]
 soil=G*np.array([1.09,.99,.83],dtype=np.float32)+np.array([12,9,7],dtype=np.float32)
 G=lerp(G,soil,ea)
 stone=lerp(C,F,fl)
 # Used and rain-darkened stones: slightly warmer in trafficked areas and
 # cooler/mossy near vegetation. Keep detail and moderate contrast.
 stone*=((.87+.15*bi+.06*we)[...,None])
 stone+=np.stack([we*6-gu*19-mo*7, we*5-gu*18+mo*4, we*2-gu*16-mo*7],axis=-1)
 A=lerp(G,stone,stv)
 # Irregular north boundary, gentle southern verge and sidewall preservation.
 # Northern castle/mountain and waterfall terrain is untouched.
 ys=np.arange(y,j,dtype=np.float32)[:,None];xs=np.arange(W,dtype=np.float32)[None,:]
 north=smooth((ys-690+(bi-.5)*60)/170)
 south=smooth((2500-ys+(bi-.5)*40)/80)
 side=smooth((xs-25)/115)*smooth((6460-xs-20)/125)
 alpha=north*south*side
 B=np.asarray(base.crop(region),dtype=np.float32)
 A=lerp(B,A,alpha)
 out.paste(Image.fromarray(np.uint8(np.clip(A,0,255))), (0,y))
# Preserve every original north tile (no changed pixels in that row).
for iy in range(1,4):
 for ix in range(9):
  box=(ix*TW,iy*TH,(ix+1)*TW,(iy+1)*TH)
  out.crop(box).save(root/f'ground-{ix}-{iy}.webp','WEBP',quality=82,method=4)
out.crop((0,0,6460,2600)).resize((1292,520),Image.Resampling.LANCZOS).save(root/'town-map.webp','WEBP',quality=89,method=4)
if args.preview_dir:
 args.preview_dir.mkdir(parents=True,exist_ok=True)
 out.resize((1620,650),Image.Resampling.LANCZOS).save(args.preview_dir/'v1521-ground-preview.jpg',quality=95)
 out.crop((1950,1170,3330,1740)).save(args.preview_dir/'v1521-merchant-preview.jpg',quality=95)
print('New tiles:',sum(p.stat().st_size for p in root.glob('ground-*.webp')))
