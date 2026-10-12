/* Tutor IA — lógica do chat (janela do aluno).
   Padrão: envia a pergunta ao motor do sistema em /api/perguntar/ (Grupo 1).
   Opcional: se o aluno configurar um endpoint próprio (🔑), usa-o no formato OpenAI. */

const CFG = window.CHAT_CONFIG || {};
let conversationHistory = (window.CHAT_HISTORY || []).map(m => ({
  role: m.role === 'aluno' || m.role === 'user' ? 'user' : 'assistant',
  content: m.content
}));
let isLoading = false;
let lessonProgress = Math.max(0, (CFG.stepAtual || 1) - 1);
const TOTAL_STEPS = CFG.totalSteps || 1;

/* ---------- Render ---------- */
function renderSteps() {
  const el = document.getElementById('lessonSteps');
  if (!el) return;
  el.innerHTML = '';
  for (let i = 0; i < TOTAL_STEPS; i++) {
    const s = document.createElement('div');
    s.className = 'step' + (i < lessonProgress ? ' done' : i === lessonProgress ? ' current' : '');
    el.appendChild(s);
  }
}

function addMessage(role, html, isTyping = false) {
  const area = document.getElementById('chatArea');
  const div = document.createElement('div');
  div.className = 'message ' + (role === 'ai' ? 'ai' : 'user');
  if (isTyping) div.id = 'typing-msg';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar ' + (role === 'ai' ? 'ai' : 'user-msg');
  avatar.textContent = role === 'ai' ? '🎓' : '🧑';
  if (role !== 'ai') avatar.style.borderRadius = '10px';

  const body = document.createElement('div');
  body.className = 'msg-body';
  const meta = document.createElement('div');
  meta.className = 'msg-meta';
  meta.textContent = role === 'ai' ? 'Prof. IA · agora' : 'Você · agora';

  const bubble = document.createElement('div');
  bubble.className = 'bubble ' + (role === 'ai' ? 'ai' : 'user');
  bubble.innerHTML = isTyping
    ? '<div class="typing-bubble"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>'
    : html;

  body.appendChild(meta); body.appendChild(bubble);
  div.appendChild(avatar); div.appendChild(body);
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
  return div;
}

function addWelcomeMessage() {
  addMessage('ai', formatMessage(
    `Olá! Sou o **Prof.ia**, seu tutor de *${CFG.disciplina || 'estudos'}*. ` +
    `Pergunte o que quiser, peça uma **dica**, um **exemplo** ou um **exercício** para praticar. 🚀`
  ));
}

function clearChat() {
  document.getElementById('chatArea').innerHTML = '';
  conversationHistory = [];
  addWelcomeMessage();
}

/* ---------- API própria (localStorage) ---------- */
function loadApiConfig() {
  try { return JSON.parse(localStorage.getItem('profIA_apiConfig') || 'null') || { endpoint:'', model:'', key:'' }; }
  catch (e) { return { endpoint:'', model:'', key:'' }; }
}
let apiConfig = loadApiConfig();

function openApiKeyModal() {
  document.getElementById('apiEndpoint').value = apiConfig.endpoint || '';
  document.getElementById('apiModel').value = apiConfig.model || '';
  document.getElementById('apiKeyInput').value = apiConfig.key || '';
  document.getElementById('apiKeyModal').classList.remove('hidden');
}
function closeApiKeyModal() { document.getElementById('apiKeyModal').classList.add('hidden'); }

function saveApiKey() {
  apiConfig = {
    endpoint: document.getElementById('apiEndpoint').value.trim(),
    model:    document.getElementById('apiModel').value.trim(),
    key:      document.getElementById('apiKeyInput').value.trim()
  };
  localStorage.setItem('profIA_apiConfig', JSON.stringify(apiConfig));
  closeApiKeyModal();
}
function clearApiKey() {
  apiConfig = { endpoint:'', model:'', key:'' };
  localStorage.removeItem('profIA_apiConfig');
  document.getElementById('apiEndpoint').value = '';
  document.getElementById('apiModel').value = '';
  document.getElementById('apiKeyInput').value = '';
  closeApiKeyModal();
}

