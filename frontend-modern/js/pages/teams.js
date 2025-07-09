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
            title: 'Team Settings',
            content: `
                <div class="space-y-6">
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

                    <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
                        <h3 class="text-lg font-medium mb-4">Team Members</h3>
                        <div class="space-y-3" id="team-members-list">
                            ${this.renderTeamMembersList(team)}
                        </div>
                        <button id="invite-member" class="btn btn-secondary mt-4">
                            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path d="M12 4v16m8-8H4"></path>
                            </svg>
                            Invite Member
                        </button>
                    </div>

                    ${this.isTeamOwner(team) ? `
                        <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
                            <h3 class="text-lg font-medium text-red-600 dark:text-red-400 mb-4">Danger Zone</h3>
                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                                Once you delete a team, there is no going back. Please be certain.
                            </p>
                            <button id="delete-team" class="btn btn-danger">
                                Delete Team
                            </button>
                        </div>
                    ` : ''}
                </div>
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
            },
            afterRender: () => {
                // Setup member management
                const inviteBtn = document.getElementById('invite-member');
                if (inviteBtn) {
                    inviteBtn.addEventListener('click', () => {
                        this.showInviteMemberModal(teamId);
                    });
                }

                // Setup role changes
                const roleSelects = document.querySelectorAll('.member-role-select');
                roleSelects.forEach(select => {
                    select.addEventListener('change', async (e) => {
                        const memberId = e.target.dataset.memberId;
                        const newRole = e.target.value;
                        await this.updateMemberRole(teamId, memberId, newRole);
                    });
                });

                // Setup member removal
                const removeButtons = document.querySelectorAll('.remove-member-btn');
                removeButtons.forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const memberId = e.target.dataset.memberId;
                        await this.removeMember(teamId, memberId);
                    });
                });

                // Setup team deletion
                const deleteBtn = document.getElementById('delete-team');
                if (deleteBtn) {
                    deleteBtn.addEventListener('click', async () => {
                        if (await this.confirmDeleteTeam(teamId)) {
                            await this.deleteTeam(teamId);
                        }
                    });
                }
            }
        });
    },

    renderTeamMembersList(team) {
        const currentUserId = getCurrentUserId();
        const isOwner = this.isTeamOwner(team);

        return team.members.map(member => `
            <div class="flex items-center justify-between py-2">
                <div class="flex items-center gap-3">
                    <div class="member-avatar" title="${escapeHtml(member.user_name)}">
                        ${this.getInitials(member.user_name)}
                    </div>
                    <div>
                        <div class="font-medium">${escapeHtml(member.user_name)}</div>
                        <div class="text-sm text-gray-500">${member.user_id}</div>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    ${isOwner ? `
                        <select class="member-role-select form-select" data-member-id="${member.user_id}">
                            <option value="member" ${member.role === 'member' ? 'selected' : ''}>Member</option>
                            <option value="admin" ${member.role === 'admin' ? 'selected' : ''}>Admin</option>
                        </select>
                        <button class="btn btn-danger btn-sm remove-member-btn" data-member-id="${member.user_id}">
                            Remove
                        </button>
                    ` : `
                        <span class="px-2 py-1 text-sm rounded-full ${member.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'}">
                            ${member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                        </span>
                    `}
                </div>
            </div>
        `).join('');
    },

    async showInviteMemberModal(teamId) {
        showModal({
            title: 'Invite Team Member',
            content: `
                <form id="invite-member-form">
                    <div class="form-group">
                        <label for="member-email">Email Address</label>
                        <input type="email" id="member-email" required>
                    </div>
                    <div class="form-group">
                        <label for="member-role">Role</label>
                        <select id="member-role">
                            <option value="member">Member</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>
                </form>
            `,
            onConfirm: async () => {
                const email = document.getElementById('member-email').value;
                const role = document.getElementById('member-role').value;

                try {
                    await api.post(`/api/teams/${teamId}/invite`, {
                        email,
                        role
                    });
                    showToast('Invitation sent successfully', 'success');
                    await this.loadTeams();
                } catch (error) {
                    showToast('Error sending invitation', 'error');
                }
            }
        });
    },

    async updateMemberRole(teamId, memberId, role) {
        try {
            await api.put(`/api/teams/${teamId}/members/${memberId}/role`, { role });
            showToast('Member role updated', 'success');
            await this.loadTeams();
        } catch (error) {
            showToast('Error updating member role', 'error');
        }
    },

    async removeMember(teamId, memberId) {
        if (!confirm('Are you sure you want to remove this member?')) return;

        try {
            await api.delete(`/api/teams/${teamId}/members/${memberId}`);
            showToast('Member removed successfully', 'success');
            await this.loadTeams();
        } catch (error) {
            showToast('Error removing member', 'error');
        }
    },

    async confirmDeleteTeam(teamId) {
        return new Promise(resolve => {
            showModal({
                title: 'Delete Team',
                content: `
                    <div class="text-center">
                        <svg class="w-16 h-16 mx-auto text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">
                            Are you absolutely sure?
                        </h3>
                        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                            This action cannot be undone. This will permanently delete the team
                            and remove all data associated with it.
                        </p>
                    </div>
                    <div class="mt-4">
                        <label class="inline-flex items-center">
                            <input type="checkbox" id="confirm-delete" class="form-checkbox">
                            <span class="ml-2 text-sm text-gray-600 dark:text-gray-300">
                                I understand that this action is irreversible
                            </span>
                        </label>
                    </div>
                `,
                onConfirm: () => {
                    const confirmed = document.getElementById('confirm-delete').checked;
                    resolve(confirmed);
                },
                onCancel: () => resolve(false)
            });
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
