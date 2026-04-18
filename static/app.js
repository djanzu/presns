const chatContainer = document.getElementById('chat-container');
const postInput = document.getElementById('post-input');
const sendBtn = document.getElementById('send-btn');

function appendMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading';
    loadingDiv.id = 'loading-msg';
    loadingDiv.innerHTML = `
        <div class="dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeLoading() {
    const loadingDiv = document.getElementById('loading-msg');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

async function handleSend() {
    const text = postInput.value.trim();
    if (!text) return;

    // Disable input
    postInput.value = '';
    postInput.disabled = true;
    sendBtn.disabled = true;

    // Show user message
    appendMessage('user', text);

    // Show loading
    showLoading();

    try {
        const response = await fetch('/evaluate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        removeLoading();

        if (response.ok) {
            appendMessage('assistant', data.evaluation);
        } else {
            appendMessage('assistant', `エラーが発生しました: ${data.detail || 'Unknown error'}`);
        }
    } catch (error) {
        removeLoading();
        appendMessage('assistant', `通信エラーが発生しました: ${error.message}`);
    } finally {
        postInput.disabled = false;
        sendBtn.disabled = false;
        postInput.focus();
    }
}

sendBtn.addEventListener('click', handleSend);

postInput.addEventListener('keydown', (e) => {
    if (e.isComposing || e.keyCode === 229) return;
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});
