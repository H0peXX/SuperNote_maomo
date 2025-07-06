// DOM utilities
export function showElement(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (element) {
        element.classList.remove('hidden');
    }
}

export function hideElement(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (element) {
        element.classList.add('hidden');
    }
}

export function toggleElement(element, show) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (element) {
        element.classList.toggle('hidden', !show);
    }
}

// String utilities
export function escapeHtml(string) {
    const div = document.createElement('div');
    div.textContent = string;
    return div.innerHTML;
}

// Date formatting
export function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Toast notifications
export function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = document.createElement('div');
    icon.className = 'toast-icon';
    icon.innerHTML = getToastIcon(type);
    
    const content = document.createElement('div');
    content.className = 'toast-content';
    content.innerHTML = `
        <div class="toast-title">${getToastTitle(type)}</div>
        <div class="toast-message">${message}</div>
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.innerHTML = `
        <svg viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
    `;
    closeBtn.onclick = () => container.removeChild(toast);
    
    toast.appendChild(icon);
    toast.appendChild(content);
    toast.appendChild(closeBtn);
    container.appendChild(toast);
    
    // Add show class after a small delay for animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove after duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => container.removeChild(toast), 300);
    }, duration);
}

function getToastIcon(type) {
    switch (type) {
        case 'success':
            return `
                <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                </svg>
            `;
        case 'error':
            return `
                <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                </svg>
            `;
        case 'warning':
            return `
                <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                </svg>
            `;
        default:
            return `
                <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                </svg>
            `;
    }
}

function getToastTitle(type) {
    switch (type) {
        case 'success':
            return 'Success';
        case 'error':
            return 'Error';
        case 'warning':
            return 'Warning';
        default:
            return 'Info';
    }
}

// Modal dialogs
export function showModal({ title, content, onConfirm, onCancel, afterRender, showConfirmButton = true }) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">${title}</h3>
                <button class="modal-close">
                    <svg viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            ${showConfirmButton ? `
                <div class="modal-footer">
                    <button class="btn btn-secondary modal-cancel">Cancel</button>
                    <button class="btn btn-primary modal-confirm">Confirm</button>
                </div>
            ` : ''}
        </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 10);
    
    // Setup event listeners
    const closeModal = () => {
        modal.classList.remove('show');
        setTimeout(() => document.body.removeChild(modal), 300);
    };
    
    modal.querySelector('.modal-close').onclick = () => {
        if (onCancel) onCancel();
        closeModal();
    };
    
    if (showConfirmButton) {
        modal.querySelector('.modal-cancel').onclick = () => {
            if (onCancel) onCancel();
            closeModal();
        };
        
        modal.querySelector('.modal-confirm').onclick = async () => {
            if (onConfirm) {
                try {
                    await onConfirm();
                    closeModal();
                } catch (error) {
                    console.error('Modal confirmation error:', error);
                }
            } else {
                closeModal();
            }
        };
    }
    
    // Close on background click
    modal.onclick = (e) => {
        if (e.target === modal) {
            if (onCancel) onCancel();
            closeModal();
        }
    };

    // Run after render callback if provided
    if (afterRender) {
        afterRender();
    }
}

// User authentication utilities
export function getCurrentUserId() {
    const user = JSON.parse(localStorage.getItem('user'));
    return user ? user._id : null;
}

export function getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
}

export function setCurrentUser(user) {
    if (user) {
        localStorage.setItem('user', JSON.stringify(user));
    } else {
        localStorage.removeItem('user');
    }
}

// File handling utilities
export async function extractTextFromPDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/ai/process-pdf', {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to process PDF');
        }
        
        const result = await response.json();
        return result.text;
        
    } catch (error) {
        console.error('Error extracting text from PDF:', error);
        throw error;
    }
}

// AI utilities
export async function generateAIVersion(text, language = 'English') {
    try {
        const response = await fetch('/api/ai/enhance-note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ text, language })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate AI version');
        }
        
        return await response.json();
        
    } catch (error) {
        console.error('Error generating AI version:', error);
        throw error;
    }
}

export async function factCheckContent(text, language = 'English') {
    try {
        const response = await fetch('/api/ai/fact-check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ text, language })
        });
        
        if (!response.ok) {
            throw new Error('Failed to fact check content');
        }
        
        return await response.json();
        
    } catch (error) {
        console.error('Error fact checking content:', error);
        throw error;
    }
}
