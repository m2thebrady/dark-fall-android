import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const dir='game-bundle/patches/art-v1524/';
const a=JSON.parse(readFileSync(dir+'landscape.json','utf8'));
assert.equal(a.tiles.length,27);assert.equal(a.materials.length,4);assert.ok(a.links.length>=8);assert.ok(a.gardens.length>=10);
assert.equal(new Set(a.tiles.map(t=>t.key)).size,27);
for(const f of [...a.tiles.map(t=>t.file),'map.webp','frontages.webp']){
 const b=readFileSync(dir+f);assert.equal(b.subarray(0,4).toString(),'RIFF');assert.equal(b.subarray(8,12).toString(),'WEBP');assert.ok(b.length>10000);
}
assert.ok(a.links.every(r=>r.points.length>=2&&r.width>=46&&r.points.every(([x,y])=>x>=0&&x<=6460&&y>=0&&y<=2600)));
assert.ok(a.gardens.every(g=>g.w<=114&&g.h<=50));
assert.equal(a.geometry,'unchanged');
const js=readFileSync('game-bundle/patches/royal-haven-v1524.js','utf8');
assert.ok(!js.includes('drawImage')&&!js.includes('requestAnimationFrame')&&!js.includes('setInterval'));
console.log('V1524 four terrain materials, 27 baked tiles and clear garden paths: asset validation PASS');
