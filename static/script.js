// YouTube Transcript App - Client-side JavaScript

const API_BASE_URL = window.location.origin;

// DOM Elements
const form = document.getElementById('transcript-form');
const urlInput = document.getElementById('youtube-url');
const languageSelect = document.getElementById('language');
const timestampCheckbox = document.getElementById('include-timestamps');
const submitBtn = document.getElementById('submit-btn');
const resultSection = document.getElementById('result-section');
const transcriptBox = document.getElementById('transcript-box');
const alertContainer = document.getElementById('alert-container');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');

let currentVideoId = null;

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const url = urlInput.value.trim();

    if (!url) {
        showAlert('error', 'URL obrigatória', 'Por favor, insira uma URL do YouTube.');
        return;
    }

    await fetchTranscript(url);
});

// Fetch transcript from API
async function fetchTranscript(url) {
    try {
        // Update UI to loading state
        setLoadingState(true);
        hideAlert();
        hideResult();

        const languages = languageSelect.value ? [languageSelect.value] : null;
        const includeTimestamps = timestampCheckbox.checked;

        const response = await fetch(`${API_BASE_URL}/api/transcript`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                languages: languages,
                include_timestamps: includeTimestamps
            })
        });

        const data = await response.json();

        if (data.success) {
            // Success - display transcript
            currentVideoId = data.video_id;
            displayTranscript(data);

            if (data.cached) {
                showAlert('info', 'Resultado em cache', 'Esta transcrição foi carregada do cache para resposta mais rápida.');
            } else {
                showAlert('success', 'Sucesso!', `Transcrição obtida em ${data.language.toUpperCase()} com ${data.total_segments} segmentos.`);
            }
        } else {
            // Error from API
            showAlert('error', data.error || 'Erro', data.message || 'Ocorreu um erro ao processar o vídeo.');
        }

    } catch (error) {
        console.error('Error fetching transcript:', error);
        showAlert('error', 'Erro de conexão', 'Não foi possível conectar ao servidor. Verifique sua conexão.');
    } finally {
        setLoadingState(false);
    }
}

// Display transcript in result section
function displayTranscript(data) {
    transcriptBox.textContent = data.transcript;
    resultSection.classList.remove('hidden');

    // Smooth scroll to result
    setTimeout(() => {
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Copy transcript to clipboard
copyBtn.addEventListener('click', async () => {
    const text = transcriptBox.textContent;

    try {
        await navigator.clipboard.writeText(text);
        showTemporaryFeedback(copyBtn, '✓ Copiado!');
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showTemporaryFeedback(copyBtn, '✓ Copiado!');
    }
});

// Download transcript as text file
downloadBtn.addEventListener('click', () => {
    const text = transcriptBox.textContent;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${currentVideoId || 'youtube'}_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showTemporaryFeedback(downloadBtn, '✓ Baixado!');
});

// Show temporary feedback on button
function showTemporaryFeedback(button, message) {
    const originalText = button.textContent;
    button.textContent = message;
    button.style.background = 'var(--success)';

    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '';
    }, 2000);
}

// Set loading state
function setLoadingState(isLoading) {
    if (isLoading) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Processando...';
    } else {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Obter Transcrição';
    }
}

// Show alert message
function showAlert(type, title, message) {
    const alertClass = `alert-${type}`;
    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            <strong>${title}</strong>
            ${message}
        </div>
    `;
    alertContainer.classList.remove('hidden');
}

// Hide alert
function hideAlert() {
    alertContainer.classList.add('hidden');
    alertContainer.innerHTML = '';
}

// Hide result section
function hideResult() {
    resultSection.classList.add('hidden');
}

// Auto-focus URL input on page load
window.addEventListener('load', () => {
    urlInput.focus();
});

// Clear error when user starts typing
urlInput.addEventListener('input', () => {
    if (alertContainer.querySelector('.alert-error')) {
        hideAlert();
    }
});

// Handle paste event - auto-submit if it looks like a YouTube URL
urlInput.addEventListener('paste', (e) => {
    setTimeout(() => {
        const pastedText = urlInput.value;
        if (pastedText.includes('youtube.com') || pastedText.includes('youtu.be')) {
            // Auto-focus submit button for easy Enter press
            submitBtn.focus();
        }
    }, 10);
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        urlInput.focus();
        urlInput.select();
    }

    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (!submitBtn.disabled) {
            form.dispatchEvent(new Event('submit'));
        }
    }
});