/* ---------- Envio ---------- */
async function sendMessage() {
  const input = document.getElementById('userInput');
  const text = input.value.trim();
  if (!text || isLoading) return;

  input.value = ''; autoResize(input); updateCharCount();
  addMessage('user', escapeHtml(text).replace(/\n/g, '<br>'));
  conversationHistory.push({ role: 'user', content: text });

  isLoading = true;
  document.getElementById('sendBtn').disabled = true;
  const typingEl = addMessage('ai', '', true);

  try {
    if (apiConfig.endpoint) {
      const reply = await callCustomAI(apiConfig, CFG.systemPrompt, conversationHistory);
      typingEl.remove();
      conversationHistory.push({ role: 'assistant', content: reply });
      addMessage('ai', formatMessage(reply));
    } else {
      const data = await callSystemAI(text);
      typingEl.remove();
      conversationHistory.push({ role: 'assistant', content: data.resposta });
      addMessage('ai', formatMessage(data.resposta));
      aplicarGanhos(data);
      oferecerExercicios(data.exercicios || [], text);
    }
  } catch (err) {
    typingEl.remove();
    addMessage('ai', `<span style="color:var(--red)">⚠️ ${escapeHtml(err.message)}</span>`);
  }

  isLoading = false;
  document.getElementById('sendBtn').disabled = false;
}

/* Motor do sistema (Grupo 1, via ponte do Grupo 2):
   POST /aluno/chat/perguntar/ {pergunta, disciplina_id}
   Devolve resposta + xp_ganho + nivel + conquistas_novas etc. */
async function callSystemAI(pergunta) {
  const resp = await fetch(CFG.apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrfToken },
    body: JSON.stringify({ pergunta, disciplina_id: CFG.disciplinaId })
  });
  let data;
  try { data = await resp.json(); } catch (e) { throw new Error('Resposta inválida do servidor.'); }
  if (!resp.ok) throw new Error(data.erro || `Erro do motor de IA (status ${resp.status}).`);
  return data;
}

/* Reflete XP e nível na barra lateral e o progresso da lição.
   Os avisos de XP, nível e conquistas NÃO aparecem mais dentro do chat:
   continuam sendo contados e aparecem na barra lateral e em Meu Desempenho. */
function aplicarGanhos(data) {
  const fill = document.getElementById('sidebarXpFill');
  const txt = document.getElementById('sidebarNivelTxt');
  if (fill && txt && typeof data.xp_total === 'number') {
    const restante = Math.max(1, data.xp_proximo_nivel || 1);
    const pct = Math.min(100, Math.floor((data.xp_total * 100) / (data.xp_total + restante)));
    fill.style.width = pct + '%';
    txt.textContent = `Nível ${data.nivel} · ${data.xp_total} XP`;
  }

  if (typeof data.etapa_atual === 'number' && data.licao_total) {
    lessonProgress = data.etapa_atual;
    renderSteps();
  }
}

function addSystemChip(texto) {
  const area = document.getElementById('chatArea');
  const div = document.createElement('div');
  div.className = 'message ai';
  div.innerHTML = `<div class="msg-avatar ai" style="opacity:.6;">✦</div>
    <div class="msg-body"><div class="bubble ai" style="font-size:12.5px;color:var(--muted);background:transparent;border:1px dashed var(--border2);">${escapeHtml(texto)}</div></div>`;
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}

/* Endpoint próprio (formato OpenAI/Anthropic) */
async function callCustomAI(cfg, systemPrompt, history) {
  const headers = { 'Content-Type': 'application/json' };
  if (cfg.key) headers['Authorization'] = 'Bearer ' + cfg.key;
  const body = { messages: [{ role:'system', content: systemPrompt }, ...history], max_tokens: 1000 };
  if (cfg.model) body.model = cfg.model;
  const resp = await fetch(cfg.endpoint, { method:'POST', headers, body: JSON.stringify(body) });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error?.message || data.error || `Erro na API (status ${resp.status}).`);
  if (data.choices?.[0]?.message?.content) return data.choices[0].message.content;
  if (data.content?.[0]?.text) return data.content[0].text;
  if (data.response) return data.response;
  throw new Error('Formato de resposta não reconhecido.');
}

function sendSuggestion(text) { document.getElementById('userInput').value = text; sendMessage(); }

/* ---------- Exercícios de fixação (questões das provas do professor) ---------- */
/* Cada "Sim" cria uma PRÁTICA PESSOAL do aluno (um quiz só dele), que fica
   salva em Exercícios de Fixação para responder depois ou revisar. */

