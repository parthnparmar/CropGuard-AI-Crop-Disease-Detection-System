/**
 * CropGuard AI — Multilingual Voice Translation
 * - Google Translate widget for page-wide translation
 * - Web Speech API: Speech-to-Text (STT) + Text-to-Speech (TTS)
 */

const LANGUAGES = [
  { code: 'en', name: 'English',    voice: 'en-IN' },
  { code: 'hi', name: 'हिंदी',      voice: 'hi-IN' },
  { code: 'gu', name: 'ગુજરાતી',    voice: 'gu-IN' },
  { code: 'mr', name: 'मराठी',      voice: 'mr-IN' },
  { code: 'ta', name: 'தமிழ்',      voice: 'ta-IN' },
  { code: 'te', name: 'తెలుగు',     voice: 'te-IN' },
  { code: 'bn', name: 'বাংলা',      voice: 'bn-IN' },
  { code: 'pa', name: 'ਪੰਜਾਬੀ',     voice: 'pa-IN' },
  { code: 'kn', name: 'ಕನ್ನಡ',      voice: 'kn-IN' },
  { code: 'ml', name: 'മലയാളം',     voice: 'ml-IN' },
  { code: 'ur', name: 'اردو',       voice: 'ur-IN' },
];

// Always reset to English on every page load — clear Google Translate cookie.
let currentLang = 'en';
localStorage.setItem('cg_lang', 'en');

// Clear the googtrans cookie that Google Translate sets to remember language
function clearGoogTransCookie() {
  const domains = [location.hostname, '.' + location.hostname, ''];
  domains.forEach(d => {
    document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${d}`;
  });
}
clearGoogTransCookie();
let ttsUtterance = null;
let isSpeaking = false;
let recognition = null;

/* ─── Google Translate ─────────────────────────────────────────── */
function googleTranslateInit() {
  new google.translate.TranslateElement(
    { pageLanguage: 'en', includedLanguages: LANGUAGES.map(l => l.code).join(','), autoDisplay: false },
    'google_translate_element'
  );
}

function setLanguage(code) {
  currentLang = code;
  localStorage.setItem('cg_lang', code);

  // Update selector UI
  document.querySelectorAll('.lang-option').forEach(el => {
    el.classList.toggle('active', el.dataset.code === code);
  });
  const selected = LANGUAGES.find(l => l.code === code);
  const btn = document.getElementById('langDropdownBtn');
  if (btn && selected) btn.innerHTML = `<i class="fas fa-globe me-1"></i>${selected.name}`;

  // Trigger Google Translate via combo select
  const combo = document.querySelector('select.goog-te-combo');
  if (!combo) return;
  if (code === 'en') {
    clearGoogTransCookie();
    combo.value = '';
  } else {
    combo.value = code;
  }
  combo.dispatchEvent(new Event('change'));
}

/* ─── Text-to-Speech ───────────────────────────────────────────── */
function speakText(text, onEnd) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const lang = LANGUAGES.find(l => l.code === currentLang) || LANGUAGES[0];
  ttsUtterance = new SpeechSynthesisUtterance(text);
  ttsUtterance.lang = lang.voice;
  ttsUtterance.rate = 0.92;
  ttsUtterance.pitch = 1;
  isSpeaking = true;
  ttsUtterance.onend = () => { isSpeaking = false; if (onEnd) onEnd(); };
  ttsUtterance.onerror = () => { isSpeaking = false; if (onEnd) onEnd(); };
  window.speechSynthesis.speak(ttsUtterance);
}

function stopSpeech() {
  window.speechSynthesis?.cancel();
  isSpeaking = false;
}

// Build a summary string from result data and speak it
function speakResult(data) {
  const btn = document.getElementById('tts-btn');
  if (isSpeaking) { stopSpeech(); updateTTSBtn(false); return; }

  const lines = [
    `Disease detected: ${data.disease_name}.`,
    data.crop_type ? `Crop type: ${data.crop_type}.` : '',
    `Confidence: ${data.confidence} percent.`,
    data.symptoms   ? `Symptoms: ${data.symptoms}.` : '',
    data.causes     ? `Causes: ${data.causes}.` : '',
    data.organic_treatment  ? `Organic treatment: ${data.organic_treatment}.` : '',
    data.chemical_treatment ? `Chemical treatment: ${data.chemical_treatment}.` : '',
    data.preventive_measures? `Preventive measures: ${data.preventive_measures}.` : '',
  ];
  updateTTSBtn(true);
  speakText(lines.filter(Boolean).join(' '), () => updateTTSBtn(false));
}

function updateTTSBtn(speaking) {
  const btn = document.getElementById('tts-btn');
  if (!btn) return;
  btn.innerHTML = speaking
    ? '<i class="fas fa-stop-circle me-2"></i>Stop Reading'
    : '<i class="fas fa-volume-up me-2"></i>Read Aloud';
  btn.classList.toggle('btn-danger', speaking);
  btn.classList.toggle('btn-outline-primary', !speaking);
}

/* ─── Speech-to-Text ───────────────────────────────────────────── */
function initSTT(inputEl, micBtn) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    micBtn.title = 'Speech recognition not supported in this browser';
    micBtn.disabled = true;
    return;
  }
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    micBtn.classList.add('recording');
    micBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
    micBtn.title = 'Listening… click to stop';
  };
  recognition.onresult = e => {
    inputEl.value = e.results[0][0].transcript;
    inputEl.dispatchEvent(new Event('input'));
  };
  recognition.onend = () => {
    micBtn.classList.remove('recording');
    micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    micBtn.title = 'Speak your query';
  };
  recognition.onerror = () => recognition.onend();

  micBtn.addEventListener('click', () => {
    const lang = LANGUAGES.find(l => l.code === currentLang) || LANGUAGES[0];
    recognition.lang = lang.voice;
    micBtn.classList.contains('recording') ? recognition.stop() : recognition.start();
  });
}

/* ─── Language Selector UI ─────────────────────────────────────── */
function buildLangSelector() {
  const wrapper = document.getElementById('lang-selector-wrapper');
  if (!wrapper) return;

  const current = LANGUAGES.find(l => l.code === currentLang) || LANGUAGES[0];
  wrapper.innerHTML = `
    <div class="dropdown">
      <button id="langDropdownBtn" class="btn btn-outline-light btn-sm dropdown-toggle lang-btn" data-bs-toggle="dropdown">
        <i class="fas fa-globe me-1"></i>${current.name}
      </button>
      <ul class="dropdown-menu dropdown-menu-end lang-dropdown">
        ${LANGUAGES.map(l => `
          <li>
            <button class="dropdown-item lang-option ${l.code === currentLang ? 'active' : ''}"
                    data-code="${l.code}" onclick="setLanguage('${l.code}')">
              ${l.name}
            </button>
          </li>`).join('')}
      </ul>
    </div>
    <div id="google_translate_element" class="d-none"></div>
  `;
}

/* ─── Auto-init on DOM ready ───────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  buildLangSelector();

  // Hook mic button in chatbot if present
  const chatInput = document.getElementById('chat-input');
  const chatMic   = document.getElementById('chat-mic-btn');
  if (chatInput && chatMic) initSTT(chatInput, chatMic);
});
