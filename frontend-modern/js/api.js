/**
 * API Client for handling all server requests
 */
class APIClient {
    constructor() {
        this.baseUrl = window.location.origin;
        this.headers = {
            'Content-Type': 'application/json'
        };
    }

    setToken(token) {
        if (token) {
            this.headers['Authorization'] = `Bearer ${token}`;
            localStorage.setItem('token', token);
        } else {
            delete this.headers['Authorization'];
            localStorage.removeItem('token');
        }
    }

    async request(method, endpoint, data = null, formData = false) {
        try {
            const url = this.baseUrl + endpoint;
            const options = {
                method,
                headers: { ...this.headers },
                credentials: 'include'
            };

            if (data) {
                if (formData) {
                    delete options.headers['Content-Type'];
                    options.body = data;
                } else {
                    options.body = JSON.stringify(data);
                }
            }

            const response = await fetch(url, options);

            // Handle authentication errors
            if (response.status === 401) {
                this.setToken(null);
                throw new Error('Authentication failed');
            }

            // Parse response
            let result;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                result = await response.json();
            } else {
                result = await response.text();
            }

            // Handle non-200 responses
            if (!response.ok) {
                throw new Error(result.message || result.detail || 'Request failed');
            }

            return result;

        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Teams endpoints
    async getTeams() {
        return this.request('GET', '/api/teams/');
    }

    async createTeam(data) {
        return this.request('POST', '/api/teams/', data);
    }

    async getTeam(teamId) {
        return this.request('GET', `/api/teams/${teamId}`);
    }

    async updateTeam(teamId, data) {
        return this.request('PUT', `/api/teams/${teamId}`, data);
    }

    async deleteTeam(teamId) {
        return this.request('DELETE', `/api/teams/${teamId}`);
    }

    async inviteTeamMember(teamId, data) {
        return this.request('POST', `/api/teams/${teamId}/invite`, data);
    }

    async removeTeamMember(teamId, userId) {
        return this.request('DELETE', `/api/teams/${teamId}/members/${userId}`);
    }

    async updateTeamMemberRole(teamId, userId, role) {
        return this.request('PUT', `/api/teams/${teamId}/members/${userId}/role`, { role });
    }

    // Notes endpoints
    async getNotes(topicId) {
        return this.request('GET', `/api/notes/?topic_id=${topicId}`);
    }

    async createNote(data) {
        return this.request('POST', '/api/notes/', data);
    }

    async getNote(noteId) {
        return this.request('GET', `/api/notes/${noteId}`);
    }

    async updateNote(noteId, data) {
        return this.request('PUT', `/api/notes/${noteId}`, data);
    }

    async deleteNote(noteId) {
        return this.request('DELETE', `/api/notes/${noteId}`);
    }

    async addComment(noteId, content) {
        return this.request('POST', `/api/notes/${noteId}/comments`, { content });
    }

    async getComments(noteId) {
        return this.request('GET', `/api/notes/${noteId}/comments`);
    }

    async factCheckNote(noteId) {
        return this.request('POST', `/api/notes/${noteId}/fact-checks`);
    }

    async createNoteVersion(noteId, data) {
        return this.request('POST', `/api/notes/${noteId}/versions`, data);
    }

    // AI Tools endpoints
    async processPDF(file) {
        const formData = new FormData();
        formData.append('file', file);
        return this.request('POST', '/api/ai/process-pdf', formData, true);
    }

    async summarizeText(text, language = 'English') {
        return this.request('POST', '/api/ai/summarize', { text, language });
    }

    async factCheckText(text, language = 'English') {
        return this.request('POST', '/api/ai/fact-check', { text, language });
    }

    async generateQuiz(text, language = 'English') {
        return this.request('POST', '/api/ai/generate-quiz', { text, language });
    }

    async enhanceNote(text, language = 'English') {
        return this.request('POST', '/api/ai/enhance-note', { text, language });
    }

    // Authentication endpoints
    async login(email, password) {
        const response = await this.request('POST', '/api/auth/login', { email, password });
        if (response.token) {
            this.setToken(response.token);
        }
        return response;
    }

    async register(data) {
        return this.request('POST', '/api/auth/register', data);
    }

    async getCurrentUser() {
        return this.request('GET', '/api/auth/me');
    }

    async logout() {
        this.setToken(null);
        return this.request('POST', '/api/auth/logout');
    }
}

// Create and export singleton instance
export const api = new APIClient();
