// Notes page functionality
class NotesPage {
    constructor() {
        this.notes = [];
        this.currentNote = null;
        this.currentTopicId = null;
    }

    async init() {
        await this.loadNotes();
        this.setupEventListeners();
    }

    async loadNotes() {
        if (!this.currentTopicId) return;

        try {
            const response = await api.get(`/api/notes/?topic_id=${this.currentTopicId}`);
            if (response.ok) {
                this.notes = await response.json();
                this.renderNotes();
            }
        } catch (error) {
            showToast('Error loading notes', 'error');
        }
    }

    renderNotes() {
        const container = document.getElementById('notes-list');
        if (!container) return;

        container.innerHTML = this.notes.map(note => `
            <div class="note-card" data-note-id="${note._id}">
                <div class="note-header">
                    <h3 class="note-title">${escapeHtml(note.title)}</h3>
                    <span class="note-status ${note.status.toLowerCase()}">${note.status}</span>
                </div>
                <div class="note-preview">${this.truncateContent(note.content)}</div>
                <div class="note-meta">
                    <span class="comments-count">
                        <i class="far fa-comment"></i> ${note.comments.length} comments
                    </span>
                    <span class="fact-checks-count">
                        <i class="far fa-check-circle"></i> ${note.fact_checks.length} fact checks
                    </span>
                </div>
                <div class="note-actions">
                    <button class="btn btn-primary edit-note-btn" data-note-id="${note._id}">
                        Edit
                    </button>
                    <button class="btn btn-secondary ai-enhance-btn" data-note-id="${note._id}">
                        AI Enhance
                    </button>
                    ${this.isNoteOwner(note) ? `
                        <button class="btn btn-danger delete-note-btn" data-note-id="${note._id}">
                            Delete
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    truncateContent(content, maxLength = 200) {
        if (content.length <= maxLength) return escapeHtml(content);
        return escapeHtml(content.substring(0, maxLength)) + '...';
    }

    isNoteOwner(note) {
        const currentUserId = getCurrentUserId();
        return note.created_by === currentUserId;
    }

    setupEventListeners() {
        document.addEventListener('click', async (e) => {
            if (e.target.matches('.edit-note-btn')) {
                const noteId = e.target.dataset.noteId;
                await this.showNoteEditor(noteId);
            } else if (e.target.matches('.ai-enhance-btn')) {
                const noteId = e.target.dataset.noteId;
                await this.showAIEnhanceOptions(noteId);
            } else if (e.target.matches('.delete-note-btn')) {
                const noteId = e.target.dataset.noteId;
                await this.deleteNote(noteId);
            }
        });

        // New note button
        const newNoteBtn = document.getElementById('new-note-btn');
        if (newNoteBtn) {
            newNoteBtn.addEventListener('click', () => this.showNoteEditor());
        }
    }

    async showNoteEditor(noteId = null) {
        const isEditing = !!noteId;
        let note = null;

        if (isEditing) {
            note = this.notes.find(n => n._id === noteId);
            if (!note) return;
        }

        const editor = document.createElement('div');
        editor.className = 'note-editor';
        editor.innerHTML = `
            <div class="editor-header">
                <input type="text" id="note-title" class="title-input" 
                    value="${isEditing ? escapeHtml(note.title) : ''}" 
                    placeholder="Note Title" required>
                
                <div class="editor-actions">
                    <button id="save-note" class="btn btn-primary">Save</button>
                    <button id="cancel-edit" class="btn btn-secondary">Cancel</button>
                </div>
            </div>
            
            <div class="editor-main">
                <div class="editor-content">
                    <textarea id="note-content" class="content-input" 
                        placeholder="Write your note here...">${isEditing ? escapeHtml(note.content) : ''}</textarea>
                </div>
                
                <div class="editor-sidebar">
                    <div class="comments-section">
                        <h3>Comments</h3>
                        <div id="comments-list" class="comments-list">
                            ${isEditing ? this.renderComments(note.comments) : ''}
                        </div>
                        <div class="add-comment">
                            <textarea id="new-comment" placeholder="Add a comment..."></textarea>
                            <button id="post-comment" class="btn btn-primary">Post</button>
                        </div>
                    </div>
                    
                    <div class="fact-checks-section">
                        <h3>Fact Checks</h3>
                        <div id="fact-checks-list" class="fact-checks-list">
                            ${isEditing ? this.renderFactChecks(note.fact_checks) : ''}
                        </div>
                        <button id="run-fact-check" class="btn btn-secondary">
                            Run Fact Check
                        </button>
                    </div>
                </div>
            </div>
        `;

        const mainContent = document.querySelector('.main-content');
        mainContent.innerHTML = '';
        mainContent.appendChild(editor);

        // Setup editor event listeners
        this.setupEditorEventListeners(noteId);
    }

    renderComments(comments) {
        return comments.map(comment => `
            <div class="comment">
                <div class="comment-header">
                    <span class="comment-author">${escapeHtml(comment.user_name)}</span>
                    <span class="comment-date">${formatDate(comment.created_at)}</span>
                </div>
                <div class="comment-content">${escapeHtml(comment.content)}</div>
            </div>
        `).join('');
    }

    renderFactChecks(factChecks) {
        return factChecks.map(check => `
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
                            ${check.sources.map(source => `
                                <li>${escapeHtml(source)}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    setupEditorEventListeners(noteId) {
        const saveBtn = document.getElementById('save-note');
        const cancelBtn = document.getElementById('cancel-edit');
        const postCommentBtn = document.getElementById('post-comment');
        const runFactCheckBtn = document.getElementById('run-fact-check');

        saveBtn.addEventListener('click', () => this.saveNote(noteId));
        cancelBtn.addEventListener('click', () => this.loadNotes());
        
        if (noteId) {
            postCommentBtn.addEventListener('click', () => this.postComment(noteId));
            runFactCheckBtn.addEventListener('click', () => this.runFactCheck(noteId));
        }
    }

    async saveNote(noteId = null) {
        const title = document.getElementById('note-title').value;
        const content = document.getElementById('note-content').value;

        if (!title || !content) {
            showToast('Title and content are required', 'error');
            return;
        }

        try {
            if (noteId) {
                await api.put(`/api/notes/${noteId}`, {
                    title,
                    content
                });
                showToast('Note updated successfully', 'success');
            } else {
                await api.post('/api/notes/', {
                    title,
                    content,
                    topic_id: this.currentTopicId
                });
                showToast('Note created successfully', 'success');
            }

            await this.loadNotes();
        } catch (error) {
            showToast('Error saving note', 'error');
        }
    }

    async postComment(noteId) {
        const content = document.getElementById('new-comment').value;
        if (!content) return;

        try {
            const response = await api.post(`/api/notes/${noteId}/comments`, {
                content
            });

            if (response.ok) {
                const comment = await response.json();
                const commentsList = document.getElementById('comments-list');
                commentsList.innerHTML += this.renderComments([comment]);
                document.getElementById('new-comment').value = '';
            }
        } catch (error) {
            showToast('Error posting comment', 'error');
        }
    }

    async runFactCheck(noteId) {
        try {
            const response = await api.post(`/api/notes/${noteId}/fact-checks`);
            if (response.ok) {
                const result = await response.json();
                const factChecksList = document.getElementById('fact-checks-list');
                factChecksList.innerHTML = this.renderFactChecks(result.fact_checks);
                showToast('Fact check completed', 'success');
            }
        } catch (error) {
            showToast('Error running fact check', 'error');
        }
    }

    async showAIEnhanceOptions(noteId) {
        const note = this.notes.find(n => n._id === noteId);
        if (!note) return;

        showModal({
            title: 'AI Enhancement Options',
            content: `
                <div class="ai-enhance-options">
                    <button id="ai-new-version" class="btn btn-primary mb-2 w-full">
                        Create New AI-Enhanced Version
                    </button>
                    <button id="ai-replace" class="btn btn-secondary w-full">
                        Replace with AI-Enhanced Version
                    </button>
                    <p class="text-sm text-gray-500 mt-4">
                        Choose whether to create a new version with AI enhancements
                        or replace the current content with an AI-enhanced version.
                    </p>
                </div>
            `,
            onConfirm: async () => {
                // This will be handled by the specific buttons
            },
            showConfirmButton: false
        });

        // Setup AI enhancement buttons
        document.getElementById('ai-new-version').addEventListener('click', () => {
            this.performAIEnhancement(noteId, false);
        });

        document.getElementById('ai-replace').addEventListener('click', () => {
            this.performAIEnhancement(noteId, true);
        });
    }

    async performAIEnhancement(noteId, replace = false) {
        const note = this.notes.find(n => n._id === noteId);
        if (!note) return;

        try {
            showToast('AI enhancement in progress...', 'info');

            const response = await api.post('/api/ai/enhance-note', {
                text: note.content,
                language: 'English'
            });

            if (response.ok) {
                const result = await response.json();
                
                if (replace) {
                    // Replace current content
                    await api.put(`/api/notes/${noteId}`, {
                        content: result.result
                    });
                    showToast('Note content replaced with AI enhancement', 'success');
                } else {
                    // Create new version
                    await api.post(`/api/notes/${noteId}/versions`, {
                        content: result.result,
                        changes_summary: 'AI-enhanced version'
                    });
                    showToast('New AI-enhanced version created', 'success');
                }

                await this.loadNotes();
            }
        } catch (error) {
            showToast('Error during AI enhancement', 'error');
        }
    }

    async deleteNote(noteId) {
        if (!confirm('Are you sure you want to delete this note? This action cannot be undone.')) {
            return;
        }

        try {
            await api.delete(`/api/notes/${noteId}`);
            showToast('Note deleted successfully', 'success');
            await this.loadNotes();
        } catch (error) {
            showToast('Error deleting note', 'error');
        }
    }
}

// Initialize Notes page
const notesPage = new NotesPage();
window.addEventListener('load', () => notesPage.init());
