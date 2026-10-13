import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, mkdtemp } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const argv=process.argv.slice(2),options={};
for(let i=0;i<argv.length;i+=2){assert.ok(argv[i].startsWith('--')&&argv[i+1],'Expected --option value');options[argv[i].slice(2)]=argv[i+1];}
for(const key of ['sources','browser','assets','output'])assert.ok(options[key],`Missing --${key}`);
const sources=path.resolve(options.sources),output=path.resolve(options.output);
const assets=JSON.parse((await readFile(path.resolve(options.assets),'utf8')).replace(/^\uFEFF/,''));
assert.match(assets.source_sha256,/^[a-f0-9]{64}$/,'Missing source identity');
assert.match(assets.label_pack_sha256,/^[a-f0-9]{64}$/,'Missing practice identity');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),images={};
for(const [name,item] of Object.entries(assets.assets)){
 assert.match(name,/^[a-z-]+\.png$/,'Invalid image role');const bytes=await readFile(item.path);assert.equal(hash(bytes),item.sha256,`Changed asset: ${name}`);images[name]='data:image/png;base64,'+bytes.toString('base64');
}
const sourceFiles=['briefing.html','submission-checklist.html','theme.css','slides.js','size-chart.js'];
for(const file of sourceFiles)await readFile(path.join(sources,file));
await mkdir(output); // Refuse overwrite. Parent must exist.
const profile=await mkdtemp(path.join(output,'browser-profile-'));
const child=spawn(options.browser,['--headless=new','--disable-gpu','--window-size=1920,1080','--force-device-scale-factor=1','--hide-scrollbars','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{windowsHide:true,stdio:'ignore'});
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));let ws,send;
try{
 let port;for(let i=0;i<100;i++){try{port=(await readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{await delay(100);}}
 assert.ok(port,'Browser endpoint absent');const targets=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(targets.find(item=>item.type==='page').webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});let nextId=0;const pending=new Map(),external=[];
 send=(method,params={})=>new Promise((resolve,reject)=>{const id=++nextId;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 ws.onmessage=event=>{const m=JSON.parse(event.data);if(m.method==='Network.requestWillBeSent'&&/^https?:/.test(m.params.request.url))external.push(m.params.request.url);const call=pending.get(m.id);if(call){pending.delete(m.id);m.error?call.reject(Error(JSON.stringify(m.error))):call.resolve(m.result);}};
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});assert.ok(!r.exceptionDetails,JSON.stringify(r.exceptionDetails));return r.result.value;};
 await send('Page.enable');await send('Network.enable');await send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false});
 const manifest={kind:'civ.presentation-render/v1',source_sha256:assets.source_sha256,label_pack_sha256:assets.label_pack_sha256,width:1920,height:1080,source_files:{},assets:{},decks:[],browser:(await send('Browser.getVersion')).product,node_version:process.version};
 for(const file of sourceFiles)manifest.source_files[file]=hash(await readFile(path.join(sources,file)));
 for(const [name,item] of Object.entries(assets.assets))manifest.assets[name]=item.sha256;
 for(const [name,file,count] of [['briefing','briefing.html',13],['submission-checklist','submission-checklist.html',1]]){
  await send('Page.navigate',{url:pathToFileURL(path.join(sources,file)).href});let loaded=false;for(let attempt=0;attempt<100;attempt++){await delay(100);loaded=await evaluate("document.readyState==='complete'&&typeof window.showSlide==='function'");if(loaded)break;}assert.ok(loaded,'Source page did not finish loading');
  assert.equal(await evaluate("document.querySelectorAll('[data-slide]').length"),count,'Unexpected slide count');
  await evaluate(`(()=>{const images=${JSON.stringify(images)},evidence=${JSON.stringify(assets.evidence)};for(const image of document.querySelectorAll('[data-asset]')){if(!images[image.dataset.asset])throw Error('Missing image '+image.dataset.asset);image.src=images[image.dataset.asset];}for(const node of document.querySelectorAll('[data-evidence]')){if(!evidence[node.dataset.evidence])throw Error('Missing evidence '+node.dataset.evidence);node.textContent=evidence[node.dataset.evidence];}return true;})()`);
  await evaluate("Promise.all([...document.images].map(image=>image.decode())).then(()=>document.fonts.ready).then(()=>true)");const slides=[];
  for(let i=0;i<count;i++){
   await evaluate(`showSlide(${i})`);await evaluate("new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))");await delay(500);
   const bounds=await evaluate("(()=>{const s=document.querySelector('.slide.active');return [...s.querySelectorAll('h1,p,pre,table,img,svg,.workflow,.number')].filter(n=>getComputedStyle(n).display!=='none').map(n=>{const r=n.getBoundingClientRect();return {tag:n.tagName,x:r.left,y:r.top,right:r.right,bottom:r.bottom};});})()");
   for(const r of bounds)assert.ok(r.x>=-1&&r.y>=-1&&r.right<=1921&&r.bottom<=1081,`Slide ${i+1} clips ${r.tag}`);
   const overlap=await evaluate("(()=>{const s=document.querySelector('.slide.active'),f=s.querySelector('.workflow').getBoundingClientRect();return [...s.children].filter(n=>!n.classList.contains('note')&&!n.classList.contains('workflow')&&!n.classList.contains('number')&&getComputedStyle(n).display!=='none').some(n=>n.getBoundingClientRect().bottom>f.top-12);})()");assert.equal(overlap,false,`Slide ${i+1} overlaps footer`);
   const png=await send('Page.captureScreenshot',{format:'png',clip:{x:0,y:0,width:1920,height:1080,scale:1}}),bytes=Buffer.from(png.data,'base64'),pngFile=`${name}-${String(i+1).padStart(2,'0')}.png`;assert.equal(bytes.readUInt32BE(16),1920);assert.equal(bytes.readUInt32BE(20),1080);await writeFile(path.join(output,pngFile),bytes);
   const notes=await evaluate("document.querySelector('.slide.active .note')?.textContent||''");slides.push({file:pngFile,sha256:hash(bytes),notes});
  }
  manifest.decks.push({name,slides});
 }
 assert.deepEqual(external,[],'External network asset requested');await writeFile(path.join(output,'render-manifest.json'),JSON.stringify(manifest,null,2));console.log('PASS: 13+1 slides, exact asset hashes, no clipping/footer overlaps or external requests.');
}finally{if(send){try{await send('Browser.close');}catch{}}ws?.close();child.kill();}
