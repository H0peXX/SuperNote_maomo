// App initialization and core functionality
class App {
    constructor() {
        this.currentPage = 'dashboard';
        this.pages = ['dashboard', 'teams', 'topics', 'notes', 'ai-tools'];
        this.user = null;
        this.isLoading = false;
    }

    async init() {
        // Initialize authentication state
        await this.checkAuth();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize theme
        this.initTheme();
        
        // Hide loading overlay
        this.hideLoading();
        
        // Show app container
        document.getElementById('app').classList.remove('hidden');
    }

    setupEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.currentTarget.dataset.page;
                this.navigateToPage(page);
            });
        });

        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Sidebar toggle (mobile)
        document.getElementById('sidebar-toggle').addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Logout button
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });

        // Handle back/forward browser navigation
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.page) {
                this.navigateToPage(e.state.page, false);
            }
        });
    }

    async navigateToPage(page, addToHistory = true) {
        if (!this.pages.includes(page)) return;

        // Update active navigation link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.dataset.page === page);
        });

        // Update page title
        document.getElementById('page-title').textContent = 
            page.charAt(0).toUpperCase() + page.slice(1);

        // Show loading state
        this.showLoading();

        try {
            // Load page content
            const pageModule = await import(`./pages/${page}.js`);
            if (pageModule.default && typeof pageModule.default.init === 'function') {
                await pageModule.default.init();
            }

            // Update current page
            this.currentPage = page;

            // Add to browser history
            if (addToHistory) {
                window.history.pushState({ page }, '', `#${page}`);
            }

        } catch (error) {
            console.error(`Error loading page ${page}:`, error);
            showToast('Error loading page', 'error');
        }

        // Hide loading state
        this.hideLoading();

        // Close sidebar on mobile after navigation
        if (window.innerWidth < 768) {
            this.toggleSidebar(false);
        }
    }

    async checkAuth() {
        const token = localStorage.getItem('token');
        if (!token) {
            this.showAuthModal();
            return;
        }

        try {
            const response = await api.get('/api/auth/me');
            if (!response.ok) throw new Error('Auth check failed');

            this.user = await response.json();
            this.updateUserInfo();

        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('token');
            this.showAuthModal();
        }
    }

    updateUserInfo() {
        if (!this.user) return;

        const userInitials = document.getElementById('user-initials');
        const userName = document.getElementById('user-name');
        const userEmail = document.getElementById('user-email');

        userInitials.textContent = this.getInitials(this.user.full_name);
        userName.textContent = this.user.full_name;
        userEmail.textContent = this.user.email;
    }

    getInitials(name) {
        return name
            .split(' ')
            .map(part => part[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    }

    showAuthModal() {
        const authModal = document.getElementById('auth-modal');
        authModal.classList.add('show');
    }

    hideAuthModal() {
        const authModal = document.getElementById('auth-modal');
        authModal.classList.remove('show');
    }

    async logout() {
        localStorage.removeItem('token');
        this.user = null;
        window.location.reload();
    }

    toggleTheme() {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        
        const sunIcon = document.querySelector('.sun-icon');
        const moonIcon = document.querySelector('.moon-icon');
        sunIcon.classList.toggle('hidden');
        moonIcon.classList.toggle('hidden');
    }

    initTheme() {
        const theme = localStorage.getItem('theme') || 'light';
        const isDark = theme === 'dark';
        document.documentElement.classList.toggle('dark', isDark);
        
        const sunIcon = document.querySelector('.sun-icon');
        const moonIcon = document.querySelector('.moon-icon');
        sunIcon.classList.toggle('hidden', isDark);
        moonIcon.classList.toggle('hidden', !isDark);
    }

    toggleSidebar(show) {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebar-toggle');
        
        if (typeof show === 'undefined') {
            show = sidebar.classList.contains('-translate-x-full');
        }
        
        sidebar.classList.toggle('-translate-x-full', !show);
        sidebarToggle.setAttribute('aria-expanded', show);
    }

    showLoading() {
        this.isLoading = true;
        document.getElementById('loading-overlay').classList.add('show');
    }

    hideLoading() {
        this.isLoading = false;
        document.getElementById('loading-overlay').classList.remove('show');
    }
}

// Initialize app
const app = new App();
document.addEventListener('DOMContentLoaded', () => app.init());
