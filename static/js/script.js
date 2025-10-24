// login.html
setTimeout(() => {
    const msg = document.getElementById('login-message');
    if (msg) {
        msg.style.transition = "opacity 0.5s";
        msg.style.opacity = 0;
        setTimeout(() => msg.remove(), 500);
    }
}, 3000);


// signup
// Hide the message after 3 seconds
setTimeout(() => {
    const msg = document.getElementById('signup-message');
    if (msg) {
        msg.style.transition = "opacity 0.5s";
        msg.style.opacity = 0;
        setTimeout(() => msg.remove(), 500);
    }
}, 2000);

// dashboard sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('show');
}

//  chat.html
// Auto scroll
const chatBox = document.getElementById('chatBox');
chatBox.scrollTop = chatBox.scrollHeight;

// Auto focus
document.getElementById('userInput').focus();

// Typing effect
document.querySelectorAll('.typing').forEach(el => {
    const text = el.dataset.text;
    let i = 0;
    el.textContent = '';
    const interval = setInterval(() => {
        if (i < text.length) {
            el.textContent += text[i];
            i++;
            chatBox.scrollTop = chatBox.scrollHeight;
        } else {
            clearInterval(interval);
        }
    }, 15);
});

