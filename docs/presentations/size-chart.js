(() => {
  const svg = document.getElementById('sankey');
  if (!svg) return;
  const NS = 'http://www.w3.org/2000/svg';
  const modes = {
    size: {
      unit: 'GB', flows: [[91597167/1e9,(57042412195-91597167)/1e9],[243510166/1e9,(16110686496-243510166)/1e9]], digits: 2,
      targets: ['Signal products','Size reduction'],
      caption: 'Selected recordings only. Widths use one linear byte scale. Camera companions are separate.'
    }
  };
  const add = (tag, attrs, text, parent = svg) => {
    const el = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k,v));
    if (text !== undefined) el.textContent = text;
    parent.appendChild(el);
    return el;
  };
  function draw(mode) {
    svg.replaceChildren();
    const {unit,flows,digits,targets,caption} = modes[mode];
    const totals = flows.map(row => row.reduce((a,b) => a+b,0));
    const dest = [0,1].map(j => flows[0][j]+flows[1][j]);
    const scale = 320 / totals.reduce((a,b) => a+b,0);
    const sy = [60,60+totals[0]*scale+70];
    const ty = [60,60+dest[0]*scale+80];
    const sourceUsed = [0,0], targetUsed = [0,0];
    const colors = ['#23777b','#b87540'];
    const label = value => `${value.toFixed(digits)} ${unit}`;
    add('title',{},`Dataset ${mode === 'size' ? 'file-size accounting' : 'split'} in ${unit}`);
    add('desc',{},`Kashiwa and Reims flow into ${targets.join(', ')}. Band width represents ${unit}.`);
    flows.forEach((row,i) => row.forEach((value,j) => {
      if (!value) return;
      const h = value*scale, a = sy[i]+sourceUsed[i], b = ty[j]+targetUsed[j];
      const path = add('path',{d:`M 222 ${a} C 395 ${a}, 480 ${b}, 650 ${b} L 650 ${b+h} C 480 ${b+h}, 395 ${a+h}, 222 ${a+h} Z`,fill:colors[i],'fill-opacity':.3});
      add('title',{},`${['Kashiwa','Reims'][i]} → ${targets[j]}: ${mode === 'size' && j === 0 ? `${(value*1000).toFixed(2)} MB` : label(value)}`,path);
      sourceUsed[i]+=h; targetUsed[j]+=h;
    }));
    totals.forEach((v,i) => {
      add('rect',{x:200,y:sy[i],width:22,height:v*scale,fill:colors[i],rx:2});
      add('text',{x:184,y:sy[i]+v*scale/2-8,'text-anchor':'end'},['Kashiwa','Reims'][i]);
      add('text',{x:184,y:sy[i]+v*scale/2+15,'text-anchor':'end',class:'sub'},label(v));
    });
    dest.forEach((v,j) => {
      add('rect',{x:650,y:ty[j],width:22,height:v*scale,fill:'#52656f',rx:2});
      add('text',{x:687,y:ty[j]+v*scale/2-5},targets[j]);
      add('text',{x:687,y:ty[j]+v*scale/2+18,class:'sub'},mode === 'size' && j === 0 ? `${(v*1000).toFixed(2)} MB` : label(v));
    });
    document.getElementById('diagram-caption').textContent = caption;
    svg.setAttribute('aria-label',`Dataset ${mode === 'size' ? 'recording size' : mode} Sankey`);
    document.querySelectorAll('[data-mode]').forEach(b => {
      b.setAttribute('aria-pressed',String(b.dataset.mode===mode));
      b.setAttribute('aria-expanded',String(b.dataset.mode===mode));
    });
    document.querySelectorAll('[data-view]').forEach(section => { section.hidden = section.dataset.view !== mode; });
  }
  document.querySelectorAll('[data-mode]').forEach(b => b.addEventListener('click',() => draw(b.dataset.mode)));
  document.querySelectorAll('[data-answer]').forEach(b => b.addEventListener('click',() => {
    document.getElementById('feedback').textContent = b.dataset.answer==='correct'
      ? 'Correct. Topic filtering removes heavy payloads while keeping the selected signal samples across nearly the full parent span.'
      : 'Try again. 0.161% measures file bytes. It does not measure recording time or the proportion of true events.';
  }));
  draw('size');
})();
