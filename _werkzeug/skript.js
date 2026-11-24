// ================= Grundlagen =================
const $=id=>document.getElementById(id);
const fmt=(n,d=0)=>Number(n).toLocaleString('de-DE',{minimumFractionDigits:d,maximumFractionDigits:d});
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const zahl=(v,min,max)=>{let n=parseInt(String(v).replace(/[^0-9-]/g,''),10);if(!isFinite(n))n=min;return Math.min(max,Math.max(min,n));};
// Gramm sinnvoll runden und anzeigen
function gramm(g){if(g<=0)return '0 g';if(g<1000)return fmt(Math.round(g/5)*5)+' g';return fmt(Math.round(g/50)*50/1000,g<10000?2:1).replace(/,?0+$/,'')+' kg';}
function ml(m){if(m<1000)return fmt(Math.round(m/10)*10)+' ml';return fmt(Math.round(m/100)*100/1000,1).replace(/,0$/,'')+' l';}

// ================= Kennung (ref) und Zählung =================
const params=new URLSearchParams(location.search);
const REF=(params.get('ref')||'direkt').toLowerCase().replace(/[^a-z0-9-]/g,'').slice(0,40)||'direkt';
const REF_W=REF.endsWith('-w')?REF:REF+'-w';
const gezaehlt={};
function senden(path,title,versuch){
  try{if(window.goatcounter&&window.goatcounter.count){window.goatcounter.count({path,title,event:true});return;}}catch(e){return;}
  if(versuch<40)setTimeout(()=>senden(path,title,versuch+1),250);
}
function zaehle(art){const key='person-'+art+'--'+REF;if(gezaehlt[key])return;gezaehlt[key]=1;senden(key,'Mengen pro Person: '+art+' ('+REF+')',0);}
// Nutzung = der Besucher stellt selbst etwas ein (nicht: bloßes Öffnen oder Antippen eines Feldes)
const genutzt=()=>zaehle('nutzung');

// ================= Zustand =================
const Z={tab:'beilage',sorte:'basmati',art:'beilage',p:4,k:0,hunger:'normal',anlass:'buffet',g:20,gk:0,h:4,titel:'',items:[]};
// items: [was, menge, wer, erledigt(0/1)]

function hashLesen(){
  const h=decodeURIComponent(location.hash.slice(1));
  if(!h)return;
  const [tab,rest]=h.split('?');
  if(['beilage','feier','liste'].includes(tab))Z.tab=tab;
  const q=new URLSearchParams(rest||'');
  if(q.has('sorte')&&D.sorten[q.get('sorte')])Z.sorte=q.get('sorte');
  if(q.get('art')==='haupt'||q.get('art')==='beilage')Z.art=q.get('art');
  if(q.has('p'))Z.p=zahl(q.get('p'),0,500);
  if(q.has('k'))Z.k=zahl(q.get('k'),0,500);
  if(D.hunger[q.get('hunger')])Z.hunger=q.get('hunger');
  if(D.feier[q.get('anlass')])Z.anlass=q.get('anlass');
  if(q.has('g'))Z.g=zahl(q.get('g'),0,1000);
  if(q.has('gk'))Z.gk=zahl(q.get('gk'),0,1000);
  if(q.has('h'))Z.h=zahl(q.get('h'),1,24);
  if(q.has('l')){const l=listeDekodieren(q.get('l'));if(l){Z.titel=l.t;Z.items=l.i;}}
  if(q.get('geteilt')==='1')$('geteiltHinweis').classList.remove('hide');
}
function hashFuer(tab,mitListe){
  let q;
  if(tab==='beilage')q=new URLSearchParams({sorte:Z.sorte,art:Z.art,p:Z.p,k:Z.k,hunger:Z.hunger});
  else if(tab==='feier')q=new URLSearchParams({anlass:Z.anlass,g:Z.g,gk:Z.gk,h:Z.h});
  else{q=new URLSearchParams();if(mitListe)q.set('l',listeKodieren());}
  return '#'+tab+(String(q)?'?'+q:'');
}
function hashSchreiben(){try{history.replaceState(null,'',location.pathname+location.search+hashFuer(Z.tab,Z.tab==='liste'));}catch(e){}}

