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

  async function send(){
    const text=inputEl.value.trim();
    if(!text) return;
    addMsg('user', text);
    inputEl.value='';
    try{
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
