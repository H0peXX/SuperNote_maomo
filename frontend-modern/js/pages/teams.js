// Teams page functionality
class TeamsPage {
    constructor() {
        this.teams = [];
        this.currentTeam = null;
    }

    async init() {
        await this.loadTeams();
        this.setupEventListeners();
    }

    async loadTeams() {
        try {
            const response = await api.get('/api/teams/');
            if (response.ok) {
                this.teams = await response.json();
                this.renderTeams();
            }
        } catch (error) {
            showToast('Error loading teams', 'error');
        }
    }

    renderTeams() {
        const container = document.getElementById('teams-list');
        if (!container) return;

        container.innerHTML = this.teams.map(team => `
            <div class="team-card" data-team-id="${team._id}">
                <div class="team-header">
                    <h3 class="team-name">${escapeHtml(team.name)}</h3>
                    <span class="member-count">${team.members.length + 1} members</span>
                </div>
                <p class="team-description">${escapeHtml(team.description || 'No description')}</p>
                <div class="team-members">
                    ${this.renderTeamMembers(team)}
                </div>
                <div class="team-actions">
                    <button class="btn btn-primary join-team-btn" data-team-id="${team._id}">
                        ${this.isTeamMember(team) ? 'Leave Team' : 'Join Team'}
                    </button>
                    ${this.isTeamOwner(team) ? `
                        <button class="btn btn-secondary edit-team-btn" data-team-id="${team._id}">
                            Edit Team
                        </button>
                        <button class="btn btn-danger delete-team-btn" data-team-id="${team._id}">
                            Delete Team
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    renderTeamMembers(team) {
        const maxDisplayMembers = 5;
        const ownerDisplay = `
            <div class="member-avatar owner" title="Owner: ${escapeHtml(team.owner_name)}">
                ${this.getInitials(team.owner_name)}
            </div>
        `;
        
        const membersDisplay = team.members
            .slice(0, maxDisplayMembers)
            .map(member => `
                <div class="member-avatar" title="${escapeHtml(member.user_name)}">
                    ${this.getInitials(member.user_name)}
                </div>
            `).join('');

        const remainingMembers = team.members.length - maxDisplayMembers;
        const remainingDisplay = remainingMembers > 0 ? `
            <div class="member-avatar more" title="${remainingMembers} more members">
                +${remainingMembers}
            </div>
        ` : '';

        return ownerDisplay + membersDisplay + remainingDisplay;
    }

    getInitials(name) {
        return name
            .split(' ')
            .map(part => part[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    }

    isTeamMember(team) {
        const currentUserId = getCurrentUserId();
        return team.members.some(member => member.user_id === currentUserId);
    }

    isTeamOwner(team) {
        const currentUserId = getCurrentUserId();
        return team.owner_id === currentUserId;
    }

    setupEventListeners() {
        document.addEventListener('click', async (e) => {
            if (e.target.matches('.join-team-btn')) {
                const teamId = e.target.dataset.teamId;
                await this.toggleTeamMembership(teamId);
            } else if (e.target.matches('.edit-team-btn')) {
                const teamId = e.target.dataset.teamId;
                this.showEditTeamModal(teamId);
            } else if (e.target.matches('.delete-team-btn')) {
                const teamId = e.target.dataset.teamId;
                await this.deleteTeam(teamId);
            }
        });

        // New team button
        const newTeamBtn = document.getElementById('new-team-btn');
        if (newTeamBtn) {
            newTeamBtn.addEventListener('click', () => this.showNewTeamModal());
        }
    }

    async toggleTeamMembership(teamId) {
        try {
            const team = this.teams.find(t => t._id === teamId);
            if (!team) return;

            if (this.isTeamMember(team)) {
                await api.delete(`/api/teams/${teamId}/members/${getCurrentUserId()}`);
                showToast('Left team successfully', 'success');
            } else {
                await api.post(`/api/teams/${teamId}/members/${getCurrentUserId()}`);
                showToast('Joined team successfully', 'success');
            }

            await this.loadTeams();
        } catch (error) {
            showToast('Error updating team membership', 'error');
        }
    }

    async showEditTeamModal(teamId) {
        const team = this.teams.find(t => t._id === teamId);
        if (!team) return;

        showModal({
            title: 'Edit Team',
            content: `
                <form id="edit-team-form">
                    <div class="form-group">
                        <label for="team-name">Team Name</label>
                        <input type="text" id="team-name" value="${escapeHtml(team.name)}" required>
                    </div>
                    <div class="form-group">
                        <label for="team-description">Description</label>
                        <textarea id="team-description">${escapeHtml(team.description || '')}</textarea>
                    </div>
                </form>
            `,
            onConfirm: async () => {
                const name = document.getElementById('team-name').value;
                const description = document.getElementById('team-description').value;
                
                try {
                    await api.put(`/api/teams/${teamId}`, {
                        name,
                        description
                    });
                    showToast('Team updated successfully', 'success');
                    await this.loadTeams();
                } catch (error) {
                    showToast('Error updating team', 'error');
                }
            }
        });
    }

    async deleteTeam(teamId) {
        if (!confirm('Are you sure you want to delete this team? This action cannot be undone.')) {
            return;
        }

        try {
            await api.delete(`/api/teams/${teamId}`);
            showToast('Team deleted successfully', 'success');
            await this.loadTeams();
        } catch (error) {
            showToast('Error deleting team', 'error');
        }
    }

    showNewTeamModal() {
        showModal({
            title: 'Create New Team',
            content: `
                <form id="new-team-form">
                    <div class="form-group">
                        <label for="team-name">Team Name</label>
                        <input type="text" id="team-name" required>
                    </div>
                    <div class="form-group">
                        <label for="team-description">Description</label>
                        <textarea id="team-description"></textarea>
                    </div>
                </form>
            `,
            onConfirm: async () => {
                const name = document.getElementById('team-name').value;
                const description = document.getElementById('team-description').value;
                
                try {
                    await api.post('/api/teams/', {
                        name,
                        description
                    });
                    showToast('Team created successfully', 'success');
                    await this.loadTeams();
                } catch (error) {
                    showToast('Error creating team', 'error');
                }
            }
        });
    }
}

// Initialize Teams page
const teamsPage = new TeamsPage();
window.addEventListener('load', () => teamsPage.init());
