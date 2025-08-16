(function(){
  const historyEl=document.getElementById('chatHistory');
  const inputEl=document.getElementById('chatInput');
  const sendBtn=document.getElementById('sendBtn');
  const clearBtn=document.getElementById('clearBtn');
  const sessionId=localStorage.getItem('chat_session_id')||crypto.randomUUID();
  localStorage.setItem('chat_session_id',sessionId);

  if(window.marked){
    marked.setOptions({gfm:true, breaks:true});
  }

  function addMsg(role, content){
    const wrap=document.createElement('div');
    wrap.className='chat-msg '+role;
    const bubble=document.createElement('div');
    bubble.className='chat-bubble';
    if(role==='assistant' && window.marked && window.DOMPurify){
      const html=marked.parse(content||'');
      bubble.innerHTML=DOMPurify.sanitize(html);
    } else {
      bubble.textContent=content;
    }
    wrap.appendChild(bubble);
    historyEl.appendChild(wrap);
    historyEl.scrollTop=historyEl.scrollHeight;
  }

  // Try to parse coordinates from free text. Supports:
  //  - "56.126917, 40.397011"
  //  - "56.126917 N, 40.397011 E" (ignores N/S/E/W sign)
  function parseCoords(text){
    if(!text) return null;
    const t=text.trim();
    // Replace commas-as-decimals (rare) by dot first? We keep default dot.
    // Pattern 1: simple lat,lon numbers
    let m=t.match(/([-+]?\d{1,2}\.\d+)\s*,\s*([-+]?\d{1,3}\.\d+)/);
    if(m){
      const lat=parseFloat(m[1]);
      const lon=parseFloat(m[2]);
      if(Number.isFinite(lat) && Number.isFinite(lon)) return {lat, lon};
    }
    // Pattern 2: with N/S/E/W
    m=t.match(/([-+]?\d{1,2}\.\d+)\s*([NS])[^\d]+([-+]?\d{1,3}\.\d+)\s*([EW])/i);
    if(m){
      let lat=parseFloat(m[1]);
      let lon=parseFloat(m[3]);
      const ns=m[2].toUpperCase();
      const ew=m[4].toUpperCase();
      if(ns==='S') lat=-Math.abs(lat);
      if(ew==='W') lon=-Math.abs(lon);
      if(Number.isFinite(lat) && Number.isFinite(lon)) return {lat, lon};
    }
    return null;
  }

  async function reverseGeocodeAndDescribe(lat, lon){
    const resp = await fetch('/reverse_geocode',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({latitude:lat, longitude:lon})
    });
    const data = await resp.json();
    if(!resp.ok){
      throw new Error(data && data.error ? data.error : 'Ошибка реверс‑геокодинга');
    }
    const address = data.address || 'Адрес не найден';
    const descr = data.ai_description || 'Описание не получено';
    return {address, descr};
  }

  async function send(){
    const text=inputEl.value.trim();
    if(!text) return;
    addMsg('user', text);
    inputEl.value='';
    try{
      // If user sent coordinates, use OSM -> AI pipeline
      const coords = parseCoords(text);
      if(coords){
        const {address, descr} = await reverseGeocodeAndDescribe(coords.lat, coords.lon);
        addMsg('assistant', `Адрес по OSM:\n${address}\n\nОписание:\n${descr}`);
        return;
      }

      // Fallback to regular chat
      const res=await fetch('/api/chat',{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({session_id:sessionId,messages:[{role:'user',content:text}]})
      });
      const data=await res.json();
      if(data.answer){ addMsg('assistant', data.answer); }
      else if(data.error){ addMsg('assistant', 'Ошибка: '+(data.error||'Неизвестно')); }
    }catch(e){ addMsg('assistant','Сеть недоступна'); }
  }

  async function clearHistory(){
    historyEl.innerHTML='';
    await fetch('/api/chat/clear',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sessionId})});
  }

  sendBtn.addEventListener('click', send);
  inputEl.addEventListener('keydown', e=>{if(e.key==='Enter') send();});
  clearBtn.addEventListener('click', clearHistory);
})();
