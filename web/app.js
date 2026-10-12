let previous = null;
const $ = id => document.getElementById(id);
const labels = {allow:'İzin verildi',deny:'Reddedildi',unreadable:'Okunamadı',error:'Hata',open:'Aç',close:'Kapat',none:'Yok'};
async function api(path, body) {
  const options = body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)};
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}
function cell(row, value) { const td=document.createElement('td'); td.textContent=value; row.append(td); }
async function refresh() {
  const state=await api('/api/state');
  $('arm').classList.toggle('open',state.barrier==='open_waiting_clear');
  $('barrier-state').textContent=state.barrier==='closed'?'Kapalı':'Açık, alan boşluğu doğrulaması bekliyor';
  $('clear').disabled=state.barrier==='closed';
  $('allowlist').replaceChildren();
  state.allowed_plates.forEach(plate=>{const li=document.createElement('li');li.textContent=plate+' ';const b=document.createElement('button');b.textContent='Sil';b.type='button';b.onclick=()=>run(async()=>{await api('/api/plates/remove',{plate});await refresh();});li.append(b);$('allowlist').append(li);});
  $('events').replaceChildren();
  state.events.forEach(e=>{const row=document.createElement('tr');[new Date(e.created_at).toLocaleTimeString('tr-TR'),e.plate||'—',e.confidence.toFixed(2),labels[e.decision],e.reason,labels[e.barrier_action]].forEach(v=>cell(row,v));$('events').append(row);});
}
async function run(fn) {try {await fn();} catch(e) {$('result').textContent='İstek başarısız: '+e.message;}}
async function scan(replay=false) {
  const body=replay?previous:{request_id:crypto.randomUUID(),plate:$('plate').value,confidence:Number($('confidence').value),fault:$('fault').value};
  const result=await api('/api/demo/scan',body);
  previous=body;$('replay').disabled=false;
  $('result').textContent=`${labels[result.decision]} · ${result.reason} · ${result.duplicate?'Tekrar istek, yeni hareket yok':'Yeni kayıt'}`;
  await refresh();
}
$('scan').onsubmit=e=>{e.preventDefault();run(()=>scan());};
$('confidence').oninput=()=>$('score').textContent=Number($('confidence').value).toFixed(2);
$('denied').onclick=()=>{$('plate').value='35 ABC 999';$('confidence').value='0.96';$('score').textContent='0.96';$('fault').value='none';run(()=>scan());};
$('low').onclick=()=>{$('plate').value='34 DMO 01';$('confidence').value='0.40';$('score').textContent='0.40';$('fault').value='none';run(()=>scan());};
$('replay').onclick=()=>run(()=>scan(true));
$('clear').onclick=()=>run(async()=>{await api('/api/demo/clear',{});$('result').textContent='Sanal alan boşluğu doğrulandı.';await refresh();});
$('add').onsubmit=e=>{e.preventDefault();run(async()=>{await api('/api/plates/add',{plate:$('new-plate').value});$('new-plate').value='';await refresh();});};
run(refresh);
