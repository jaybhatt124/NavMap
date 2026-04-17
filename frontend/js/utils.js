// ── Shared utilities across all pages ──────────────────────────

const API = '/api';

async function apiFetch(path, opts = {}) {
    const token = localStorage.getItem('nm_token') || '';
    const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch(API + path, { ...opts, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
}

async function apiForm(path, formData) {
    const token = localStorage.getItem('nm_token') || '';
    const res = await fetch(API + path, {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token },
        body: formData
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Upload failed');
    return data;
}

function toast(msg, dur = 2800) {
    let t = document.getElementById('toast');
    if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t); }
    t.textContent = msg;
    t.style.display = 'block';
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.style.display = 'none', dur);
}

function openModal(id)  { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

function showErr(id, msg) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = msg;
    el.style.display = 'block';
}

function getAuth() {
    return {
        token:   localStorage.getItem('nm_token')    || '',
        orgId:   localStorage.getItem('nm_org_id')   || '',
        orgName: localStorage.getItem('nm_org_name') || ''
    };
}

function setAuth(d) {
    localStorage.setItem('nm_token',    d.token);
    localStorage.setItem('nm_org_id',   d.org_id);
    localStorage.setItem('nm_org_name', d.org_name);
}

function clearAuth() {
    localStorage.removeItem('nm_token');
    localStorage.removeItem('nm_org_id');
    localStorage.removeItem('nm_org_name');
}

function requireAuth() {
    const { token } = getAuth();
    if (!token) { window.location.href = '/login'; return false; }
    return true;
}