function contarAlternativas(texto) {
  return (texto || '').split('\n').filter(l => /^\s*[A-Ea-e]\)/.test(l)).length;
}

/* Depois da resposta do tutor: pergunta se o aluno quer praticar */
function oferecerExercicios(questoes, pergunta) {
  questoes = (questoes || []).filter(q => contarAlternativas(q.texto) >= 2);
  if (!questoes.length) return;

  const msg = addMessage('ai',
    formatMessage('Quer praticar com algumas questões?') +
    `<div class="ex-acoes" style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;">
       <button class="btn btn-primary ex-sim">Sim</button>
       <button class="btn ex-nao">Agora não</button>
     </div>`);

  msg.querySelector('.ex-sim').onclick = () => iniciarPratica(msg, questoes, pergunta);
  msg.querySelector('.ex-nao').onclick = () => {
    msg.querySelector('.ex-acoes').remove();
    addMessage('ai', formatMessage('OK! Qual a sua próxima dúvida?'));
    document.getElementById('userInput').focus();
  };
}

/* Cria a prática no servidor e mostra as questões */
async function iniciarPratica(msg, questoes, pergunta) {
  const acoes = msg.querySelector('.ex-acoes');
  acoes.innerHTML = '<span style="font-size:12.5px;color:var(--muted);">Preparando as questões...</span>';

  let data;
  try {
    const resp = await fetch(CFG.praticaUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrfToken },
      body: JSON.stringify({ pergunta, ids: questoes.map(q => q.id), disciplina_id: CFG.disciplinaId })
    });
    data = await resp.json();
    if (!resp.ok) throw new Error(data.erro || 'Não foi possível montar as questões agora.');
  } catch (e) {
    acoes.innerHTML = `<span style="font-size:12.5px;color:var(--red);">⚠️ ${escapeHtml(e.message)}</span>`;
    return;
  }
  acoes.remove();
  mostrarQuestoes(data);
}

/* Mostra todas as questões da prática, com um único botão Corrigir */
function mostrarQuestoes(pratica) {
  const grupo = 'ex' + Date.now();
  const total = pratica.questoes.length;
  let html = '';

  pratica.questoes.forEach((q, i) => {
    html += `<div class="ex-questao" data-qid="${q.id}" style="${i ? 'margin-top:16px;padding-top:14px;border-top:1px solid var(--border2);' : ''}">`;
    html += `<div style="font-size:12px;color:var(--muted);margin-bottom:6px;">Questão ${i + 1} de ${total}</div>`;
    html += `<div style="white-space:pre-wrap;">${escapeHtml(q.enunciado)}</div>`;
    html += '<div class="ex-alts" style="margin-top:10px;display:flex;flex-direction:column;gap:6px;">';
    q.alternativas.forEach(a => {
      html += `<label style="display:flex;gap:8px;align-items:flex-start;cursor:pointer;padding:6px 8px;border:1px solid var(--border2);border-radius:6px;">
        <input type="radio" name="${grupo}_${i}" value="${a.id}" style="margin-top:3px;">
        <span><strong>${a.letra})</strong> ${escapeHtml(a.texto)}</span></label>`;
    });
    html += '</div><div class="ex-feedback" style="margin-top:8px;font-size:13.5px;"></div></div>';
  });
  html += `<div class="ex-rodape" style="margin-top:14px;">
    <button class="btn btn-primary ex-corrigir">Corrigir</button>
    <div style="margin-top:6px;font-size:12px;color:var(--muted);">Esta prática fica salva em Exercícios de Fixação.</div>
  </div>`;

  const msg = addMessage('ai', html);
  msg.querySelector('.ex-corrigir').onclick = () => corrigirQuestoes(msg, pratica, grupo);
}

/* Aviso dentro do bloco de questões (ex.: faltou responder) */
function avisoExercicio(msg, texto) {
  let el = msg.querySelector('.ex-aviso');
  if (!el) {
    el = document.createElement('div');
    el.className = 'ex-aviso';
    el.style.cssText = 'margin-top:8px;font-size:13px;color:var(--red);';
    msg.querySelector('.ex-rodape').appendChild(el);
  }
  el.textContent = '⚠️ ' + texto;
}

