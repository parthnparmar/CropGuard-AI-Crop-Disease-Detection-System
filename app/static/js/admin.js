document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    loadDiseases();

    document.getElementById('user-search').addEventListener('input', function() {
        const q = this.value.toLowerCase();
        document.querySelectorAll('#users-tbody tr').forEach(tr => {
            tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
    });

    document.querySelector('[data-bs-target="#tab-analytics"]').addEventListener('shown.bs.tab', loadAnalytics);
});

async function loadUsers() {
    const res = await fetch('/admin/api/users');
    const data = await res.json();
    const tbody = document.getElementById('users-tbody');
    if (!data.success || !data.data.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No farmers registered yet.</td></tr>';
        return;
    }
    tbody.innerHTML = data.data.map(u => `
        <tr>
            <td>${u.id}</td>
            <td class="fw-semibold">${u.username}</td>
            <td>${u.email}</td>
            <td>${u.phone || '—'}</td>
            <td><span class="badge bg-success">${u.detection_count}</span></td>
            <td><small>${u.created_at.substring(0, 10)}</small></td>
            <td><button class="btn btn-outline-danger btn-sm" onclick="deleteUser(${u.id}, '${u.username}')"><i class="fas fa-trash"></i></button></td>
        </tr>
    `).join('');
}

async function deleteUser(id, name) {
    if (!confirm(`Delete farmer "${name}"? This will remove all their data.`)) return;
    const res = await fetch(`/admin/api/users/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) { alert('User deleted.'); loadUsers(); }
}

async function loadDiseases() {
    const res = await fetch('/admin/api/diseases');
    const data = await res.json();
    const tbody = document.getElementById('diseases-tbody');
    tbody.innerHTML = data.data.map(d => `
        <tr>
            <td class="fw-semibold">${d.name}</td>
            <td><span class="badge bg-success-subtle text-success">${d.crop_type}</span></td>
            <td><small class="text-muted">${(d.symptoms || '').substring(0, 60)}...</small></td>
            <td>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteDisease(${d.id}, '${d.name}')"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

async function addDisease() {
    const body = {
        name: document.getElementById('d-name').value,
        crop_type: document.getElementById('d-crop').value,
        symptoms: document.getElementById('d-symptoms').value,
        causes: document.getElementById('d-causes').value,
        organic_treatment: document.getElementById('d-organic').value,
        chemical_treatment: document.getElementById('d-chemical').value,
        preventive_measures: document.getElementById('d-preventive').value
    };
    const res = await fetch('/admin/api/diseases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const data = await res.json();
    if (data.success) { alert('Disease added!'); bootstrap.Modal.getInstance(document.getElementById('addDiseaseModal')).hide(); loadDiseases(); }
}

async function deleteDisease(id, name) {
    if (!confirm(`Delete disease "${name}"?`)) return;
    const res = await fetch(`/admin/api/diseases/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) { alert('Disease deleted.'); loadDiseases(); }
}

async function loadAnalytics() {
    const res = await fetch('/admin/api/analytics');
    const data = await res.json();
    if (!data.success) return;

    const colors = ['#2e7d32','#ff6b6b','#ffd93d','#6bcf7f','#95e1d3','#f38181','#aa96da','#fcbad3','#ff9a76','#a8d8ea'];

    new Chart(document.getElementById('adminDiseaseChart'), {
        type: 'bar',
        data: {
            labels: data.disease_distribution.map(d => d.name),
            datasets: [{ label: 'Detections', data: data.disease_distribution.map(d => d.count), backgroundColor: colors }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });

    new Chart(document.getElementById('adminMonthlyChart'), {
        type: 'line',
        data: {
            labels: data.monthly_detections.map(d => d.month),
            datasets: [{ label: 'Detections', data: data.monthly_detections.map(d => d.count), borderColor: '#2e7d32', backgroundColor: 'rgba(46,125,50,0.1)', fill: true, tension: 0.3 }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
}
