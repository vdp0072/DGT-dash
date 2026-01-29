const API_URL = window.location.origin + "/api";

// --- State ---
let currentUser = null;
let currentToken = localStorage.getItem('dgt_token');
let currentSort = 'name';
let currentOrder = 'asc';

// --- Elements ---
const appState = {
    views: {
        auth: document.getElementById('auth-view'),
        dashboard: document.getElementById('dashboard-view')
    },
    pages: {
        search: document.getElementById('page-search'),
        ingest: document.getElementById('page-ingest'),
        lookup: document.getElementById('page-lookup'),
        logs: document.getElementById('page-logs')
    }
};

// --- Init ---
async function init() {
    if (currentToken) {
        try {
            const payload = parseJwt(currentToken);
            if (payload.exp * 1000 < Date.now()) {
                logout();
            } else {
                currentUser = { username: payload.sub, role: payload.role };
                showDashboard();
            }
        } catch (e) {
            logout();
        }
    } else {
        showAuth();
    }
}

// --- Auth Functions ---
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('auth-error');

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) throw new Error('Invalid credentials');

        const data = await response.json();
        currentToken = data.access_token;
        localStorage.setItem('dgt_token', currentToken);
        currentUser = { username, role: data.role };

        showDashboard();
    } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
    }
});

document.getElementById('logout-btn').addEventListener('click', logout);

function logout() {
    currentToken = null;
    currentUser = null;
    localStorage.removeItem('dgt_token');
    showAuth();
}

function parseJwt(token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

// --- Navigation ---
function showAuth() {
    appState.views.auth.classList.remove('hidden');
    appState.views.dashboard.classList.add('hidden');
}

function showDashboard() {
    appState.views.auth.classList.add('hidden');
    appState.views.dashboard.classList.remove('hidden');

    document.getElementById('display-username').textContent = currentUser.username;
    document.getElementById('display-role').textContent = currentUser.role.toUpperCase();

    // Permissions
    if (currentUser.role === 'admin' || currentUser.role === 'superuser') {
        document.getElementById('admin-ingest-link').classList.remove('hidden');
        document.getElementById('admin-lookup-link').classList.remove('hidden');
        document.getElementById('admin-logs-link').classList.remove('hidden');
    } else {
        document.getElementById('admin-ingest-link').classList.add('hidden');
        document.getElementById('admin-lookup-link').classList.add('hidden');
        document.getElementById('admin-logs-link').classList.add('hidden');
    }

    showPage('search');
}

window.showPage = function (pageId) {
    Object.values(appState.pages).forEach(p => p.classList.add('hidden'));
    document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));

    appState.pages[pageId].classList.remove('hidden');

    if (pageId === 'ingest') document.getElementById('admin-ingest-link').classList.add('active');
    else if (pageId === 'lookup') document.getElementById('admin-lookup-link').classList.add('active');
    else if (pageId === 'logs') document.getElementById('admin-logs-link').classList.add('active');
    else document.querySelector('.nav-links li:first-child').classList.add('active');
}


// --- Search Logic ---
document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const q = document.getElementById('q-general').value;
    const city = document.getElementById('q-city').value;
    const area = document.getElementById('q-area').value;
    await performSearch(q, city, area);
});

window.handleSort = function (field) {
    if (currentSort === field) {
        currentOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort = field;
        currentOrder = 'asc';
    }

    document.querySelectorAll('th.sortable i').forEach(i => i.className = 'fa-solid fa-sort');
    const activeHeader = document.querySelector(`th[onclick="handleSort('${field}')"]`);
    const icon = activeHeader.querySelector('i');
    icon.className = currentOrder === 'asc' ? 'fa-solid fa-sort-up' : 'fa-solid fa-sort-down';

    const q = document.getElementById('q-general').value;
    const city = document.getElementById('q-city').value;
    const area = document.getElementById('q-area').value;
    performSearch(q, city, area);
}

async function performSearch(q, city, area) {
    const loading = document.getElementById('loading-indicator');
    const tableBody = document.getElementById('results-body');
    const noResults = document.getElementById('no-results');
    const meta = document.getElementById('results-meta');

    loading.classList.remove('hidden');
    tableBody.innerHTML = '';
    noResults.classList.add('hidden');
    meta.classList.add('hidden');

    try {
        const params = new URLSearchParams({
            limit: 50,
            sort_by: currentSort,
            order: currentOrder
        });
        if (q) params.append('q', q);
        if (city) params.append('city', city);
        if (area) params.append('area', area);

        const res = await fetch(`${API_URL}/search?${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });

        const data = await res.json();
        loading.classList.add('hidden');

        if (data.results.length === 0) {
            noResults.classList.remove('hidden');
            return;
        }

        meta.classList.remove('hidden');
        document.getElementById('total-count').textContent = data.total_count || data.results.length;

        data.results.forEach(rec => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${rec.name}</td>
                <td>${rec.fathers_name || '-'}</td>
                <td>${rec.age || '-'}</td>
                <td>${rec.gender || '-'}</td>
                <td>${rec.city || '-'}</td>
                <td>${rec.area || '-'}</td>
                <td>${rec.company || '-'}</td>
                <td>${rec.phone || '-'}</td>
                <td>${rec.misc || '-'}</td>
            `;
            tableBody.appendChild(tr);
        });

    } catch (err) {
        loading.classList.add('hidden');
        alert("Search failed: " + err.message);
    }
}

