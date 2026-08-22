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

/* Reflete XP, nível e conquistas ganhas na sidebar e no chat. */
function aplicarGanhos(data) {
  const fill = document.getElementById('sidebarXpFill');
  const txt = document.getElementById('sidebarNivelTxt');
  if (fill && txt && typeof data.xp_total === 'number') {
    const restante = Math.max(1, data.xp_proximo_nivel || 1);
    const pct = Math.min(100, Math.floor((data.xp_total * 100) / (data.xp_total + restante)));
    fill.style.width = pct + '%';
    txt.textContent = `Nível ${data.nivel} · ${data.xp_total} XP`;
  }

  if (data.xp_ganho) {
    addSystemChip(`+${data.xp_ganho} XP por essa interação`);
  }
  if (data.subiu_de_nivel) {
    addSystemChip(`🎉 Você subiu para o nível ${data.nivel}!`);
  }
  (data.conquistas_novas || []).forEach(c => {
    addSystemChip(`🏆 Conquista desbloqueada: ${c.icone || ''} ${c.nome} (+${c.xp_bonus} XP)`);
  });

  if (typeof data.etapa_atual === 'number' && data.licao_total) {
    lessonProgress = data.etapa_atual;
    renderSteps();
    if (data.licao_concluida) {
      addSystemChip('✅ Lição concluída! +20 XP de bônus');
    }
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
