const slides=[...document.querySelectorAll('[data-slide]')];
let current=0;
for(const [index,slide] of slides.entries()){
  const step=slide.dataset.step;
  const progress=document.createElement('div');progress.className='workflow';progress.setAttribute('aria-label','Participant workflow');
  for(const label of ['Inspect','Detect','Check evidence','Submit']){const entry=document.createElement('span');entry.textContent=label;if(label===step)entry.className='current';progress.append(entry);}
  const number=document.createElement('span');number.className='number';number.textContent=String(index+1).padStart(2,'0')+' / '+slides.length;
  slide.append(progress,number);
}
function showSlide(index){current=Math.max(0,Math.min(index,slides.length-1));slides.forEach((slide,i)=>slide.classList.toggle('active',i===current));}
function fit(){document.querySelector('.stage').style.transform='scale('+Math.min(innerWidth/1920,innerHeight/1080)+')';}
showSlide(Number(new URLSearchParams(location.search).get('slide')||1)-1);fit();addEventListener('resize',fit);
addEventListener('keydown',event=>{if(event.target.closest('input,textarea,select,button,a')||event.altKey||event.ctrlKey||event.metaKey)return;if(event.key==='ArrowRight'){event.preventDefault();showSlide(current+1)}if(event.key==='ArrowLeft'){event.preventDefault();showSlide(current-1)}});
window.showSlide=showSlide;