/* Envia as respostas, grava a tentativa no servidor e mostra o resultado */
async function corrigirQuestoes(msg, pratica, grupo) {
  const respostas = {};
  for (let i = 0; i < pratica.questoes.length; i++) {
    const marcada = msg.querySelector(`input[name="${grupo}_${i}"]:checked`);
    if (!marcada) { avisoExercicio(msg, 'Responda todas as questões antes de corrigir.'); return; }
    respostas[pratica.questoes[i].id] = marcada.value;
  }

  const botao = msg.querySelector('.ex-corrigir');
  botao.disabled = true;
  botao.textContent = 'Corrigindo...';

  let data;
  try {
    const resp = await fetch(CFG.corrigirUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrfToken },
      body: JSON.stringify({ quiz_id: pratica.quiz_id, respostas })
    });
    data = await resp.json();
    if (!resp.ok) throw new Error(data.erro || 'Não foi possível corrigir agora.');
  } catch (e) {
    botao.disabled = false;
    botao.textContent = 'Corrigir';
    avisoExercicio(msg, e.message);
    return;
  }

  // Em cada questão: trava as alternativas, pinta certa/errada e mostra a justificativa
  (data.resultados || []).forEach(r => {
    const bloco = msg.querySelector(`.ex-questao[data-qid="${r.questao_id}"]`);
    if (!bloco) return;
    const marcada = respostas[r.questao_id];
    bloco.querySelectorAll('.ex-alts label').forEach(l => {
      const radio = l.querySelector('input');
      radio.disabled = true;
      if (String(radio.value) === String(r.alternativa_correta_id)) l.style.background = 'rgba(0,200,100,0.12)';
      else if (String(radio.value) === String(marcada) && !r.correta) l.style.background = 'rgba(220,38,38,0.10)';
    });
    let fb = r.correta
      ? '✅ <strong>Correto!</strong>'
      : `❌ <strong>Não foi dessa vez.</strong> A resposta certa é <strong>${r.letra_correta}</strong>.`;
    if (r.justificativa) fb += `<div style="margin-top:4px;">${escapeHtml(r.justificativa)}</div>`;
    bloco.querySelector('.ex-feedback').innerHTML = fb;
  });

  // Resultado final com a nota (0 a 10)
  const nota = Number(data.nota).toFixed(1).replace('.', ',');
  msg.querySelector('.ex-rodape').innerHTML =
    `<div style="font-size:14px;"><strong>Resultado:</strong> você acertou ${data.acertos} de ${data.total}, nota <strong>${nota}</strong>. ` +
    (data.acertos === data.total ? 'Excelente! 🎉' : 'Se quiser, pergunte sobre o que ficou em dúvida.') +
    `</div><div style="margin-top:6px;font-size:12px;color:var(--muted);">Você pode revisar esta prática em Exercícios de Fixação.</div>`;

  if (data.xp_ganho) aplicarGanhos(data);
  const area = document.getElementById('chatArea');
  area.scrollTop = area.scrollHeight;
}


/* ---------- Utilidades ---------- */
function formatMessage(text) {
  return text
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,'<em>$1</em>')
    .replace(/`(.+?)`/g,'<code>$1</code>')
    .replace(/\n\n/g,'</p><p>').replace(/\n/g,'<br>')
    .replace(/^/,'<p>').replace(/$/, '</p>');
}
function escapeHtml(t) { return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function handleKey(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }
function autoResize(el) { el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 120) + 'px'; }
function updateCharCount() {
  const el = document.getElementById('charCount');
  if (el) el.textContent = `${document.getElementById('userInput').value.length} / 1000`;
}

/* ---------- Início ---------- */
document.addEventListener('DOMContentLoaded', () => {
  renderSteps();
  const area = document.getElementById('chatArea');
  if (conversationHistory.length) {
    conversationHistory.forEach(m =>
      addMessage(m.role === 'user' ? 'user' : 'ai',
                 m.role === 'user' ? escapeHtml(m.content).replace(/\n/g,'<br>') : formatMessage(m.content)));
  } else {
    addWelcomeMessage();
  }
  const modal = document.getElementById('apiKeyModal');
  if (modal) modal.addEventListener('click', e => { if (e.target.id === 'apiKeyModal') closeApiKeyModal(); });
});
