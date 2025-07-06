// Dashboard page module
const DashboardPage = {
    async init() {
        this.renderDashboard();
    },

    async renderDashboard() {
        const pageContent = document.getElementById('page-content');
        
        try {
            const [notesResponse, teamsResponse] = await Promise.all([
                api.get('/api/notes/recent'),
                api.get('/api/teams/')
            ]);

            const recentNotes = await notesResponse.json();
            const teams = await teamsResponse.json();

            pageContent.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    ${this.renderStatsCards(recentNotes, teams)}
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Recent Notes</h2>
                            <a href="#notes" class="btn btn-sm btn-secondary">View All</a>
                        </div>
                        <div class="space-y-4">
                            ${this.renderRecentNotes(recentNotes)}
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Your Teams</h2>
                            <a href="#teams" class="btn btn-sm btn-secondary">View All</a>
                        </div>
                        <div class="space-y-4">
                            ${this.renderTeamsList(teams)}
                        </div>
                    </div>
                </div>
            `;

        } catch (error) {
            console.error('Error loading dashboard:', error);
            showToast('Error loading dashboard data', 'error');
        }
    },

    renderStatsCards(notes, teams) {
        const stats = [
            {
                label: 'Total Notes',
                value: notes.length,
                change: '+12% from last month',
                icon: '<path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />'
            },
            {
                label: 'Active Teams',
                value: teams.length,
                change: '+3 new this month',
                icon: '<path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />'
            },
            {
                label: 'Fact Checks',
                value: notes.reduce((acc, note) => acc + note.fact_checks.length, 0),
                change: '+24% accuracy rate',
                icon: '<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />'
            },
            {
                label: 'AI Enhancements',
                value: notes.reduce((acc, note) => acc + note.versions.length, 0),
                change: '+8 this week',
                icon: '<path d="M13 10V3L4 14h7v7l9-11h-7z" />'
            }
        ];

        return stats.map(stat => `
            <div class="stats-card">
                <div class="stats-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        ${stat.icon}
                    </svg>
                </div>
                <div class="stats-number">${stat.value}</div>
                <div class="stats-label">${stat.label}</div>
                <div class="stats-change">${stat.change}</div>
            </div>
        `).join('');
    },

    renderRecentNotes(notes) {
        if (!notes.length) {
            return `
                <div class="empty-state">
                    <p>No notes yet. Start creating!</p>
                </div>
            `;
        }

        return notes.map(note => `
            <div class="card" onclick="window.location.href='#notes/${note._id}'">
                <h3 class="card-title">${escapeHtml(note.title)}</h3>
                <p class="card-subtitle">Last updated ${formatDate(note.updated_at)}</p>
                <div class="card-footer">
                    <div class="flex items-center gap-2 text-sm text-gray-500">
                        <span>${note.comments.length} comments</span>
                        <span>•</span>
                        <span>${note.fact_checks.length} fact checks</span>
                    </div>
                </div>
            </div>
        `).join('');
    },

    renderTeamsList(teams) {
        if (!teams.length) {
            return `
                <div class="empty-state">
                    <p>No teams yet. Create or join one!</p>
                </div>
            `;
        }

        return teams.map(team => `
            <div class="card" onclick="window.location.href='#teams/${team._id}'">
                <h3 class="card-title">${escapeHtml(team.name)}</h3>
                <p class="card-subtitle">${team.members.length + 1} members</p>
                <div class="card-footer">
                    <div class="flex items-center gap-2">
                        ${this.renderTeamMembers(team)}
                    </div>
                </div>
            </div>
        `).join('');
    },

    renderTeamMembers(team) {
        const maxDisplay = 3;
        const members = team.members.slice(0, maxDisplay);
        const remaining = team.members.length - maxDisplay;

        const memberAvatars = members.map(member => `
            <div class="member-avatar" title="${escapeHtml(member.user_name)}">
                ${this.getInitials(member.user_name)}
            </div>
        `).join('');

        const remainingDisplay = remaining > 0 ? `
            <div class="member-avatar more" title="${remaining} more members">
                +${remaining}
            </div>
        ` : '';

        return memberAvatars + remainingDisplay;
    },

    getInitials(name) {
        return name
            .split(' ')
            .map(part => part[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    }
};

export default DashboardPage;
