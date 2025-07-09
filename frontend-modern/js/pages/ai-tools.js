// AI Tools page module
const AIToolsPage = {
    async init() {
        this.renderAITools();
        this.setupEventListeners();
    },

    async renderAITools() {
        const pageContent = document.getElementById('page-content');
        
        pageContent.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Upload PDF</h2>
                        <p class="card-subtitle">Upload a PDF (text or GoodNotes with handwriting)</p>
                    </div>
                    <div class="card-content">
                        <div class="pdf-upload-zone" id="pdf-upload-zone">
                            <input type="file" id="pdf-input" accept=".pdf" class="hidden" />
                            <div class="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 transition-colors">
                                <svg class="w-12 h-12 mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V7a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <p class="mb-2 text-sm text-gray-500">Click or drag and drop PDF file here</p>
                                <p class="text-xs text-gray-400">Supports text PDF and GoodNotes PDF with handwriting</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Text Preview</h2>
                        <p class="card-subtitle">Extracted text will appear here</p>
                    </div>
                    <div class="card-content">
                        <div id="text-preview" class="min-h-[200px] p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <p class="text-gray-400 text-center">No text extracted yet</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-6">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">AI Actions</h2>
                        <p class="card-subtitle">Choose what to do with the extracted text</p>
                    </div>
                    <div class="card-content">
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4" id="ai-actions">
                            <button class="btn btn-primary" disabled data-action="summarize">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6z" />
                                </svg>
                                Summarize
                            </button>
                            <button class="btn btn-primary" disabled data-action="fact-check">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                                </svg>
                                Fact Check
                            </button>
                            <button class="btn btn-primary" disabled data-action="quiz">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Generate Quiz
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div id="result-section" class="mt-6 hidden">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Results</h2>
                        <div class="flex gap-2">
                            <button id="save-result" class="btn btn-secondary">
                                Save as Note
                            </button>
                            <button id="copy-result" class="btn btn-secondary">
                                Copy to Clipboard
                            </button>
                        </div>
                    </div>
                    <div class="card-content">
                        <div id="result-content" class="prose dark:prose-invert max-w-none">
                            <!-- Results will be inserted here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        const uploadZone = document.getElementById('pdf-upload-zone');
        const pdfInput = document.getElementById('pdf-input');
        const aiActions = document.getElementById('ai-actions');
        const saveResult = document.getElementById('save-result');
        const copyResult = document.getElementById('copy-result');

        // PDF Upload
        uploadZone.addEventListener('click', () => pdfInput.click());
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('border-primary-500');
        });
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('border-primary-500');
        });
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('border-primary-500');
            
            const file = e.dataTransfer.files[0];
            if (file && file.type === 'application/pdf') {
                this.handlePDFUpload(file);
            } else {
                showToast('Please upload a PDF file', 'error');
            }
        });

        pdfInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handlePDFUpload(file);
            }
        });

        // AI Actions
        aiActions.addEventListener('click', (e) => {
            const button = e.target.closest('button[data-action]');
            if (button && !button.disabled) {
                const action = button.dataset.action;
                this.processText(action);
            }
        });

        // Result Actions
        saveResult.addEventListener('click', () => this.saveAsNote());
        copyResult.addEventListener('click', () => this.copyToClipboard());
    },

    async handlePDFUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            showToast('Processing PDF...', 'info');

            const response = await fetch('/api/ai/process-pdf', {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to process PDF');

            const result = await response.json();
            this.displayExtractedText(result.text);
            this.enableAIActions();
            
            showToast('PDF processed successfully', 'success');

        } catch (error) {
            console.error('Error processing PDF:', error);
            showToast('Error processing PDF', 'error');
        }
    },

    displayExtractedText(text) {
        const preview = document.getElementById('text-preview');
        preview.innerHTML = `<pre class="whitespace-pre-wrap">${escapeHtml(text)}</pre>`;
        this.extractedText = text;
    },

    enableAIActions() {
        const buttons = document.querySelectorAll('#ai-actions button');
        buttons.forEach(button => button.disabled = false);
    },

    async processText(action) {
        if (!this.extractedText) return;

        const resultSection = document.getElementById('result-section');
        const resultContent = document.getElementById('result-content');
        
        try {
            showToast(`Running ${action}...`, 'info');

            const response = await fetch(`/api/ai/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    text: this.extractedText,
                    language: 'English'
                })
            });

            if (!response.ok) throw new Error(`Failed to ${action}`);

            const result = await response.json();
            
            // Display results based on action type
            switch (action) {
                case 'summarize':
                    resultContent.innerHTML = this.formatSummary(result);
                    break;
                case 'fact-check':
                    resultContent.innerHTML = this.formatFactCheck(result);
                    break;
                case 'quiz':
                    resultContent.innerHTML = this.formatQuiz(result);
                    break;
            }

            resultSection.classList.remove('hidden');
            showToast(`${action} completed`, 'success');

        } catch (error) {
            console.error(`Error during ${action}:`, error);
            showToast(`Error during ${action}`, 'error');
        }
    },

    formatSummary(result) {
        return `
            <h3>Summary</h3>
            <div class="mt-4">
                ${result.result.split('\n').map(line => `<p>${escapeHtml(line)}</p>`).join('')}
            </div>
        `;
    },

    formatFactCheck(result) {
        return `
            <h3>Fact Check Results</h3>
            <div class="mt-4 space-y-4">
                ${result.fact_checks.map(check => `
                    <div class="fact-check ${check.status.toLowerCase()}">
                        <div class="fact-check-header">
                            <span class="fact-check-status">${check.status}</span>
                            <span class="fact-check-confidence">${Math.round(check.confidence * 100)}% confidence</span>
                        </div>
                        <div class="fact-check-claim">${escapeHtml(check.claim)}</div>
                        <div class="fact-check-explanation">${escapeHtml(check.explanation)}</div>
                        ${check.sources.length ? `
                            <div class="fact-check-sources">
                                Sources:
                                <ul>
                                    ${check.sources.map(source => `<li>${escapeHtml(source)}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    },

    formatQuiz(result) {
        return `
            <h3>Generated Quiz</h3>
            <div class="mt-4 space-y-6">
                ${result.questions.map((q, i) => `
                    <div class="quiz-question">
                        <p class="font-semibold">${i + 1}. ${escapeHtml(q.question)}</p>
                        <div class="mt-2 space-y-2">
                            ${q.options.map(option => `
                                <div class="flex items-center">
                                    <input type="radio" name="q${i}" value="${option.charAt(0)}" 
                                        ${option.charAt(0) === q.correct_answer ? 'data-correct="true"' : ''}>
                                    <label class="ml-2">${escapeHtml(option)}</label>
                                </div>
                            `).join('')}
                        </div>
                        <div class="mt-2 hidden text-success" data-explanation>
                            ${escapeHtml(q.explanation || `Correct answer: ${q.correct_answer}`)}
                        </div>
                    </div>
                `).join('')}
                <button class="btn btn-primary mt-4" onclick="this.closest('.quiz-question').querySelectorAll('[data-explanation]').forEach(e => e.classList.remove('hidden'))">
                    Show Answers
                </button>
            </div>
        `;
    },

    async saveAsNote() {
        const resultContent = document.getElementById('result-content');
        if (!resultContent.innerHTML) return;

        try {
            const response = await fetch('/api/notes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    title: 'AI Generated Content',
                    content: resultContent.innerHTML,
                    topic_id: 'default' // You might want to let users select a topic
                })
            });

            if (!response.ok) throw new Error('Failed to save note');

            showToast('Saved as new note', 'success');
            window.location.hash = '#notes';

        } catch (error) {
            console.error('Error saving note:', error);
            showToast('Error saving note', 'error');
        }
    },

    copyToClipboard() {
        const resultContent = document.getElementById('result-content');
        if (!resultContent.innerHTML) return;

        const textToCopy = resultContent.innerText;
        
        navigator.clipboard.writeText(textToCopy)
            .then(() => showToast('Copied to clipboard', 'success'))
            .catch(() => showToast('Failed to copy to clipboard', 'error'));
    }
};

export default AIToolsPage;
