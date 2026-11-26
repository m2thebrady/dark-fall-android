import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
const scope=vm.createContext({});
vm.runInContext(readFileSync('game-bundle/patches/royal-haven-v1510.js','utf8'),scope);
const {rh1457Overlap:overlap,rh1510WeatherPixels:wear}=scope;
const bounds={left:50,top:20,w:100,h:180};
assert.equal(overlap(bounds,200,100,130),true,'behind a building anywhere, not just a marked lane');
assert.equal(overlap(bounds,200,100,205),false,'in front of a building');
assert.equal(overlap(bounds,200,300,130),false,'beside a distant building');
assert.equal(overlap(bounds,200,100,-120),false,'above its roof');
assert.equal(overlap(null,200,100,130),false);
const w=160,h=170,original=new Uint8ClampedArray(w*h*4);
for(let y=0;y<h;y++)for(let x=0;x<w;x++){
 const i=(y*w+x)*4;original.set(x<18?[20,20,20,0]:x<35?[235,174,33,255]:[139,132,117,255],i);
}
const a=original.slice(),b=original.slice(),different=original.slice();
wear(a,w,h,47390,{hearth:true,flues:[[.5,.15]]});
wear(b,w,h,47390,{hearth:true,flues:[[.5,.15]]});
wear(different,w,h,47391,{green:true});
assert.deepEqual(a,b,'deterministic weathering across frames');
assert.notDeepEqual(a,original,'weathering changes visible masonry');
assert.notDeepEqual(a,different,'separate buildings have distinct patina');
let material=0,window=0,n=0;
for(let i=0;i<a.length;i+=4){
 assert.equal(a[i+3],original[i+3],'alpha/silhouette preserved');
 if(original[i+3]===0)assert.deepEqual(a.slice(i,i+4),original.slice(i,i+4),'transparent edges preserved');
 if(original[i]===139){material+=Math.abs(a[i]-original[i]);n++;}
 if(original[i]===235)window+=Math.abs(a[i]-original[i]);
}
assert.ok(material/n>2,'masonry wear is visible');
assert.ok(window/(17*h)<material/n,'bright shop glass and signage relatively protected');
console.log('Royal Haven geometry, deterministic weathering, colour protection and silhouette tests PASS');
