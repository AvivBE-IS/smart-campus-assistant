const messagesDiv = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const staffBtn = document.getElementById('staffBtn');
const loginModal = document.getElementById('loginModal');
const loginBtn = document.getElementById('loginBtn');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

let staffCredentials = null;

function appendMessage(type, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    userInput.value = '';

    const body = { message };
    if (staffCredentials) {
        body.username = staffCredentials.username;
        body.password = staffCredentials.password;
    }

    try {
        const response = await fetch('http://localhost:8000/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await response.json();
        appendMessage('bot', data.response || 'Sorry, I couldn\'t process that.');
    } catch (error) {
        appendMessage('bot', 'Error connecting to server.');
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

staffBtn.addEventListener('click', () => {
    loginModal.style.display = 'flex';
});

loginBtn.addEventListener('click', () => {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    if (username && password) {
        staffCredentials = { username, password };
        loginModal.style.display = 'none';
        usernameInput.value = '';
        passwordInput.value = '';
        alert('Logged in as staff.');
    }
});

window.addEventListener('click', (e) => {
    if (e.target === loginModal) {
        loginModal.style.display = 'none';
    }
});