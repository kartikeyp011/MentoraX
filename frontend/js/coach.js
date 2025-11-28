let messageCount = 0;

// Load on page load
document.addEventListener('DOMContentLoaded', async () => {
    const isValid = await verifySession();
    if (!isValid) return;
});

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Clear input
    input.value = '';

    // Add user message to chat
    addUserMessage(message);

    // Show typing indicator
    const typingId = showTypingIndicator();

    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Thinking...';

    try {
        const token = localStorage.getItem('session_token');
        const response = await fetch(`${API_BASE_URL}/coach/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (data.success) {
            addAIMessage(data.response, data.suggestions || []);
        } else {
            addAIMessage("I apologize, but I encountered an error. Please try again.", []);
        }
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingId);
        addAIMessage("I'm having trouble connecting. Please check your internet and try again.", []);
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
    }
}

function addUserMessage(message) {
    const chatMessages = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3 justify-end';

    messageDiv.innerHTML = `
        <div class="bg-blue-600 text-white rounded-lg p-4 max-w-2xl">
            <p>${escapeHtml(message)}</p>
        </div>
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold">
            You
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addAIMessage(message, suggestions = []) {
    const chatMessages = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3';

    messageDiv.innerHTML = `
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">
            AI
        </div>
        <div class="flex-1 bg-blue-50 rounded-lg p-4 max-w-2xl">
            <p class="text-gray-900 whitespace-pre-wrap">${escapeHtml(message)}</p>
        </div>
    `;

    chatMessages.appendChild(messageDiv);

    // Show suggestions
    if (suggestions.length > 0) {
        showSuggestions(suggestions);
    } else {
        hideSuggestions();
    }

    scrollToBottom();
}

function showSuggestions(suggestions) {
    const suggestionsDiv = document.getElementById('suggestions');
    suggestionsDiv.innerHTML = '<p class="text-sm text-gray-600 w-full mb-2">💡 You might also ask:</p>';

    suggestions.forEach(suggestion => {
        const chip = document.createElement('button');
        chip.className = 'px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full hover:bg-gray-200 transition';
        chip.textContent = suggestion;
        chip.onclick = () => quickPrompt(suggestion);
        suggestionsDiv.appendChild(chip);
    });

    suggestionsDiv.classList.remove('hidden');
}

function hideSuggestions() {
    document.getElementById('suggestions').classList.add('hidden');
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');

    const typingDiv = document.createElement('div');
    typingDiv.className = 'flex items-start space-x-3';
    typingDiv.id = `typing_${messageCount++}`;

    typingDiv.innerHTML = `
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">
            AI
        </div>
        <div class="bg-blue-50 rounded-lg p-4">
            <div class="flex space-x-2">
                <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
        </div>
    `;

    chatMessages.appendChild(typingDiv);
    scrollToBottom();

    return typingDiv.id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

async function getLearningPlan() {
    addUserMessage("Can you create a personalized learning plan for me?");

    const typingId = showTypingIndicator();

    try {
        const token = localStorage.getItem('session_token');
        const response = await fetch(`${API_BASE_URL}/coach/plan`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        removeTypingIndicator(typingId);

        if (data.success) {
            const plan = data.plan;

            let message = `Here's your personalized learning plan:\n\n`;
            message += `📚 Current Skills: ${plan.current_skills.join(', ') || 'None yet'}\n\n`;
            message += `🎯 Recommended Skills to Learn:\n`;
            plan.recommended_skills.forEach(skill => {
                message += `  • ${skill}\n`;
            });
            message += `\n📖 Top Learning Resources:\n`;
            plan.learning_resources.forEach((resource, i) => {
                message += `  ${i + 1}. ${resource.title}\n`;
            });
            message += `\n✅ Next Steps:\n`;
            plan.next_steps.forEach((step, i) => {
                message += `  ${i + 1}. ${step}\n`;
            });

            addAIMessage(message, [
                "Tell me more about these resources",
                "How long will this take?",
                "What should I start with first?"
            ]);
        }
    } catch (error) {
        console.error('Learning plan error:', error);
        removeTypingIndicator(typingId);
        addAIMessage("Error generating learning plan. Please try again.", []);
    }
}

function quickPrompt(text) {
    document.getElementById('chatInput').value = text;
    sendMessage();
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}