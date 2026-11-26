// V1539: render a real aspect-matched world viewport, not a stretched 16:9 picture.
// The original logical view defines combat distances; only view-dependent operations use W/H.
const DF1539_BASE_W=1280,DF1539_BASE_H=720;
let W=DF1539_BASE_W,H=DF1539_BASE_H;
function df1539ViewSize(cssW,cssH,mobile=false){
 const ratio=cssW/cssH,base=DF1539_BASE_W/DF1539_BASE_H;
 const cap=Math.floor(DF1539_BASE_W*DF1539_BASE_H*(mobile?1:1.25));
 if(!Number.isFinite(ratio)||ratio<=0)return {width:DF1539_BASE_W,height:DF1539_BASE_H,cap};
 let w=ratio>=base?DF1539_BASE_H*ratio:DF1539_BASE_W;
 let h=ratio>=base?DF1539_BASE_H:DF1539_BASE_W/ratio;
 // Never exceed the small Hollow Courtyard map, or the device's pixel budget.
 const scale=Math.min(1,Math.sqrt(cap/(w*h)),2400/w,1900/h);
 w=Math.max(1,Math.floor(w*scale));h=Math.max(1,Math.floor(h*scale));
 return {width:w,height:h,cap};
}
function df1539Pointer(clientX,clientY,rect){
 return {x:(clientX-rect.left)/rect.width*W,y:(clientY-rect.top)/rect.height*H};
}
let df1539ResizeCount=0,df1539ResizePending=false,df1539PixelCap=DF1539_BASE_W*DF1539_BASE_H;
function df1539Resize(){
 df1539ResizePending=false;
 const r=canvas.getBoundingClientRect();
 if(r.width<2||r.height<2)return;
 const mobile=thornMobileLite||!!window.matchMedia?.('(hover:none),(pointer:coarse),(max-width:800px)').matches;
 const fit=df1539ViewSize(r.width,r.height,mobile);
 df1539PixelCap=fit.cap;
 document.getElementById('gameWrap').style.setProperty('--df1539-road-bottom',Math.ceil(r.top+52*r.height/fit.height+10)+'px');
 if(W===fit.width&&H===fit.height&&canvas.width===W&&canvas.height===H)return;
 W=fit.width;H=fit.height;
 canvas.width=W;canvas.height=H;
 df1539ResizeCount++;
}
function df1539Schedule(){
 if(df1539ResizePending)return;
 df1539ResizePending=true;requestAnimationFrame(df1539Resize);
}
function df1539Install(){
 df1539Resize();
 if(typeof ResizeObserver==='function')new ResizeObserver(df1539Schedule).observe(canvas.parentElement);
 window.addEventListener('resize',df1539Schedule,{passive:true});
 window.visualViewport?.addEventListener('resize',df1539Schedule,{passive:true});
 document.addEventListener('fullscreenchange',df1539Schedule);
 document.addEventListener('webkitfullscreenchange',df1539Schedule);
}
// Read-only diagnostics test the identical coordinate transform used for click-to-target.
window.DarkFallForestViewport=()=>{
 const r=canvas.getBoundingClientRect(),stage=canvas.parentElement.getBoundingClientRect(),wrap=document.getElementById('gameWrap').getBoundingClientRect();
 const box=q=>({x:q.x,y:q.y,width:q.width,height:q.height});
 const point=df1539Pointer(r.left+r.width*.237,r.top+r.height*.681,r);
 return {logical:[W,H],backing:[canvas.width,canvas.height],css:box(r),stage:box(stage),wrap:box(wrap),
  viewport:[innerWidth,innerHeight],nativeFullscreen:!!(document.fullscreenElement||document.webkitFullscreenElement),
  scaleMismatch:Math.abs((r.width/W)/(r.height/H)-1),pointerError:Math.max(Math.abs(point.x-W*.237),Math.abs(point.y-H*.681)),
  area:W*H,cap:df1539PixelCap,resizeCount:df1539ResizeCount,
  camera:started?cam():null,player:started?{x:p.x,y:p.y}:null};
};
