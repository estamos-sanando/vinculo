import sys
import os

def modify(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, not found")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update DB object
    db_old = """    async addMood(em) { const l = await this.moods(); l.push({emotion:em, timestamp:new Date().toISOString()}); await this.set('moods', l); },
    async clear() { for (const k of ['entries','moods','userName','pinHash','termsAccepted','reflection','microRef','todaySem','isFirstEntry','firstEntrySem']) { await this.remove(k); } }
  };"""
    db_new = """    async addMood(em) { const l = await this.moods(); l.push({emotion:em, timestamp:new Date().toISOString()}); await this.set('moods', l); },
    async contacts() { return (await this.get('contacts')) || []; },
    async saveContact(c) { const l = await this.contacts(); c.id = Date.now(); l.push(c); await this.set('contacts', l); },
    async deleteContact(id) { const l = await this.contacts(); const nl = l.filter(x => x.id !== id); await this.set('contacts', nl); },
    async clear() { for (const k of ['entries','moods','userName','pinHash','termsAccepted','reflection','microRef','todaySem','isFirstEntry','firstEntrySem','contacts']) { await this.remove(k); } }
  };"""
    content = content.replace(db_old, db_new)

    # 2. Update HTML Contacts Container
    html_old = """    <h3 style="margin-bottom:10px;font-size:.92rem">👥 Contactos de confianza</h3>
    <div class="contact-card"><div class="contact-avatar">👩</div><div class="contact-info"><h4>María (amiga)</h4><p>Siempre escucha</p></div><button class="contact-btn" onclick="window.open('https://wa.me/?text=Hola%20Mar%C3%ADa%2C%20necesito%20hablar%20con%20vos', '_blank')">💬</button></div>
    <div class="contact-card"><div class="contact-avatar">👩‍⚕️</div><div class="contact-info"><h4>Dra. López</h4><p>Psicóloga</p></div><button class="contact-btn" onclick="window.open('https://calendar.google.com/calendar/render?action=TEMPLATE&text=Turno+Psic%C3%B3loga', '_blank')">📅</button></div>
    <div class="contact-card"><div class="contact-avatar">👩‍👧</div><div class="contact-info"><h4>Mamá</h4><p>Contención familiar</p></div><button class="contact-btn" onclick="window.location.href='tel:123456789'">📞</button></div>

    <button class="btn-primary" style="margin-top:12px" onclick="shareApp()">+ Invitar a alguien</button>"""
    
    html_new = """    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
      <h3 style="font-size:.92rem; margin:0;">👥 Contactos de confianza</h3>
      <button onclick="openContactModal()" style="background:none;border:none;color:var(--lila-dark);font-size:.85rem;font-weight:600;cursor:pointer;">+ Agregar</button>
    </div>
    <div id="contactsContainer"></div>

    <button class="btn-primary" style="margin-top:12px" onclick="shareApp()">Compartir App</button>"""
    content = content.replace(html_old, html_new)

    # 3. Add Modal HTML
    modal_html = """<!-- Contact Modal -->
<div class="safety-modal" id="contactModal">
  <div class="safety-content">
    <h2>➕ Nuevo Contacto</h2>
    <div class="form-group">
      <label class="form-label">Nombre</label>
      <input type="text" id="cntName" class="onboarding-input" placeholder="Ej: María">
    </div>
    <div class="form-group">
      <label class="form-label">Rol / Relación</label>
      <input type="text" id="cntRole" class="onboarding-input" placeholder="Ej: Amiga, Psicóloga">
    </div>
    <div class="form-group">
      <label class="form-label">Método de contacto</label>
      <select id="cntMethod" class="onboarding-input" onchange="updCntPlaceholder()">
        <option value="wa">WhatsApp</option>
        <option value="tel">Llamada telefónica</option>
        <option value="link">Link / Recordatorio</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Dato (Número o URL)</label>
      <input type="text" id="cntTarget" class="onboarding-input" placeholder="Ej: 1154321098">
    </div>
    <button class="btn-call" onclick="saveContact()">Guardar Contacto</button>
    <button class="btn-dismiss" onclick="closeContactModal()">Cancelar</button>
  </div>
</div>

<!-- Safety Modal -->"""
    content = content.replace('<!-- Safety Modal -->', modal_html)

    # 4. Add JavaScript Logic
    js_code = """function updCntPlaceholder() {
  const method = document.getElementById('cntMethod').value;
  const input = document.getElementById('cntTarget');
  if (method === 'wa') input.placeholder = 'Ej: 1154321098 (sin 0 ni 15)';
  else if (method === 'tel') input.placeholder = 'Ej: 011154321098';
  else input.placeholder = 'Ej: https://calendar.google.com/...';
}

function openContactModal() {
  document.getElementById('cntName').value = '';
  document.getElementById('cntRole').value = '';
  document.getElementById('cntTarget').value = '';
  document.getElementById('cntMethod').value = 'wa';
  updCntPlaceholder();
  document.getElementById('contactModal').classList.add('visible');
}

function closeContactModal() {
  document.getElementById('contactModal').classList.remove('visible');
}

async function saveContact() {
  const name = document.getElementById('cntName').value.trim();
  const role = document.getElementById('cntRole').value.trim();
  const method = document.getElementById('cntMethod').value;
  const target = document.getElementById('cntTarget').value.trim();
  
  if (!name || !target) { toast('Faltan datos'); return; }
  
  let action = '';
  let icon = '';
  let avatar = '👤';
  if (method === 'wa') { action = `window.open('https://wa.me/${target}', '_blank')`; icon = '💬'; avatar = '👩'; }
  else if (method === 'tel') { action = `window.location.href='tel:${target}'`; icon = '📞'; avatar = '👩‍👧'; }
  else { action = `window.open('${target}', '_blank')`; icon = '📅'; avatar = '👩‍⚕️'; }
  
  await DB.saveContact({ name, role, method, target, action, icon, avatar });
  closeContactModal();
  renderContacts();
  toast('Contacto guardado');
}

async function deleteContact(id) {
  if (confirm('¿Seguro querés eliminar este contacto?')) {
    await DB.deleteContact(id);
    renderContacts();
    toast('Contacto eliminado');
  }
}

async function renderContacts() {
  const container = document.getElementById('contactsContainer');
  if (!container) return;
  const contacts = await DB.contacts();
  
  if (contacts.length === 0) {
    container.innerHTML = '<p style="font-size:.8rem;color:var(--text-muted);text-align:center;margin-bottom:14px;">No tenés contactos de confianza agregados aún. Agregá uno para tenerlo siempre a mano.</p>';
    return;
  }
  
  let html = '';
  contacts.forEach(c => {
    html += `<div class="contact-card">
      <div class="contact-avatar">${c.avatar}</div>
      <div class="contact-info">
        <h4>${c.name}</h4><p>${c.role}</p>
      </div>
      <button class="contact-btn" onclick="${c.action}">${c.icon}</button>
      <button class="contact-btn" style="background:none;color:var(--alert-dark);margin-left:4px;font-size:1.1rem;" onclick="deleteContact(${c.id})">🗑️</button>
    </div>`;
  });
  container.innerHTML = html;
}

// Call renderContacts in doInit()
function shareApp() {"""
    
    # Inject JavaScript logic into the script tag
    content = content.replace('function shareApp() {', js_code)

    # Make sure we render contacts on startup
    init_old = """  if (!APP.name) {
    document.getElementById('onboard').classList.add('active');
  } else {
    document.getElementById('settName').textContent = APP.name;
    document.querySelector('.app-container').classList.add('active');"""
    
    init_new = """  if (!APP.name) {
    document.getElementById('onboard').classList.add('active');
  } else {
    document.getElementById('settName').textContent = APP.name;
    document.querySelector('.app-container').classList.add('active');
    renderContacts();"""
    content = content.replace(init_old, init_new)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully modified {filepath}")

modify('index.html')
modify('Vínculo.html')
