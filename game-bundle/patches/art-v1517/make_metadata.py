"""Reviewed, normalized sprite anchors and world geometry for the residential pass."""
from pathlib import Path
import json
from PIL import Image
root=Path(__file__).parent
def window(x0,y0,x1,y1,lit):
 return {'points':[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],'lit':lit}
def house(k,w,h,door,offset,doorHeight,doorWidth,flues,windows,boxes,**extra):
 iw,ih=Image.open(root/(k+'.webp')).size
 # Same fixed door offsets for relocated homes; use relative rather than
 # absolute coordinates so staged Artisan District placement still works.
 geometry=dict(w=w,h=h,dx=round(offset-(door[0]-.5)*w,6),artDy=round((1-door[1])*h,6),doorHeight=h*doorHeight,doorWorldOffset=offset,boxes=boxes,rx=max(abs(b[i]) for b in boxes for i in (0,2)),ry=max(abs(b[1]) for b in boxes),flue=flues[0][0],flueY=flues[0][1],**extra)
 return dict(file=k+'.webp',width=iw,height=ih,door=door,doorHeight=doorHeight,doorWidth=doorWidth,flues=flues,lanterns=[],windows=windows,geometry=geometry)
forward=house('forward',322,274,[.347,.986],-40,.298,.156,[[.061,.010],[.094,.047]],[
 window(.134,.460,.176,.535,True),window(.425,.460,.484,.556,False),window(.627,.467,.685,.539,True),window(.124,.743,.174,.833,True),window(.556,.740,.639,.850,False),window(.839,.767,.867,.836,False)
],[[ -145,-45,-64,-4],[-16,-45,145,-4],[-64,-45,-16,-15]],y=2360)
deepstone=house('deepstone',266,396,[.308,.995],-76,.236,.188,[[.095,.008],[.134,.008]],[
 window(.456,.235,.543,.307,False),window(.222,.416,.357,.498,False),window(.547,.420,.653,.477,False),window(.677,.422,.726,.477,True),window(.225,.605,.348,.682,False),window(.602,.607,.700,.690,True),window(.511,.797,.641,.886,False),window(.740,.827,.774,.865,False)
],[[-140.6,-64.66,-100,-4],[-52,-64.66,107.06,-4],[-100,-64.66,-52,-15]])
meta={'homes':{'forward':forward,'deepstone':deepstone},'ground':[
 {'key':'cottageCourt','x':4430,'y':2348,'w':341,'h':83,'shape':[[4441,2360],[4490,2357],[4565,2360],[4630,2357],[4719,2363],[4750,2377],[4729,2405],[4660,2417],[4595,2416],[4565,2424],[4520,2412],[4465,2405],[4443,2389]],'kind':'threshold','seed':15171},
 {'key':'stoneCourt','x':4771,'y':2284,'w':296,'h':76,'shape':[[4780,2300],[4825,2295],[4864,2289],[4910,2292],[4960,2291],[5032,2299],[5051,2313],[5033,2331],[4950,2348],[4864,2345],[4800,2336],[4780,2321]],'kind':'damp','seed':15172},
 {'key':'sideLane','x':4736,'y':2130,'w':72,'h':210,'shape':[[4756,2140],[4777,2138],[4794,2170],[4790,2220],[4797,2283],[4792,2323],[4768,2329],[4750,2309],[4752,2220],[4747,2170]],'kind':'lane','seed':15173},
 {'key':'foundryCrossing','x':537,'y':1375,'w':202,'h':123,'shape':[[580,1382],[639,1385],[692,1397],[723,1423],[699,1468],[647,1486],[590,1485],[548,1456],[555,1415]],'kind':'lane','seed':15174},
 {'key':'foundryCorner','x':1023,'y':1369,'w':149,'h':102,'shape':[[1035,1380],[1092,1376],[1154,1398],[1155,1441],[1109,1459],[1052,1450],[1032,1426]],'kind':'damp','seed':15175}
 ],
 'routes':[
 {'key':'cottageDoor','points':[[4565,2376],[4565,2408],[4565,2418]],'half':8},
 {'key':'cottageFront','points':[[4490,2377],[4565,2377],[4705,2377]],'half':8},
 {'key':'stoneDoor','points':[[4864,2306],[4864,2315],[4770,2315]],'half':8},
 {'key':'stoneLane','points':[[4770,2315],[4770,2170],[4770,2120]],'half':12}
 ]}
(root/'layout-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
