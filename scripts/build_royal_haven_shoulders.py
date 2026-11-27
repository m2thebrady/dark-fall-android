"""Build world-aligned, sparse road-shoulder overlays from existing painted terrain.

This is an offline visual pass: the road graph, collision, map and world geometry
are untouched. The natural terrain provides both source materials. Requires
Pillow, numpy and scipy; not required by ordinary game materialization.
"""
from pathlib import Path
from PIL import Image
import base64
import io
import json
import re
import sys
import numpy as np
from scipy.ndimage import binary_closing,binary_opening,distance_transform_edt,gaussian_filter,label,map_coordinates

def build(html, folder, preview=None):
    terrain=json.loads(re.search(rb'const rh119ChunkData=(\{[^\n]+?\}), rh119ChunkImages',html).group(1))
    im=Image.new('RGB',(2880,1300))
    for k,v in terrain.items():
        x,y=map(int,k.split(':'))
        tile=Image.open(io.BytesIO(base64.b64decode(v.split(',')[1]))).convert('RGB')
        im.paste(tile.resize((360,325),Image.Resampling.LANCZOS),(x*360,y*325))
    v=np.asarray(im).astype(np.float32)
    r,g,bl=v.transpose((2,0,1))
    score=gaussian_filter(bl-0.24*g,3.8)
    mask=binary_opening(binary_closing(score>23.5,iterations=4),iterations=6)
    lab,_=label(mask);counts=np.bincount(lab.ravel());counts[0]=0
    mask=lab==np.argmax(counts) # ignore isolated rocky outcrops and ridge artwork
    d=distance_transform_edt(mask)-distance_transform_edt(~mask)
    y,x=np.indices(mask.shape,dtype=np.float32)
    # Displace the edge in world-space, combining broad erosion with small stone
    # notches. Do not introduce per-frame randomness or rectangular tile borders.
    noise=6.2*np.sin(x*.057+y*.046)+4.7*np.sin(x*.103-y*.076)+2.3*np.sin(x*.281+y*.213)
    q=np.clip((d-noise+5)/10,0,1);q=q*q*(3-2*q)
    # Surface coverage and worn shoulders are wider than the original bluff edge.
    a=np.where(mask,1-q,q)*.86
    mottled=np.clip((.44+.26*np.sin(x*.19+y*.12)+.24*np.cos(y*.26-x*.10)),0,1)
    a=np.maximum(a,np.where(mask,np.clip((15-d)/15,0,1)*mottled*.26,0))
    a*=np.clip((24-np.abs(d))/7,0,1)
    # Never extend shoreline blend onto northern cliff/rock faces or beyond map.
    a[(x>1800)&(y<260)]=0
    a[:2]=a[-2:]=0;a[:,:2]=a[:,-2:]=0
    # Pull actual neighboring terrain across the edge, using the signed distance
    # gradient only for direction. Offset samples inside both real surfaces
    # instead of creating a flat tinted strip, retaining cobble and moss texture.
    dy,dx=np.gradient(gaussian_filter(d,3.0));norm=np.maximum(.01,np.hypot(dx,dy))
    dx/=norm;dy/=norm
    inward=np.where(mask,-1,1)*(np.abs(d)+10+2.5*np.sin(x*.10+y*.17))
    slip=8*np.sin(x*.067-y*.08)
    sx=x+dx*inward-dy*slip;sy=y+dy*inward+dx*slip
    # The nearest actual opposite-class texel ensures corners do not sample the
    # same material. Resampled texture only participates within the narrow band.
    src=np.stack([map_coordinates(v[:,:,i],(sy,sx),order=1,mode='nearest') for i in range(3)],axis=2)
    rgba=np.dstack([np.clip(src,0,255).astype(np.uint8),np.round(a*255).astype(np.uint8)])
    rgba[rgba[:,:,3]<3]=0
    out=Image.fromarray(rgba,'RGBA')
    folder.mkdir(parents=True,exist_ok=True)
    for j in range(2):
        for i in range(2):
            piece=out.crop((i*1440,j*650,(i+1)*1440,(j+1)*650))
            piece.save(folder/f'shoulder-{i}-{j}.webp',quality=82,method=6)
    if preview:
        Image.alpha_composite(im.convert('RGBA'),out).save(preview)
    print('Shoulder coverage:',round(np.count_nonzero(rgba[:,:,3])/rgba[:,:,3].size*100,2),'percent')

if __name__=='__main__':
    build(Path(sys.argv[1]).read_bytes(),Path(sys.argv[2]),Path(sys.argv[3]) if len(sys.argv)>3 else None)