// Liste im Link: JSON → UTF-8 → base64url
function listeKodieren(){
  const json=JSON.stringify({t:Z.titel,i:Z.items});
  const bytes=new TextEncoder().encode(json);let bin='';bytes.forEach(b=>bin+=String.fromCharCode(b));
  return btoa(bin).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
function listeDekodieren(s){
  try{const b64=s.replace(/-/g,'+').replace(/_/g,'/');const bin=atob(b64);const bytes=Uint8Array.from(bin,c=>c.charCodeAt(0));
    const o=JSON.parse(new TextDecoder().decode(bytes));
    const t=String(o.t||'').slice(0,80);
    const i=(Array.isArray(o.i)?o.i:[]).filter(x=>Array.isArray(x)).map(x=>[String(x[0]||'').slice(0,60),String(x[1]||'').slice(0,40),String(x[2]||'').slice(0,40),x[3]?1:0]);
    return {t,i};
  }catch(e){return null;}
}

// ================= Beilage =================
function beilageRechnen(){
  const s=D.sorten[Z.sorte];
  const jeP=(Z.art==='haupt'?s.h:s.b)*D.hunger[Z.hunger];
  const personen=Z.p+Z.k*D.kinderFaktor;
  const roh=jeP*personen;
  return {s,jeP,personen,roh,wasser:s.wasserJeG?roh*s.wasserJeG:0};
}
function beilageZeigen(){
  const r=beilageRechnen(),s=r.s;
  const wer=(Z.p?Z.p+' Erwachsene':'')+(Z.p&&Z.k?' + ':'')+(Z.k?Z.k+' Kinder':'');
  let html='';
  if(r.personen<=0){html='<p class="gross">Bitte mindestens eine Person eintragen.</p>';}
  else{
    html+=`<p class="gross">${gramm(r.roh)} ${esc(s.kurz)} ${s.roh?'roh':''}</p>`;
    html+=`<div>für ${esc(wer)} als ${Z.art==='haupt'?'Hauptgericht':'Beilage'} (${fmt(Math.round(r.jeP))} g je Erwachsenem${Z.k?', Kinder die Hälfte':''})</div><ul>`;
    if(s.wasserJeG)html+=`<li><b>Wasser:</b> etwa ${ml(r.wasser)} – ${esc(s.wasserRegel)}</li>`;
    else if(s.wasserRegel)html+=`<li><b>Wasser:</b> ${esc(s.wasserRegel)}</li>`;
    html+=`<li><b>Garzeit:</b> ${esc(s.zeit)}</li>`;
    if(s.packung){const pk=r.roh/s.packung;html+=`<li><b>Einkauf:</b> ${pk<=1?'1 Packung':fmt(Math.ceil(pk*2)/2,1).replace(/,0$/,'')+' Packungen'} à ${gramm(s.packung)} (${esc(s.packungText)})</li>`;}
    const hungerText=Z.hunger==='viel'?' Hunger „groß“: +25 %, „wenig“: −20 % (eigene Annahme).':Z.hunger==='wenig'?' Hunger „wenig“: −20 %, „groß“: +25 % (eigene Annahme).':'';
    const kinderText=Z.k?' Kinder bis etwa 10 Jahre zählen halb (Annahme nach den DGE-Richtwerten für den Energiebedarf).':'';
    html+=`</ul><p class="klein">Richtwert, Quelle: ${esc(s.quelle)}.${hungerText}${kinderText} Packungsangabe geht vor.</p>`;
  }
  $('beilageErgebnis').innerHTML=html;
}

// ================= Feier =================
function feierRechnen(){
  const a=D.feier[Z.anlass];
  const E=Z.g,K=Z.gk,H=Z.h;
  const posten=a.posten.map(p=>{
    let menge;
    const trinken=(E*D.getraenk.erwachsene+K*D.getraenk.kinder)*H;
    if(p.typ==='getraenk')menge=trinken;
    else if(p.typ==='getraenkOhneKaffee'){const kaffee=a.posten.find(x=>x.kinderJeP===0);menge=Math.max(0,trinken-E*(kaffee?kaffee.jeP:0));}
    else menge=E*p.jeP+K*(p.kinderJeP!==undefined?p.kinderJeP:p.jeP*D.kinderFaktor);
    return {...p,menge};
  });
  return {a,posten};
}
function mengeText(p){
  const m=p.menge;
  if(p.einheit==='g')return gramm(m);
  if(p.einheit==='l')return fmt(Math.ceil(m*2)/2,1).replace(/,0$/,'')+' l';
  if(p.einheit==='stueck'){const n=Math.ceil(m);let t=fmt(n)+' '+(n===1?p.stueckEins:p.stueckViele);
    if(p.kuchen){t+=` (≈ ${fmt(Math.ceil(n/D.kuchen.blech))} Blechkuchen à ${D.kuchen.blech} Stück oder ${fmt(Math.ceil(n/D.kuchen.rund))} runde Kuchen à ${D.kuchen.rund} Stück)`;}
    return t;}
  return fmt(m);
}
function feierZeigen(){
  const r=feierRechnen();
  if(Z.g+Z.gk<=0){$('feierErgebnis').innerHTML='<p class="gross">Bitte mindestens einen Gast eintragen.</p>';return;}
  let html=`<p class="gross">${esc(r.a.name)} für ${Z.g+Z.gk} Gäste</p><table><tbody>`;
  r.posten.forEach(p=>{html+=`<tr><td>${esc(p.name)}<div class="klein">${esc(p.hinweis||'')}</div></td><td class="r"><b>${mengeText(p)}</b></td></tr>`;});
  html+=`</tbody></table><p class="klein">${esc(r.a.notiz)} Kinder bis etwa 10 Jahre zählen beim Essen halb. Richtwerte, Quellen: ${esc(r.a.quelle)}.</p>`;
  $('feierErgebnis').innerHTML=html;
}

// ================= Liste =================
function listeZeigen(){
  $('titel').value=Z.titel;
  const ul=$('items');ul.innerHTML='';
  Z.items.forEach((it,i)=>{
    const li=document.createElement('li');if(it[3])li.className='done';
    li.innerHTML=`<input type="checkbox" ${it[3]?'checked':''} aria-label="erledigt" data-i="${i}"><div><span class="was">${esc(it[0])}</span> <span class="menge">${esc(it[1])}</span></div><button class="weg" data-weg="${i}" aria-label="entfernen">×</button><input class="wer" type="text" maxlength="40" placeholder="Wer bringt es mit?" value="${esc(it[2])}" data-wer="${i}">`;
    ul.appendChild(li);
  });
  $('listeLeer').classList.toggle('hide',Z.items.length>0);
  $('listeWhatsapp').href='https://wa.me/?text='+encodeURIComponent(teilText('liste'));
}
function zurListe(eintraege){
  eintraege.forEach(e=>{const vorhanden=Z.items.find(x=>x[0]===e[0]);if(vorhanden)vorhanden[1]=e[1];else Z.items.push([e[0],e[1],'',0]);});
  if(!Z.titel)Z.titel=Z.tab==='feier'?D.feier[Z.anlass].name+' ('+(Z.g+Z.gk)+' Gäste)':'Einkauf';
  genutzt();listeZeigen();tab('liste');
  $('listeMsg').textContent='In die Liste übernommen ✓';setTimeout(()=>$('listeMsg').textContent='',2500);
}

// ================= Teilen =================
function teilUrl(t){
  const basis=location.href.split(/[?#]/)[0]+'?ref='+encodeURIComponent(REF_W);
  if(t==='liste')return basis+'#liste?'+new URLSearchParams({l:listeKodieren(),geteilt:'1'});
  return basis+hashFuer(t,false);
}
function teilText(t){
  if(t==='liste'){
    const zeilen=Z.items.map(it=>'• '+it[0]+(it[1]?' – '+it[1]:'')+(it[2]?' ('+it[2]+')':'')).join('\n');
    return (Z.titel||'Mitbringliste')+'\n'+zeilen+'\n\nWer bringt was? Im Link abhaken und den neuen Link zurückschicken:\n'+teilUrl('liste');
  }
  if(t==='beilage'){const r=beilageRechnen();return gramm(r.roh)+' '+r.s.kurz+' für '+(Z.p+Z.k)+' Personen'+(r.s.wasserJeG?', Wasser etwa '+ml(r.wasser):'')+'. Nachrechnen: '+teilUrl('beilage');}
  return D.feier[Z.anlass].name+' für '+(Z.g+Z.gk)+' Gäste – Mengen: '+teilUrl('feier');
}
async function teilen(t,msgEl){
  genutzt();zaehle('teilen');
  const text=teilText(t);
  try{if(navigator.share){await navigator.share({text});return;}}catch(e){if(e&&e.name==='AbortError')return;}
  try{await navigator.clipboard.writeText(text);msgEl.textContent='Text mit Link kopiert ✓ – jetzt in die Gruppe einfügen.';}
  catch(e){msgEl.textContent='Bitte den Link oben aus der Adresszeile kopieren.';}
  setTimeout(()=>msgEl.textContent='',4000);
}

// ================= Oberfläche =================
function tab(t){
  Z.tab=t;
  document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.tab===t));
  ['beilage','feier','liste'].forEach(id=>$(id).classList.toggle('hide',id!==t));
  hashSchreiben();
}
function pills(id,key,cb){
  const el=$(id);
  el.querySelectorAll('[data-v]').forEach(b=>b.classList.toggle('on',b.dataset.v===Z[key]));
  el.addEventListener('click',e=>{const b=e.target.closest('[data-v]');if(!b)return;Z[key]=b.dataset.v;el.querySelectorAll('[data-v]').forEach(x=>x.classList.toggle('on',x===b));genutzt();cb();hashSchreiben();});
}
function zahlFeld(id,key,min,max,cb){
  const el=$(id);el.value=Z[key];
  el.addEventListener('input',()=>{Z[key]=zahl(el.value,min,max);genutzt();cb();hashSchreiben();});
  el.addEventListener('blur',()=>{el.value=Z[key];});
}
document.querySelectorAll('.num button').forEach(b=>b.addEventListener('click',()=>{
  const el=$(b.dataset.f);const n=zahl(el.value,0,1000)+parseInt(b.dataset.d,10);el.value=Math.max(parseInt(el.min,10)||0,Math.min(parseInt(el.max,10)||1000,n));el.dispatchEvent(new Event('input'));
}));

function start(){
  hashLesen();
  const sel=$('sorte');
  Object.entries(D.sorten).forEach(([id,s])=>{const o=document.createElement('option');o.value=id;o.textContent=s.name;sel.appendChild(o);});
  sel.value=Z.sorte;
  sel.addEventListener('change',()=>{Z.sorte=sel.value;genutzt();beilageZeigen();hashSchreiben();});
  pills('art','art',beilageZeigen);pills('hunger','hunger',beilageZeigen);pills('anlass','anlass',feierZeigen);
  zahlFeld('p','p',0,500,beilageZeigen);zahlFeld('k','k',0,500,beilageZeigen);
  zahlFeld('g','g',0,1000,feierZeigen);zahlFeld('gk','gk',0,1000,feierZeigen);zahlFeld('h','h',1,24,feierZeigen);
  $('tabs').addEventListener('click',e=>{const b=e.target.closest('[data-tab]');if(b)tab(b.dataset.tab);});
  $('beilageZurListe').addEventListener('click',()=>{const r=beilageRechnen();zurListe([[r.s.kurz+(Z.art==='haupt'?' (Hauptgericht)':' (Beilage)'),gramm(r.roh)]]);});
  $('feierZurListe').addEventListener('click',()=>{const r=feierRechnen();zurListe(r.posten.map(p=>[p.name,mengeText(p).replace(/ \(≈.*\)$/,'')]));});
  $('beilageTeilen').addEventListener('click',()=>teilen('beilage',$('beilageMsg')));
  $('feierTeilen').addEventListener('click',()=>teilen('feier',$('feierMsg')));
  $('listeTeilen').addEventListener('click',()=>teilen('liste',$('listeMsg')));
  $('listeWhatsapp').addEventListener('click',()=>{genutzt();zaehle('teilen');});
  $('listeDrucken').addEventListener('click',()=>{genutzt();window.print();});
  $('titel').addEventListener('input',()=>{Z.titel=$('titel').value.slice(0,80);genutzt();hashSchreiben();$('listeWhatsapp').href='https://wa.me/?text='+encodeURIComponent(teilText('liste'));});
  $('items').addEventListener('change',e=>{const i=e.target.dataset.i;if(i!==undefined){Z.items[i][3]=e.target.checked?1:0;genutzt();listeZeigen();hashSchreiben();}});
  $('items').addEventListener('input',e=>{const i=e.target.dataset.wer;if(i!==undefined){Z.items[i][2]=e.target.value.slice(0,40);genutzt();hashSchreiben();$('listeWhatsapp').href='https://wa.me/?text='+encodeURIComponent(teilText('liste'));}});
  $('items').addEventListener('click',e=>{const i=e.target.dataset.weg;if(i!==undefined){Z.items.splice(i,1);genutzt();listeZeigen();hashSchreiben();}});
  $('addForm').addEventListener('submit',e=>{e.preventDefault();const n=$('neuName').value.trim().slice(0,60);if(!n)return;Z.items.push([n,$('neuMenge').value.trim().slice(0,40),'',0]);$('neuName').value='';$('neuMenge').value='';genutzt();listeZeigen();hashSchreiben();$('neuName').focus();});
  allesZeigen();
  if(location.hash&&location.hash.length>1)document.getElementById('tabs').scrollIntoView({block:'start'});
  // Wird nur der Teil hinter # geändert (z. B. ein zweiter Link im selben Tab), neu einlesen
  window.addEventListener('hashchange',()=>{hashLesen();allesZeigen();});
}
function allesZeigen(){
  $('sorte').value=Z.sorte;['p','k','g','gk','h'].forEach(id=>{$(id).value=Z[id];});
  [['art','art'],['hunger','hunger'],['anlass','anlass']].forEach(([id,key])=>$(id).querySelectorAll('[data-v]').forEach(b=>b.classList.toggle('on',b.dataset.v===Z[key])));
  beilageZeigen();feierZeigen();listeZeigen();tab(Z.tab);
}
start();