// --- Phone Lookup Logic ---
document.getElementById('lookup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const phoneInput = document.getElementById('lookup-phone').value.trim();
    if (!phoneInput) return;

    // Apply 91 prefix if not present
    let phone = phoneInput.replace(/\D/g, ''); // strip non-digits
    if (!phone.startsWith('91')) {
        phone = '91' + phone;
    }

    const loading = document.getElementById('lookup-loading');
    const content = document.getElementById('lookup-content');

    loading.classList.remove('hidden');
    content.innerHTML = '';

    try {
        const res = await fetch(`${API_URL}/lookup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ phone })
        });

        if (!res.ok) throw new Error('Lookup failed or unauthorized');

        const data = await res.json();
        loading.classList.add('hidden');
        renderLookupResults(data);

    } catch (err) {
        loading.classList.add('hidden');
        content.innerHTML = `<div class="error-msg">Error: ${err.message}</div>`;
    }
});

function renderLookupResults(data) {
    const content = document.getElementById('lookup-content');
    const container = document.createElement('div');
    container.className = 'lookup-results-container';

    // Findings
    for (const [provider, result] of Object.entries(data.findings)) {
        const card = document.createElement('div');
        card.className = 'finding-card';
        card.innerHTML = `
            <h4><i class="fa-solid fa-circle-check"></i> ${provider}</h4>
            <div class="finding-content">${result}</div>
        `;
        container.appendChild(card);
    }

    // Errors
    for (const [provider, err] of Object.entries(data.errors)) {
        const card = document.createElement('div');
        card.className = 'finding-card error';
        card.innerHTML = `
            <h4><i class="fa-solid fa-circle-exclamation"></i> ${provider}</h4>
            <div class="finding-content">${err}</div>
        `;
        container.appendChild(card);
    }

    if (Object.keys(data.findings).length === 0 && Object.keys(data.errors).length === 0) {
        content.innerHTML = `<div class="empty-state"><p>No intelligence found for this number.</p></div>`;
    } else {
        content.appendChild(container);
    }
}

// --- Ingestion Logic ---
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
let selectedFile = null;

if (dropZone) dropZone.addEventListener('click', () => fileInput.click());
if (fileInput) fileInput.addEventListener('change', (e) => handleFileSelect(e.target.files[0]));

if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files[0]);
    });
}

function handleFileSelect(file) {
    if (!file) return;
    selectedFile = file;
    document.getElementById('selected-file-name').textContent = file.name;
    document.getElementById('selected-file-name').classList.remove('hidden');
    document.getElementById('upload-btn').disabled = false;
}

document.getElementById('upload-btn').addEventListener('click', async () => {
    if (!selectedFile) return;

    const progress = document.getElementById('upload-progress');
    const summary = document.getElementById('upload-summary');
    const btn = document.getElementById('upload-btn');

    progress.classList.remove('hidden');
    summary.classList.add('hidden');
    btn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const res = await fetch(`${API_URL}/admin/ingest`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentToken}` },
            body: formData
        });

        const data = await res.json();
        progress.classList.add('hidden');
        summary.classList.remove('hidden');
        btn.disabled = false;

        document.getElementById('summary-inserted').textContent = data.inserted_rows;
        document.getElementById('summary-rejected').textContent = data.rejected_rows;
        document.getElementById('summary-total').textContent = data.total_rows;

        if (data.status !== 'success') {
            const reason = document.getElementById('summary-reason');
            reason.textContent = data.rejection_reason || "Ingestion failed";
            reason.classList.remove('hidden');
        }

    } catch (err) {
        progress.classList.add('hidden');
        alert("Upload failed: " + err.message);
        btn.disabled = false;
    }
});

// --- Clear Database Logic ---
document.getElementById('clear-db-btn').addEventListener('click', async () => {
    const confirmation = prompt("This will wipe ALL records and logs. Type 'clear' to proceed:");

    if (confirmation === 'clear') {
        try {
            const res = await fetch(`${API_URL}/admin/clear-db`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${currentToken}` }
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Failed to clear database");
            }

            alert("Database cleared successfully!");
            if (!appState.pages.search.classList.contains('hidden')) {
                performSearch('', '', '');
            }
        } catch (err) {
            alert("Error: " + err.message);
        }
    } else if (confirmation !== null) {
        alert("Confirmation failed. Database not cleared.");
    }
});

// Start
init();
