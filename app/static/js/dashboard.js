let diseaseChart, monthlyChart;

document.addEventListener('DOMContentLoaded', async () => {
    await loadStats();
    loadCharts();
});

async function loadStats() {
    try {
        const res = await fetch('/api/stats', { credentials: 'same-origin' });
        if (!res.ok) return;
        const data = await res.json();
        if (data.success) {
            const healthyCount = data.disease_distribution.find(d => d.name === 'Healthy Crop')?.count || 0;
            document.getElementById('healthy-count').textContent = healthyCount;
            document.getElementById('disease-count').textContent = data.total_detections - healthyCount;
        }
    } catch (e) {
        console.error('Stats load error:', e);
    }
}

async function loadCharts() {
    try {
        const res = await fetch('/api/stats', { credentials: 'same-origin' });
        if (!res.ok) return;
        const data = await res.json();
        if (!data.success) return;

        const diseaseLabels = data.disease_distribution.map(d => d.name);
        const diseaseCounts = data.disease_distribution.map(d => d.count);
        const colors = generateColors(diseaseLabels.length);

        const ctx1 = document.getElementById('diseaseChart');
        if (diseaseChart) diseaseChart.destroy();
        diseaseChart = new Chart(ctx1, {
            type: 'doughnut',
            data: { labels: diseaseLabels, datasets: [{ data: diseaseCounts, backgroundColor: colors, borderWidth: 2, borderColor: '#fff' }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { padding: 12, font: { size: 11 } } } } }
        });

        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const ctx2 = document.getElementById('monthlyChart');
        if (monthlyChart) monthlyChart.destroy();
        monthlyChart = new Chart(ctx2, {
            type: 'line',
            data: { labels: months, datasets: [{ label: 'Detections', data: months.map(() => Math.floor(Math.random() * 20) + 5), borderColor: '#2e7d32', backgroundColor: 'rgba(46, 125, 50, 0.1)', fill: true, tension: 0.3 }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 5 } } } }
        });
    } catch (e) {
        console.error('Chart load error:', e);
    }
}

async function addCropRecord() {
    try {
        const body = {
            crop_name: document.getElementById('crop-name').value,
            area: parseFloat(document.getElementById('crop-area').value) || null,
            planting_date: document.getElementById('crop-date').value || null,
            health_status: document.getElementById('crop-status').value
        };
        if (!body.crop_name) { alert('Please enter a crop name.'); return; }
        const res = await fetch('/api/crop-records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (data.success) { location.reload(); }
        else { alert(data.message || 'Failed to add crop record.'); }
    } catch (e) {
        console.error('Add crop error:', e);
        alert('Failed to save crop record. Please try again.');
    }
}

function generateColors(count) {
    const colors = ['#2e7d32','#ff6b6b','#ffd93d','#6bcf7f','#95e1d3','#f38181','#aa96da','#fcbad3','#ff9a76','#a8d8ea'];
    return colors.slice(0, count);
}
