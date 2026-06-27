let selectedFile = null;

const dropZone = document.getElementById('drop-zone');
const imageInput = document.getElementById('image-input');

dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});
imageInput.addEventListener('change', e => { if (e.target.files[0]) handleFile(e.target.files[0]); });

function handleFile(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload a JPG, JPEG, or PNG image.');
        return;
    }
    if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB.');
        return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = e => {
        document.getElementById('preview-img').src = e.target.result;
        document.getElementById('file-name').textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        document.getElementById('preview-section').classList.remove('d-none');
        document.getElementById('result-card').classList.add('d-none');
    };
    reader.readAsDataURL(file);
}

async function analyzeImage() {
    if (!selectedFile) {
        alert('Please select an image first.');
        return;
    }
    
    console.log('[DETECT] Starting analysis for:', selectedFile.name);
    document.getElementById('loading').classList.remove('d-none');
    document.getElementById('preview-section').classList.add('d-none');
    document.getElementById('result-card').classList.add('d-none');

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
        console.log('[DETECT] Sending request to /api/detect');
        const res = await fetch('/api/detect', { 
            method: 'POST', 
            body: formData,
            credentials: 'same-origin'
        });
        
        console.log('[DETECT] Response status:', res.status, res.statusText);
        document.getElementById('loading').classList.add('d-none');
        
        if (res.status === 401) {
            alert('Please login first to detect diseases.');
            window.location.href = '/login';
            return;
        }
        
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            console.error('[DETECT] Server error:', res.status, errData);
            alert(errData.message || `Server error (${res.status}). Check console for details.`);
            document.getElementById('preview-section').classList.remove('d-none');
            return;
        }
        
        const data = await res.json();
        console.log('[DETECT] Response data:', data);

        if (!data.success) {
            console.error('[DETECT] Detection failed:', data.message);
            alert(data.message || 'Detection failed. Please try again.');
            document.getElementById('preview-section').classList.remove('d-none');
            return;
        }
        
        console.log('[DETECT] Success! Disease:', data.disease_name, 'Confidence:', data.confidence);
        renderResult(data);
    } catch (err) {
        console.error('[DETECT] Network error:', err);
        document.getElementById('loading').classList.add('d-none');
        document.getElementById('preview-section').classList.remove('d-none');
        alert(`Network error: ${err.message}\n\nMake sure:\n1. Flask server is running\n2. You are logged in\n3. Check browser console for details`);
    }
}

function renderResult(data) {
    window._lastResult = data; // expose for TTS
    stopSpeech?.();
    updateTTSBtn?.(false);
    const isHealthy = data.disease_name === 'Healthy Crop';
    document.getElementById('disease-badge').textContent = isHealthy ? '✅ Healthy' : '⚠️ Disease Detected';
    document.getElementById('disease-badge').className = `badge px-3 py-2 fs-6 fw-semibold ${isHealthy ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'}`;
    document.getElementById('result-disease').textContent = data.disease_name;
    document.getElementById('result-crop').textContent = data.crop_type ? `Crop: ${data.crop_type}` : '';
    document.getElementById('result-img').src = data.image_url;

    const conf = data.confidence;
    document.getElementById('confidence-text').textContent = `${conf}%`;
    const bar = document.getElementById('confidence-bar');
    bar.style.width = '0%';
    bar.className = `progress-bar ${conf >= 80 ? 'bg-success' : conf >= 60 ? 'bg-warning' : 'bg-danger'}`;
    setTimeout(() => bar.style.width = conf + '%', 100);

    document.getElementById('result-symptoms').textContent = data.symptoms || 'No symptoms data available.';
    document.getElementById('result-causes').textContent = data.causes || 'No cause data available.';
    document.getElementById('result-organic').textContent = data.organic_treatment || 'No organic treatment data.';
    document.getElementById('result-chemical').textContent = data.chemical_treatment || 'No chemical treatment data.';
    document.getElementById('result-preventive').textContent = data.preventive_measures || 'No preventive measures data.';

    document.getElementById('result-card').classList.remove('d-none');
    document.getElementById('result-card').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetUpload() {
    selectedFile = null;
    stopSpeech?.();
    updateTTSBtn?.(false);
    document.getElementById('image-input').value = '';
    document.getElementById('preview-section').classList.add('d-none');
    document.getElementById('result-card').classList.add('d-none');
    document.getElementById('loading').classList.add('d-none');
}

console.log('[DETECT] Module loaded successfully');
