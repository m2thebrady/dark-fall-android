"""Extend the actual painted Royal Haven atlas to the eastern market boundary.
No map, navigation, collision or resident data changes. Requires Pillow/numpy/scipy.
"""
from pathlib import Path
from PIL import Image
import base64, io, json, re, sys
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter

def build(html, folder, preview=None):
    data=json.loads(re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html).group(1))
    full=Image.new('RGB',(5760,2600))
    for k,v in data.items():
        x,y=map(int,k.split(':'))
        if x>=8: continue
        full.paste(Image.open(io.BytesIO(base64.b64decode(v.split(',')[1]))).convert('RGB'),(x*720,y*650))
    im=np.asarray(full)
    y,x=np.indices((2600,720),dtype=np.float32)
    # Sample broad natural patches, with continuous gentle coordinate warping.
    # Non-repeating shifts remove the visual grid of the old procedural fallback.
    def sample(rect,phase,warp):
        l,t,r,b=rect
        p=np.asarray(full.crop(rect),dtype=np.float32); hh,ww=p.shape[:2]
        sx=x+phase+warp*np.sin(y*.009)+.047*y
        sy=y+phase*.43+warp*np.cos(x*.013+y*.004)
        return np.stack([map_coordinates(p[:,:,i],(sy,sx),order=1,mode='reflect') for i in range(3)],axis=2)
    grass0=sample((18,25,695,510),34,12)
    grass1=sample((2320,0,2768,525),347,19)
    f=(.5+.34*np.sin(y*.0078+x*.006)+.15*np.sin(x*.015-y*.021)).clip(0,1)[...,None]
    grass=grass0*(1-f)+grass1*f
    # Keep frequent paths readable but wear their edges into the grass.
    stone=sample((2300,950,3380,1380),187,4)
    offset=78*np.exp(-x/165)
    road=np.maximum(np.minimum(y-(1480-offset),1620-offset-y),np.minimum(y-2050,2178-y))
    irregular=10*np.sin(x*.037+y*.008)+5*np.sin(x*.092-y*.014)+3*np.sin(x*.22+y*.031)
    a=np.clip((road+irregular+12)/25,0,1);a=a*a*(3-2*a)
    east=grass*(1-a[...,None])+stone*a[...,None]
    # Match every pixel at the west seam and phase out the reflected original
    # terrain irregularly over a generous shoulder, not along a hard vertical line.
    mirror=im[:,5759-np.arange(720)].astype(np.float32)
    seam=np.clip((x-8)/(143+23*np.sin(y*.012)+11*np.sin(y*.048)),0,1);seam=seam*seam*(3-2*seam)
    east=mirror*(1-seam[...,None])+east*seam[...,None]
    out=Image.fromarray(np.uint8(np.clip(east,0,255)),'RGB')
    folder.mkdir(parents=True,exist_ok=True)
    for j in range(4):
        out.crop((0,j*650,720,(j+1)*650)).save(folder/f'east-ground-{j}.webp',quality=83,method=6)
    if preview:
        p=Image.new('RGB',(1440,2600));p.paste(full.crop((5040,0,5760,2600)),(0,0));p.paste(out,(720,0))
        p.resize((720,1300),Image.Resampling.LANCZOS).save(preview,quality=92)

if __name__=='__main__':
    build(Path(sys.argv[1]).read_bytes(),Path(sys.argv[2]),Path(sys.argv[3]) if len(sys.argv)>3 else None)
